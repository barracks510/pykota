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

from pykota import config, storage, logger, accounter
from pykota.version import __version__, __author__, __years__, __gplblurb__

try :
    from pkpgpdls import analyzer, pdlparser
except ImportError : # TODO : Remove the try/except after release 1.24.
    sys.stderr.write("ERROR: pkpgcounter is now distributed separately, please grab it from http://www.librelogiciel.com/software/pkpgcounter/action_Download\n")
    
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
    msg = "ERROR: ".join(["%s\n" % l for l in (["ERROR: PyKota v%s" % __version__, message] + lines)])
    sys.stderr.write(msg)
    sys.stderr.flush()
    return msg

class Tool :
    """Base class for tools with no database access."""
    def __init__(self, lang="", charset=None, doc="PyKota v%(__version__)s (c) %(__years__)s %(__author__)s") :
        """Initializes the command line tool."""
        # did we drop priviledges ?
        self.privdropped = 0
        
        # locale stuff
        self.defaultToCLocale = 0
        try :
            locale.setlocale(locale.LC_ALL, lang)
        except (locale.Error, IOError) :
            # locale.setlocale(locale.LC_ALL, "C")
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
            self.printInfo("Incorrect locale settings. PyKota falls back to the default locale.", "warn")
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
        print __version__
        sys.exit(0)
    
    def display_usage_and_quit(self) :
        """Displays command line usage, then exists successfully."""
        try :
            self.clean()
        except AttributeError :    
            pass
        print _(self.documentation) % globals()
        print __gplblurb__
        print
        print _("Please report bugs to :"), __author__
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
                                       (admin, crashrecipient, admin, __version__, fullmessage))
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
    def __init__(self, lang="", charset=None, doc="PyKota v%(__version__)s (c) %(__years__)s %(__author__)s") :
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
            # No need to check anything if the group is in noquota mode
            if group.LimitBy != "noquota" :
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
        
