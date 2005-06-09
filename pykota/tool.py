# PyKota
# -*- coding: ISO-8859-15 -*-

# PyKota - Print Quotas for CUPS and LPRng
#
# (c) 2003-2004 Jerome Alet <alet@librelogiciel.com>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# $Id$
#
#

import sys
import os
import pwd
import fnmatch
import getopt
import smtplib
import gettext
import locale
import signal
import socket
import tempfile
import md5
import ConfigParser
import popen2

from mx import DateTime

from pykota import version, config, storage, logger, accounter, pdlanalyzer

def N_(message) :
    """Fake translation marker for translatable strings extraction."""
    return message

class PyKotaToolError(Exception):
    """An exception for PyKota config related stuff."""
    def __init__(self, message = ""):
        self.message = message
        Exception.__init__(self, message)
    def __repr__(self):
        return self.message
    __str__ = __repr__
    
def crashed(message="Bug in PyKota") :    
    """Minimal crash method."""
    import traceback
    lines = []
    for line in traceback.format_exception(*sys.exc_info()) :
        lines.extend([l for l in line.split("\n") if l])
    msg = "ERROR: ".join(["%s\n" % l for l in (["ERROR: PyKota v%s" % version.__version__, message] + lines)])
    sys.stderr.write(msg)
    sys.stderr.flush()
    return msg

class Tool :
    """Base class for tools with no database access."""
    def __init__(self, lang="", charset=None, doc="PyKota v%s (c) %s %s" % (version.__version__, version.__copyright__, version.__author__)) :
        """Initializes the command line tool."""
        # did we drop priviledges ?
        self.privdropped = 0
        
        # locale stuff
        self.defaultToCLocale = 0
        try :
            locale.setlocale(locale.LC_ALL, lang)
        except (locale.Error, IOError) :
            locale.setlocale(locale.LC_ALL, "C")
            self.defaultToCLocale = 1
        try :
            gettext.install("pykota")
        except :
            gettext.NullTranslations().install()
            
        # We can force the charset.    
        # The CHARSET environment variable is set by CUPS when printing.
        # Else we use the current locale's one.
        # If nothing is set, we use ISO-8859-15 widely used in western Europe.
        localecharset = None
        try :
            try :
                localecharset = locale.nl_langinfo(locale.CODESET)
            except AttributeError :    
                try :
                    localecharset = locale.getpreferredencoding()
                except AttributeError :    
                    try :
                        localecharset = locale.getlocale()[1]
                        localecharset = localecharset or locale.getdefaultlocale()[1]
                    except ValueError :    
                        pass        # Unknown locale, strange...
        except locale.Error :            
            pass
        self.charset = charset or os.environ.get("CHARSET") or localecharset or "ISO-8859-15"
    
        # pykota specific stuff
        self.documentation = doc
        
    def deferredInit(self) :        
        """Deferred initialization."""
        # try to find the configuration files in user's 'pykota' home directory.
        try :
            self.pykotauser = pwd.getpwnam("pykota")
        except KeyError :    
            self.pykotauser = None
            confdir = "/etc/pykota"
            missingUser = 1
        else :    
            confdir = self.pykotauser[5]
            missingUser = 0
            
        self.config = config.PyKotaConfig(confdir)
        self.debug = self.config.getDebug()
        self.smtpserver = self.config.getSMTPServer()
        self.maildomain = self.config.getMailDomain()
        self.logger = logger.openLogger(self.config.getLoggingBackend())
            
        # now drop priviledge if possible
        self.dropPriv()    
        
        # We NEED this here, even when not in an accounting filter/backend    
        self.softwareJobSize = 0
        self.softwareJobPrice = 0.0
        
        if self.defaultToCLocale :
            self.printInfo("Incorrect locale settings. PyKota falls back to the 'C' locale.", "warn")
        if missingUser :     
            self.printInfo("The 'pykota' system account is missing. Configuration files were searched in /etc/pykota instead.", "warn")
        
        self.logdebug("Charset in use : %s" % self.charset)
        arguments = " ".join(['"%s"' % arg for arg in sys.argv])
        self.logdebug("Command line arguments : %s" % arguments)
        
    def dropPriv(self) :    
        """Drops priviledges."""
        uid = os.geteuid()
        if uid :
            try :
                username = pwd.getpwuid(uid)[0]
            except (KeyError, IndexError), msg :    
                self.printInfo(_("Strange problem with uid(%s) : %s") % (uid, msg), "warn")
            else :
                self.logdebug(_("Running as user '%s'.") % username)
        else :
            if self.pykotauser is None :
                self.logdebug(_("No user named 'pykota'. Not dropping priviledges."))
            else :    
                try :
                    os.setegid(self.pykotauser[3])
                    os.seteuid(self.pykotauser[2])
                except OSError, msg :    
                    self.printInfo(_("Impossible to drop priviledges : %s") % msg, "warn")
                else :    
                    self.logdebug(_("Priviledges dropped. Now running as user 'pykota'."))
                    self.privdropped = 1
            
    def regainPriv(self) :    
        """Drops priviledges."""
        if self.privdropped :
            try :
                os.seteuid(0)
                os.setegid(0)
            except OSError, msg :    
                self.printInfo(_("Impossible to regain priviledges : %s") % msg, "warn")
            else :    
                self.logdebug(_("Regained priviledges. Now running as root."))
                self.privdropped = 0
        
    def getCharset(self) :    
        """Returns the charset in use."""
        return self.charset
        
    def logdebug(self, message) :    
        """Logs something to debug output if debug is enabled."""
        if self.debug :
            self.logger.log_message(message, "debug")
            
    def printInfo(self, message, level="info") :        
        """Sends a message to standard error."""
        sys.stderr.write("%s: %s\n" % (level.upper(), message))
        sys.stderr.flush()
        
    def matchString(self, s, patterns) :
        """Returns 1 if the string s matches one of the patterns, else 0."""
        for pattern in patterns :
            if fnmatch.fnmatchcase(s, pattern) :
                return 1
        return 0
        
    def display_version_and_quit(self) :
        """Displays version number, then exists successfully."""
        try :
            self.clean()
        except AttributeError :    
            pass
        print version.__version__
        sys.exit(0)
    
    def display_usage_and_quit(self) :
        """Displays command line usage, then exists successfully."""
        try :
            self.clean()
        except AttributeError :    
            pass
        print _(self.documentation) % (version.__version__, version.__copyright__, version.__author__, version.__author__)
        sys.exit(0)
        
    def crashed(self, message="Bug in PyKota") :    
        """Outputs a crash message, and optionally sends it to software author."""
        msg = crashed(message)
        fullmessage = "========== Traceback :\n\n%s\n\n========== sys.argv :\n\n%s\n\n========== Environment :\n\n%s\n" % \
                        (msg, \
                         "\n".join(["    %s" % repr(a) for a in sys.argv]), \
                         "\n".join(["    %s=%s" % (k, v) for (k, v) in os.environ.items()]))
        try :
            crashrecipient = self.config.getCrashRecipient()
            if crashrecipient :
                admin = self.config.getAdminMail("global") # Nice trick, isn't it ?
                server = smtplib.SMTP(self.smtpserver)
                server.sendmail(admin, [admin, crashrecipient], \
                                       "From: %s\nTo: %s\nCc: %s\nSubject: PyKota v%s crash traceback !\n\n%s" % \
                                       (admin, crashrecipient, admin, version.__version__, fullmessage))
                server.quit()
        except :
            pass
        return fullmessage    
        
    def parseCommandline(self, argv, short, long, allownothing=0) :
        """Parses the command line, controlling options."""
        # split options in two lists: those which need an argument, those which don't need any
        withoutarg = []
        witharg = []
        lgs = len(short)
        i = 0
        while i < lgs :
            ii = i + 1
            if (ii < lgs) and (short[ii] == ':') :
                # needs an argument
                witharg.append(short[i])
                ii = ii + 1 # skip the ':'
            else :
                # doesn't need an argument
                withoutarg.append(short[i])
            i = ii
                
        for option in long :
            if option[-1] == '=' :
                # needs an argument
                witharg.append(option[:-1])
            else :
                # doesn't need an argument
                withoutarg.append(option)
        
        # we begin with all possible options unset
        parsed = {}
        for option in withoutarg + witharg :
            parsed[option] = None
        
        # then we parse the command line
        args = []       # to not break if something unexpected happened
        try :
            options, args = getopt.getopt(argv, short, long)
            if options :
                for (o, v) in options :
                    # we skip the '-' chars
                    lgo = len(o)
                    i = 0
                    while (i < lgo) and (o[i] == '-') :
                        i = i + 1
                    o = o[i:]
                    if o in witharg :
                        # needs an argument : set it
                        parsed[o] = v
                    elif o in withoutarg :
                        # doesn't need an argument : boolean
                        parsed[o] = 1
                    else :
                        # should never occur
                        raise PyKotaToolError, "Unexpected problem when parsing command line"
            elif (not args) and (not allownothing) and sys.stdin.isatty() : # no option and no argument, we display help if we are a tty
                self.display_usage_and_quit()
        except getopt.error, msg :
            self.printInfo(msg)
            self.display_usage_and_quit()
        return (parsed, args)
    
class PyKotaTool(Tool) :    
    """Base class for all PyKota command line tools."""
    def __init__(self, lang="", charset=None, doc="PyKota %s (c) 2003-2004 %s" % (version.__version__, version.__author__)) :
        """Initializes the command line tool and opens the database."""
        Tool.__init__(self, lang, charset, doc)
        
    def deferredInit(self) :    
        """Deferred initialization."""
        Tool.deferredInit(self)
        self.storage = storage.openConnection(self)
        if self.config.isAdmin : # TODO : We don't know this before, fix this !
            self.logdebug("Beware : running as a PyKota administrator !")
        else :    
            self.logdebug("Don't Panic : running as a mere mortal !")
        
    def clean(self) :    
        """Ensures that the database is closed."""
        try :
            self.storage.close()
        except (TypeError, NameError, AttributeError) :    
            pass
            
    def isValidName(self, name) :
        """Checks if a user or printer name is valid."""
        invalidchars = "/@?*,;&|"
        for c in list(invalidchars) :
            if c in name :
                return 0
        return 1        
        
    def sendMessage(self, adminmail, touser, fullmessage) :
        """Sends an email message containing headers to some user."""
        if "@" not in touser :
            touser = "%s@%s" % (touser, self.maildomain or self.smtpserver)
        try :    
            server = smtplib.SMTP(self.smtpserver)
        except socket.error, msg :    
            self.printInfo(_("Impossible to connect to SMTP server : %s") % msg, "error")
        else :
            try :
                server.sendmail(adminmail, [touser], "From: %s\nTo: %s\n%s" % (adminmail, touser, fullmessage))
            except smtplib.SMTPException, answer :    
                for (k, v) in answer.recipients.items() :
                    self.printInfo(_("Impossible to send mail to %s, error %s : %s") % (k, v[0], v[1]), "error")
            server.quit()
        
    def sendMessageToUser(self, admin, adminmail, user, subject, message) :
        """Sends an email message to a user."""
        message += _("\n\nPlease contact your system administrator :\n\n\t%s - <%s>\n") % (admin, adminmail)
        self.sendMessage(adminmail, user.Email or user.Name, "Subject: %s\n\n%s" % (subject, message))
        
    def sendMessageToAdmin(self, adminmail, subject, message) :
        """Sends an email message to the Print Quota administrator."""
        self.sendMessage(adminmail, adminmail, "Subject: %s\n\n%s" % (subject, message))
        
    def _checkUserPQuota(self, userpquota) :            
        """Checks the user quota on a printer and deny or accept the job."""
        # then we check the user's own quota
        # if we get there we are sure that policy is not EXTERNAL
        user = userpquota.User
        printer = userpquota.Printer
        enforcement = self.config.getPrinterEnforcement(printer.Name)
        self.logdebug("Checking user %s's quota on printer %s" % (user.Name, printer.Name))
        (policy, dummy) = self.config.getPrinterPolicy(userpquota.Printer.Name)
        if not userpquota.Exists :
            # Unknown userquota 
            if policy == "ALLOW" :
                action = "POLICY_ALLOW"
            else :    
                action = "POLICY_DENY"
            self.printInfo(_("Unable to match user %s on printer %s, applying default policy (%s)") % (user.Name, printer.Name, action))
        else :    
            pagecounter = int(userpquota.PageCounter or 0)
            if enforcement == "STRICT" :
                pagecounter += self.softwareJobSize
            if userpquota.SoftLimit is not None :
                softlimit = int(userpquota.SoftLimit)
                if pagecounter < softlimit :
                    action = "ALLOW"
                else :    
                    if userpquota.HardLimit is None :
                        # only a soft limit, this is equivalent to having only a hard limit
                        action = "DENY"
                    else :    
                        hardlimit = int(userpquota.HardLimit)
                        if softlimit <= pagecounter < hardlimit :    
                            now = DateTime.now()
                            if userpquota.DateLimit is not None :
                                datelimit = DateTime.ISO.ParseDateTime(userpquota.DateLimit)
                            else :
                                datelimit = now + self.config.getGraceDelay(printer.Name)
                                userpquota.setDateLimit(datelimit)
                            if now < datelimit :
                                action = "WARN"
                            else :    
                                action = "DENY"
                        else :         
                            action = "DENY"
            else :        
                if userpquota.HardLimit is not None :
                    # no soft limit, only a hard one.
                    hardlimit = int(userpquota.HardLimit)
                    if pagecounter < hardlimit :
                        action = "ALLOW"
                    else :      
                        action = "DENY"
                else :
                    # Both are unset, no quota, i.e. accounting only
                    action = "ALLOW"
        return action
    
    def checkGroupPQuota(self, grouppquota) :    
        """Checks the group quota on a printer and deny or accept the job."""
        group = grouppquota.Group
        printer = grouppquota.Printer
        enforcement = self.config.getPrinterEnforcement(printer.Name)
        self.logdebug("Checking group %s's quota on printer %s" % (group.Name, printer.Name))
        if group.LimitBy and (group.LimitBy.lower() == "balance") : 
            val = group.AccountBalance or 0.0
            if enforcement == "STRICT" : 
                val -= self.softwareJobPrice # use precomputed size.
            if val <= 0.0 :
                action = "DENY"
            elif val <= self.config.getPoorMan() :    
                action = "WARN"
            else :    
                action = "ALLOW"
            if (enforcement == "STRICT") and (val == 0.0) :
                action = "WARN" # we can still print until account is 0
        else :
            val = grouppquota.PageCounter or 0
            if enforcement == "STRICT" :
                val += self.softwareJobSize
            if grouppquota.SoftLimit is not None :
                softlimit = int(grouppquota.SoftLimit)
                if val < softlimit :
                    action = "ALLOW"
                else :    
                    if grouppquota.HardLimit is None :
                        # only a soft limit, this is equivalent to having only a hard limit
                        action = "DENY"
                    else :    
                        hardlimit = int(grouppquota.HardLimit)
                        if softlimit <= val < hardlimit :    
                            now = DateTime.now()
                            if grouppquota.DateLimit is not None :
                                datelimit = DateTime.ISO.ParseDateTime(grouppquota.DateLimit)
                            else :
                                datelimit = now + self.config.getGraceDelay(printer.Name)
                                grouppquota.setDateLimit(datelimit)
                            if now < datelimit :
                                action = "WARN"
                            else :    
                                action = "DENY"
                        else :         
                            action = "DENY"
            else :        
                if grouppquota.HardLimit is not None :
                    # no soft limit, only a hard one.
                    hardlimit = int(grouppquota.HardLimit)
                    if val < hardlimit :
                        action = "ALLOW"
                    else :      
                        action = "DENY"
                else :
                    # Both are unset, no quota, i.e. accounting only
                    action = "ALLOW"
        return action
    
    def checkUserPQuota(self, userpquota) :
        """Checks the user quota on a printer and all its parents and deny or accept the job."""
        user = userpquota.User
        printer = userpquota.Printer
        
        # indicates that a warning needs to be sent
        warned = 0                
        
        # first we check any group the user is a member of
        for group in self.storage.getUserGroups(user) :
            grouppquota = self.storage.getGroupPQuota(group, printer)
            # for the printer and all its parents
            for gpquota in [ grouppquota ] + grouppquota.ParentPrintersGroupPQuota :
                if gpquota.Exists :
                    action = self.checkGroupPQuota(gpquota)
                    if action == "DENY" :
                        return action
                    elif action == "WARN" :    
                        warned = 1
                        
        # Then we check the user's account balance
        # if we get there we are sure that policy is not EXTERNAL
        (policy, dummy) = self.config.getPrinterPolicy(printer.Name)
        if user.LimitBy and (user.LimitBy.lower() == "balance") : 
            self.logdebug("Checking account balance for user %s" % user.Name)
            if user.AccountBalance is None :
                if policy == "ALLOW" :
                    action = "POLICY_ALLOW"
                else :    
                    action = "POLICY_DENY"
                self.printInfo(_("Unable to find user %s's account balance, applying default policy (%s) for printer %s") % (user.Name, action, printer.Name))
                return action        
            else :    
                if user.OverCharge == 0.0 :
                    self.printInfo(_("User %s will not be charged for printing.") % user.Name)
                    action = "ALLOW"
                else :
                    val = float(user.AccountBalance or 0.0)
                    enforcement = self.config.getPrinterEnforcement(printer.Name)
                    if enforcement == "STRICT" : 
                        val -= self.softwareJobPrice # use precomputed size.
                    if val <= 0.0 :
                        action = "DENY"
                    elif val <= self.config.getPoorMan() :    
                        action = "WARN"
                    else :
                        action = "ALLOW"
                    if (enforcement == "STRICT") and (val == 0.0) :
                        action = "WARN" # we can still print until account is 0
                return action    
        else :
            # Then check the user quota on current printer and all its parents.                
            policyallowed = 0
            for upquota in [ userpquota ] + userpquota.ParentPrintersUserPQuota :               
                action = self._checkUserPQuota(upquota)
                if action in ("DENY", "POLICY_DENY") :
                    return action
                elif action == "WARN" :    
                    warned = 1
                elif action == "POLICY_ALLOW" :    
                    policyallowed = 1
            if warned :        
                return "WARN"
            elif policyallowed :    
                return "POLICY_ALLOW" 
            else :    
                return "ALLOW"
                
    def externalMailTo(self, cmd, action, user, printer, message) :
        """Warns the user with an external command."""
        username = user.Name
        printername = printer.Name
        email = user.Email or user.Name
        if "@" not in email :
            email = "%s@%s" % (email, self.maildomain or self.smtpserver)
        os.system(cmd % locals())
    
    def formatCommandLine(self, cmd, user, printer) :
        """Executes an external command."""
        username = user.Name
        printername = printer.Name
        return cmd % locals()
        
    def warnGroupPQuota(self, grouppquota) :
        """Checks a group quota and send messages if quota is exceeded on current printer."""
        group = grouppquota.Group
        printer = grouppquota.Printer
        admin = self.config.getAdmin(printer.Name)
        adminmail = self.config.getAdminMail(printer.Name)
        (mailto, arguments) = self.config.getMailTo(printer.Name)
        action = self.checkGroupPQuota(grouppquota)
        if action.startswith("POLICY_") :
            action = action[7:]
        if action == "DENY" :
            adminmessage = _("Print Quota exceeded for group %s on printer %s") % (group.Name, printer.Name)
            self.printInfo(adminmessage)
            if mailto in [ "BOTH", "ADMIN" ] :
                self.sendMessageToAdmin(adminmail, _("Print Quota"), adminmessage)
            if mailto in [ "BOTH", "USER", "EXTERNAL" ] :
                for user in self.storage.getGroupMembers(group) :
                    if mailto != "EXTERNAL" :
                        self.sendMessageToUser(admin, adminmail, user, _("Print Quota Exceeded"), self.config.getHardWarn(printer.Name))
                    else :    
                        self.externalMailTo(arguments, action, user, printer, self.config.getHardWarn(printer.Name))
        elif action == "WARN" :    
            adminmessage = _("Print Quota low for group %s on printer %s") % (group.Name, printer.Name)
            self.printInfo(adminmessage)
            if mailto in [ "BOTH", "ADMIN" ] :
                self.sendMessageToAdmin(adminmail, _("Print Quota"), adminmessage)
            if group.LimitBy and (group.LimitBy.lower() == "balance") : 
                message = self.config.getPoorWarn()
            else :     
                message = self.config.getSoftWarn(printer.Name)
            if mailto in [ "BOTH", "USER", "EXTERNAL" ] :
                for user in self.storage.getGroupMembers(group) :
                    if mailto != "EXTERNAL" :
                        self.sendMessageToUser(admin, adminmail, user, _("Print Quota Exceeded"), message)
                    else :    
                        self.externalMailTo(arguments, action, user, printer, message)
        return action        
        
    def warnUserPQuota(self, userpquota) :
        """Checks a user quota and send him a message if quota is exceeded on current printer."""
        user = userpquota.User
        printer = userpquota.Printer
        admin = self.config.getAdmin(printer.Name)
        adminmail = self.config.getAdminMail(printer.Name)
        (mailto, arguments) = self.config.getMailTo(printer.Name)
        action = self.checkUserPQuota(userpquota)
        if action.startswith("POLICY_") :
            action = action[7:]
            
        if action == "DENY" :
            adminmessage = _("Print Quota exceeded for user %s on printer %s") % (user.Name, printer.Name)
            self.printInfo(adminmessage)
            if mailto in [ "BOTH", "USER", "EXTERNAL" ] :
                message = self.config.getHardWarn(printer.Name)
                if mailto != "EXTERNAL" :
                    self.sendMessageToUser(admin, adminmail, user, _("Print Quota Exceeded"), message)
                else :    
                    self.externalMailTo(arguments, action, user, printer, message)
            if mailto in [ "BOTH", "ADMIN" ] :
                self.sendMessageToAdmin(adminmail, _("Print Quota"), adminmessage)
        elif action == "WARN" :    
            adminmessage = _("Print Quota low for user %s on printer %s") % (user.Name, printer.Name)
            self.printInfo(adminmessage)
            if mailto in [ "BOTH", "USER", "EXTERNAL" ] :
                if user.LimitBy and (user.LimitBy.lower() == "balance") : 
                    message = self.config.getPoorWarn()
                else :     
                    message = self.config.getSoftWarn(printer.Name)
                if mailto != "EXTERNAL" :    
                    self.sendMessageToUser(admin, adminmail, user, _("Print Quota Low"), message)
                else :    
                    self.externalMailTo(arguments, action, user, printer, message)
            if mailto in [ "BOTH", "ADMIN" ] :
                self.sendMessageToAdmin(adminmail, _("Print Quota"), adminmessage)
        return action        
        
class PyKotaFilterOrBackend(PyKotaTool) :    
    """Class for the PyKota filter or backend."""
    def __init__(self) :
        """Initialize local datas from current environment."""
        # We begin with ignoring signals, we may de-ignore them later on.
        self.gotSigTerm = 0
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        # signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        signal.signal(signal.SIGPIPE, signal.SIG_IGN)
        
        PyKotaTool.__init__(self)
        (self.printingsystem, \
         self.printerhostname, \
         self.printername, \
         self.username, \
         self.jobid, \
         self.inputfile, \
         self.copies, \
         self.title, \
         self.options, \
         self.originalbackend) = self.extractInfoFromCupsOrLprng()
         
    def deferredInit(self) :
        """Deferred initialization."""
        PyKotaTool.deferredInit(self)
        
        arguments = " ".join(['"%s"' % arg for arg in sys.argv])
        self.logdebug(_("Printing system %s, args=%s") % (str(self.printingsystem), arguments))
        
        self.username = self.username or pwd.getpwuid(os.geteuid())[0] # use CUPS' user when printing test page from CUPS web interface, otherwise username is empty
        
        # do we want to strip out the Samba/Winbind domain name ?
        separator = self.config.getWinbindSeparator()
        if separator is not None :
            self.username = self.username.split(separator)[-1]
            
        # do we want to lowercase usernames ?    
        if self.config.getUserNameToLower() :
            self.username = self.username.lower()
            
        self.preserveinputfile = self.inputfile 
        try :
            self.accounter = accounter.openAccounter(self)
        except (config.PyKotaConfigError, accounter.PyKotaAccounterError), msg :    
            self.crashed(msg)
            raise
        self.exportJobInfo()
        self.jobdatastream = self.openJobDataStream()
        self.checksum = self.computeChecksum()
        self.softwareJobSize = self.precomputeJobSize()
        os.environ["PYKOTAPRECOMPUTEDJOBSIZE"] = str(self.softwareJobSize)
        os.environ["PYKOTAJOBSIZEBYTES"] = str(self.jobSizeBytes)
        self.logdebug("Job size is %s bytes on %s pages." % (self.jobSizeBytes, self.softwareJobSize))
        self.logdebug("Capturing SIGTERM events.")
        signal.signal(signal.SIGTERM, self.sigterm_handler)
        
    def sendBackChannelData(self, message, level="info") :    
        """Sends an informational message to CUPS via back channel stream (stderr)."""
        sys.stderr.write("%s: PyKota (PID %s) : %s\n" % (level.upper(), os.getpid(), message.strip()))
        sys.stderr.flush()
        
    def computeChecksum(self) :    
        """Computes the MD5 checksum of the job's datas, to be able to detect and forbid duplicate jobs."""
        self.logdebug("Computing MD5 checksum for job %s" % self.jobid)
        MEGABYTE = 1024*1024
        checksum = md5.new()
        while 1 :
            data = self.jobdatastream.read(MEGABYTE) 
            if not data :
                break
            checksum.update(data)    
        self.jobdatastream.seek(0)
        digest = checksum.hexdigest()
        self.logdebug("MD5 checksum for job %s is %s" % (self.jobid, digest))
        os.environ["PYKOTAMD5SUM"] = digest
        return digest
        
    def openJobDataStream(self) :    
        """Opens the file which contains the job's datas."""
        if self.preserveinputfile is None :
            # Job comes from sys.stdin, but this is not
            # seekable and complexifies our task, so create
            # a temporary file and use it instead
            self.logdebug("Duplicating data stream from stdin to temporary file")
            dummy = 0
            MEGABYTE = 1024*1024
            self.jobSizeBytes = 0
            infile = tempfile.TemporaryFile()
            while 1 :
                data = sys.stdin.read(MEGABYTE) 
                if not data :
                    break
                self.jobSizeBytes += len(data)    
                if not (dummy % 10) :
                    self.logdebug("%s bytes read..." % self.jobSizeBytes)
                dummy += 1    
                infile.write(data)
            self.logdebug("%s bytes read total." % self.jobSizeBytes)
            infile.flush()    
            infile.seek(0)
            return infile
        else :    
            # real file, just open it
            self.regainPriv()
            self.logdebug("Opening data stream %s" % self.preserveinputfile)
            self.jobSizeBytes = os.stat(self.preserveinputfile)[6]
            infile = open(self.preserveinputfile, "rb")
            self.dropPriv()
            return infile
        
    def closeJobDataStream(self) :    
        """Closes the file which contains the job's datas."""
        self.logdebug("Closing data stream.")
        try :
            self.jobdatastream.close()
        except :    
            pass
        
    def precomputeJobSize(self) :    
        """Computes the job size with a software method."""
        self.logdebug("Precomputing job's size with generic PDL analyzer...")
        self.jobdatastream.seek(0)
        try :
            parser = pdlanalyzer.PDLAnalyzer(self.jobdatastream)
            jobsize = parser.getJobSize()
        except pdlanalyzer.PDLAnalyzerError, msg :    
            # Here we just log the failure, but
            # we finally ignore it and return 0 since this
            # computation is just an indication of what the
            # job's size MAY be.
            self.printInfo(_("Unable to precompute the job's size with the generic PDL analyzer : %s") % msg, "warn")
            return 0
        else :    
            if ((self.printingsystem == "CUPS") \
                and (self.preserveinputfile is not None)) \
                or (self.printingsystem != "CUPS") :
                return jobsize * self.copies
            else :        
                return jobsize
            
    def sigterm_handler(self, signum, frame) :
        """Sets an attribute whenever SIGTERM is received."""
        self.gotSigTerm = 1
        os.environ["PYKOTASTATUS"] = "CANCELLED"
        self.printInfo(_("SIGTERM received, job %s cancelled.") % self.jobid)
        
    def exportJobInfo(self) :    
        """Exports job information to the environment."""
        os.environ["PYKOTAUSERNAME"] = str(self.username)
        os.environ["PYKOTAPRINTERNAME"] = str(self.printername)
        os.environ["PYKOTAJOBID"] = str(self.jobid)
        os.environ["PYKOTATITLE"] = self.title or ""
        os.environ["PYKOTAFILENAME"] = self.preserveinputfile or ""
        os.environ["PYKOTACOPIES"] = str(self.copies)
        os.environ["PYKOTAOPTIONS"] = self.options or ""
        os.environ["PYKOTAPRINTERHOSTNAME"] = self.printerhostname or "localhost"
    
    def exportUserInfo(self, userpquota) :
        """Exports user information to the environment."""
        os.environ["PYKOTAOVERCHARGE"] = str(userpquota.User.OverCharge)
        os.environ["PYKOTALIMITBY"] = str(userpquota.User.LimitBy)
        os.environ["PYKOTABALANCE"] = str(userpquota.User.AccountBalance or 0.0)
        os.environ["PYKOTALIFETIMEPAID"] = str(userpquota.User.LifeTimePaid or 0.0)
        os.environ["PYKOTAPAGECOUNTER"] = str(userpquota.PageCounter or 0)
        os.environ["PYKOTALIFEPAGECOUNTER"] = str(userpquota.LifePageCounter or 0)
        os.environ["PYKOTASOFTLIMIT"] = str(userpquota.SoftLimit)
        os.environ["PYKOTAHARDLIMIT"] = str(userpquota.HardLimit)
        os.environ["PYKOTADATELIMIT"] = str(userpquota.DateLimit)
        os.environ["PYKOTAWARNCOUNT"] = str(userpquota.WarnCount)
        
        # not really an user information, but anyway
        # exports the list of printers groups the current
        # printer is a member of
        os.environ["PYKOTAPGROUPS"] = ",".join([p.Name for p in self.storage.getParentPrinters(userpquota.Printer)])
        
    def prehook(self, userpquota) :
        """Allows plugging of an external hook before the job gets printed."""
        prehook = self.config.getPreHook(userpquota.Printer.Name)
        if prehook :
            self.logdebug("Executing pre-hook [%s]" % prehook)
            os.system(prehook)
        
    def posthook(self, userpquota) :
        """Allows plugging of an external hook after the job gets printed and/or denied."""
        posthook = self.config.getPostHook(userpquota.Printer.Name)
        if posthook :
            self.logdebug("Executing post-hook [%s]" % posthook)
            os.system(posthook)
            
    def printInfo(self, message, level="info") :        
        """Sends a message to standard error."""
        self.logger.log_message("%s" % message, level)
        
    def printMoreInfo(self, user, printer, message, level="info") :            
        """Prefixes the information printed with 'user@printer(jobid) =>'."""
        self.printInfo("%s@%s(%s) => %s" % (getattr(user, "Name", None), getattr(printer, "Name", None), self.jobid, message), level)
        
    def extractInfoFromCupsOrLprng(self) :    
        """Returns a tuple (printingsystem, printerhostname, printername, username, jobid, filename, title, options, backend).
        
           Returns (None, None, None, None, None, None, None, None, None, None) if no printing system is recognized.
        """
        # Try to detect CUPS
        if os.environ.has_key("CUPS_SERVERROOT") and os.path.isdir(os.environ.get("CUPS_SERVERROOT", "")) :
            if len(sys.argv) == 7 :
                inputfile = sys.argv[6]
            else :    
                inputfile = None
                
            # check that the DEVICE_URI environment variable's value is 
            # prefixed with "cupspykota:" otherwise don't touch it.
            # If this is the case, we have to remove the prefix from 
            # the environment before launching the real backend in cupspykota
            device_uri = os.environ.get("DEVICE_URI", "")
            if device_uri.startswith("cupspykota:") :
                fulldevice_uri = device_uri[:]
                device_uri = fulldevice_uri[len("cupspykota:"):]
                if device_uri.startswith("//") :    # lpd (at least)
                    device_uri = device_uri[2:]
                os.environ["DEVICE_URI"] = device_uri   # TODO : side effect !
            # TODO : check this for more complex urls than ipp://myprinter.dot.com:631/printers/lp
            try :
                (backend, destination) = device_uri.split(":", 1) 
            except ValueError :    
                raise PyKotaToolError, "Invalid DEVICE_URI : %s\n" % device_uri
            while destination.startswith("/") :
                destination = destination[1:]
            checkauth = destination.split("@", 1)    
            if len(checkauth) == 2 :
                destination = checkauth[1]
            printerhostname = destination.split("/")[0].split(":")[0]
            return ("CUPS", \
                    printerhostname, \
                    os.environ.get("PRINTER"), \
                    sys.argv[2].strip(), \
                    sys.argv[1].strip(), \
                    inputfile, \
                    int(sys.argv[4].strip()), \
                    sys.argv[3], \
                    sys.argv[5], \
                    backend)
        else :    
            # Try to detect LPRng
            # TODO : try to extract filename, options if available
            jseen = Jseen = Pseen = nseen = rseen = Kseen = None
            for arg in sys.argv :
                if arg.startswith("-j") :
                    jseen = arg[2:].strip()
                elif arg.startswith("-n") :     
                    nseen = arg[2:].strip()
                elif arg.startswith("-P") :    
                    Pseen = arg[2:].strip()
                elif arg.startswith("-r") :    
                    rseen = arg[2:].strip()
                elif arg.startswith("-J") :    
                    Jseen = arg[2:].strip()
                elif arg.startswith("-K") or arg.startswith("-#") :    
                    Kseen = int(arg[2:].strip())
            if Kseen is None :        
                Kseen = 1       # we assume the user wants at least one copy...
            if (rseen is None) and jseen and Pseen and nseen :    
                lparg = [arg for arg in "".join(os.environ.get("PRINTCAP_ENTRY", "").split()).split(":") if arg.startswith("rm=") or arg.startswith("lp=")]
                try :
                    rseen = lparg[0].split("=")[-1].split("@")[-1].split("%")[0]
                except :    
                    # Not found
                    self.printInfo(_("Printer hostname undefined, set to 'localhost'"), "warn")
                    rseen = "localhost"
                
            spooldir = os.environ.get("SPOOL_DIR", ".")    
            df_name = os.environ.get("DATAFILES")
            if not df_name :
                try : 
                    df_name = [line[10:] for line in os.environ.get("HF", "").split() if line.startswith("datafiles=")][0]
                except IndexError :    
                    try :    
                        df_name = [line[8:] for line in os.environ.get("HF", "").split() if line.startswith("df_name=")][0]
                    except IndexError :
                        try :
                            cftransfername = [line[15:] for line in os.environ.get("HF", "").split() if line.startswith("cftransfername=")][0]
                        except IndexError :    
                            try :
                                df_name = [line[1:] for line in os.environ.get("CONTROL", "").split() if line.startswith("fdf") or line.startswith("Udf")][0]
                            except IndexError :    
                                raise PyKotaToolError, "Unable to find the file which holds the job's datas. Please file a bug report for PyKota."
                            else :    
                                inputfile = os.path.join(spooldir, df_name) # no need to strip()
                        else :    
                            inputfile = os.path.join(spooldir, "d" + cftransfername[1:]) # no need to strip()
                    else :    
                        inputfile = os.path.join(spooldir, df_name) # no need to strip()
                else :    
                    inputfile = os.path.join(spooldir, df_name) # no need to strip()
            else :    
                inputfile = os.path.join(spooldir, df_name.strip())
                
            if jseen and Pseen and nseen and rseen :        
                options = os.environ.get("HF", "") or os.environ.get("CONTROL", "")
                return ("LPRNG", rseen, Pseen, nseen, jseen, inputfile, Kseen, Jseen, options, None)
        self.printInfo(_("Printing system unknown, args=%s") % " ".join(sys.argv), "warn")
        return (None, None, None, None, None, None, None, None, None, None)   # Unknown printing system
        
    def getPrinterUserAndUserPQuota(self) :        
        """Returns a tuple (policy, printer, user, and user print quota) on this printer.
        
           "OK" is returned in the policy if both printer, user and user print quota
           exist in the Quota Storage.
           Otherwise, the policy as defined for this printer in pykota.conf is returned.
           
           If policy was set to "EXTERNAL" and one of printer, user, or user print quota
           doesn't exist in the Quota Storage, then an external command is launched, as
           defined in the external policy for this printer in pykota.conf
           This external command can do anything, like automatically adding printers
           or users, for example, and finally extracting printer, user and user print
           quota from the Quota Storage is tried a second time.
           
           "EXTERNALERROR" is returned in case policy was "EXTERNAL" and an error status
           was returned by the external command.
        """
        for passnumber in range(1, 3) :
            printer = self.storage.getPrinter(self.printername)
            user = self.storage.getUser(self.username)
            userpquota = self.storage.getUserPQuota(user, printer)
            if printer.Exists and user.Exists and userpquota.Exists :
                policy = "OK"
                break
            (policy, args) = self.config.getPrinterPolicy(self.printername)
            if policy == "EXTERNAL" :    
                commandline = self.formatCommandLine(args, user, printer)
                if not printer.Exists :
                    self.printInfo(_("Printer %s not registered in the PyKota system, applying external policy (%s) for printer %s") % (self.printername, commandline, self.printername))
                if not user.Exists :
                    self.printInfo(_("User %s not registered in the PyKota system, applying external policy (%s) for printer %s") % (self.username, commandline, self.printername))
                if not userpquota.Exists :
                    self.printInfo(_("User %s doesn't have quota on printer %s in the PyKota system, applying external policy (%s) for printer %s") % (self.username, self.printername, commandline, self.printername))
                if os.system(commandline) :
                    self.printInfo(_("External policy %s for printer %s produced an error. Job rejected. Please check PyKota's configuration files.") % (commandline, self.printername), "error")
                    policy = "EXTERNALERROR"
                    break
            else :        
                if not printer.Exists :
                    self.printInfo(_("Printer %s not registered in the PyKota system, applying default policy (%s)") % (self.printername, policy))
                if not user.Exists :
                    self.printInfo(_("User %s not registered in the PyKota system, applying default policy (%s) for printer %s") % (self.username, policy, self.printername))
                if not userpquota.Exists :
                    self.printInfo(_("User %s doesn't have quota on printer %s in the PyKota system, applying default policy (%s)") % (self.username, self.printername, policy))
                break
        if policy == "EXTERNAL" :    
            if not printer.Exists :
                self.printInfo(_("Printer %s still not registered in the PyKota system, job will be rejected") % self.printername)
            if not user.Exists :
                self.printInfo(_("User %s still not registered in the PyKota system, job will be rejected on printer %s") % (self.username, self.printername))
            if not userpquota.Exists :
                self.printInfo(_("User %s still doesn't have quota on printer %s in the PyKota system, job will be rejected") % (self.username, self.printername))
        return (policy, printer, user, userpquota)
        
    def mainWork(self) :    
        """Main work is done here."""
        (policy, printer, user, userpquota) = self.getPrinterUserAndUserPQuota()
        # TODO : check for last user's quota in case pykota filter is used with querying
        if policy == "EXTERNALERROR" :
            # Policy was 'EXTERNAL' and the external command returned an error code
            return self.removeJob()
        elif policy == "EXTERNAL" :
            # Policy was 'EXTERNAL' and the external command wasn't able
            # to add either the printer, user or user print quota
            return self.removeJob()
        elif policy == "DENY" :    
            # Either printer, user or user print quota doesn't exist,
            # and the job should be rejected.
            return self.removeJob()
        else :
            if policy not in ("OK", "ALLOW") :
                self.printInfo(_("Invalid policy %s for printer %s") % (policy, self.printername))
                return self.removeJob()
            else :
                return self.doWork(policy, printer, user, userpquota)
