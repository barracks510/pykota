# -*- coding: utf-8 -*-*-
#
# PyKota : Print Quotas for CUPS
#
# (c) 2003, 2004, 2005, 2006, 2007, 2008 Jerome Alet <alet@librelogiciel.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# $Id$
#
#

"""This module defines the base classes for PyKota command line tools."""

import sys
import os
import pwd
import fnmatch
import getopt
import smtplib
import locale
import socket
import time
from email.MIMEText import MIMEText
from email.Header import Header
import email.Utils

from mx import DateTime

from pykota import utils
from pykota.errors import PyKotaCommandLineError
from pykota import config, storage, logger
from pykota.version import __version__, __author__, __years__, __gplblurb__

class Percent :
    """A class to display progress."""
    def __init__(self, app, size=None) :
        """Initializes the engine."""
        self.isatty = sys.stdout.isatty()
        self.app = app
        self.size = None
        if size :
            self.setSize(size)
        self.previous = None
        self.before = time.time()

    def setSize(self, size) :
        """Sets the total size."""
        self.number = 0
        self.size = size
        if size :
            self.factor = 100.0 / float(size)

    def display(self, msg) :
        """Displays the value."""
        if self.isatty :
            self.app.display(msg)
            sys.stdout.flush()

    def oneMore(self) :
        """Increments internal counter."""
        if self.size :
            self.number += 1
            percent = "%.02f" % (float(self.number) * self.factor)
            if percent != self.previous : # optimize for large number of items
                self.display("\r%s%%" % percent)
                self.previous = percent

    def done(self) :
        """Displays the 'done' message."""
        after = time.time()
        if self.size :
            try :
                speed = self.size / ((after - self.before) + 0.00000000001) # adds an epsilon to avoid an user's problem I can't reproduce...
            except ZeroDivisionError :
                speed = 1 # Fake value in case of division by zero, shouldn't happen anyway with the epsilon above...
            self.display("\r100.00%%\r        \r%s. %s : %.2f %s.\n" \
                     % (_("Done"), _("Average speed"), speed, _("entries per second")))
        else :
            self.display("\r100.00%%\r        \r%s.\n" % _("Done"))

class Tool :
    """Base class for tools with no database access."""
    def __init__(self, doc="PyKota v%(__version__)s (c) %(__years__)s %(__author__)s") :
        """Initializes the command line tool."""
        self.debug = True # in case of early failure
        self.logger = logger.openLogger("stderr")

        # Saves a copy of the locale settings
        (self.language, self.charset) = locale.getlocale()
        if not self.language :
            self.language = "C"
        if not self.charset :
            self.charset = "UTF-8"

        # pykota specific stuff
        self.documentation = doc

        # Extract the effective username
        uid = os.geteuid()
        try :
            self.effectiveUserName = pwd.getpwuid(uid)[0]
        except (KeyError, IndexError), msg :
            self.printInfo(_("Strange problem with uid(%s) : %s") % (uid, msg), "warn")
            self.effectiveUserName = os.getlogin()

    def deferredInit(self) :
        """Deferred initialization."""
        confdir = os.environ.get("PYKOTA_HOME")
        environHome = True
        missingUser = False
        if confdir is None :
            environHome = False
            # check for config files in the 'pykota' user's home directory.
            try :
                self.pykotauser = pwd.getpwnam("pykota")
                confdir = self.pykotauser[5]
            except KeyError :
                self.pykotauser = None
                confdir = "/etc/pykota"
                missingUser = True

        self.config = config.PyKotaConfig(confdir)
        self.debug = self.config.getDebug()
        self.smtpserver = self.config.getSMTPServer()
        self.maildomain = self.config.getMailDomain()
        self.logger = logger.openLogger(self.config.getLoggingBackend())

        # TODO : We NEED this here, even when not in an accounting filter/backend
        self.softwareJobSize = 0
        self.softwareJobPrice = 0.0

        if environHome :
            self.printInfo("PYKOTA_HOME environment variable is set. Configuration files were searched in %s" % confdir, "info")
        else :
            if missingUser :
                self.printInfo("The 'pykota' system account is missing. Configuration files were searched in %s instead." % confdir, "warn")

        self.logdebug("Language in use : %s" % self.language)
        self.logdebug("Charset in use : %s" % self.charset)

        arguments = " ".join(['"%s"' % arg for arg in sys.argv])
        self.logdebug("Command line arguments : %s" % arguments)

    def display(self, message) :
        """Display a message after ensuring the correct charset is used."""
        sys.stdout.write(message.encode(self.charset,
                                            "replace"))

    def logdebug(self, message) :
        """Logs something to debug output if debug is enabled."""
        if self.debug :
            self.logger.log_message(message.encode(self.charset, \
                                                   "replace"), \
                                    "debug")

    def printInfo(self, message, level="info") :
        """Sends a message to standard error."""
        sys.stderr.write("%s: %s\n" % (level.upper(), \
                                       message.encode(self.charset, \
                                                      "replace")))
        sys.stderr.flush()

    def adminOnly(self, restricted=True) :
        """Raises an exception if the user is not a PyKota administrator."""
        if restricted and not self.config.isAdmin :
            raise PyKotaCommandLineError, "%s : %s" % (pwd.getpwuid(os.geteuid())[0], _("You're not allowed to use this command."))

    def matchString(self, s, patterns) :
        """Returns True if the string s matches one of the patterns, else False."""
        if not patterns :
            return True # No pattern, always matches.
        else :
            for pattern in patterns :
                if fnmatch.fnmatchcase(s, pattern) :
                    return True
            return False

    def sanitizeNames(self, names, isgroups) :
        """Sanitize users and groups names if needed."""
        if not self.config.isAdmin :
            username = pwd.getpwuid(os.geteuid())[0]
            if isgroups :
                user = self.storage.getUser(username)
                if user.Exists :
                    return [ g.Name for g in self.storage.getUserGroups(user) ]
            return [ username ]
        return names

    def display_version_and_quit(self) :
        """Displays version number, then exists successfully."""
        try :
            self.clean()
        except AttributeError :
            pass
        self.display("%s\n" % __version__)
        sys.exit(0)

    def display_usage_and_quit(self) :
        """Displays command line usage, then exists successfully."""
        try :
            self.clean()
        except AttributeError :
            pass
        self.display("%s\n" % (_(self.documentation) % globals()))
        self.display("%s\n\n" % __gplblurb__)
        self.display("%s %s\n" % (_("Please report bugs to :"), __author__))
        sys.exit(0)

    def crashed(self, message="Bug in PyKota") :
        """Outputs a crash message, and optionally sends it to software author."""
        msg = utils.crashed(message)
        fullmessage = "========== Traceback :\n\n%s\n\n========== sys.argv :\n\n%s\n\n========== Environment :\n\n%s\n" % \
                        (msg, \
                         "\n".join(["    %s" % repr(a) for a in sys.argv]), \
                         "\n".join(["    %s=%s" % (k, repr(v)) for (k, v) in os.environ.items()]))
        try :
            crashrecipient = self.config.getCrashRecipient()
            if crashrecipient :
                admin = self.config.getAdminMail("global") # Nice trick, isn't it ?
                server = smtplib.SMTP(self.smtpserver)
                msg = MIMEText(fullmessage.encode(self.charset, "replace"), _charset=self.charset)
                msg["Subject"] = Header("PyKota v%s crash traceback !" \
                                        % __version__, charset=self.charset, errors="replace")
                msg["From"] = admin
                msg["To"] = crashrecipient
                msg["Cc"] = admin
                msg["Date"] = email.Utils.formatdate(localtime=True)
                server.sendmail(admin, [admin, crashrecipient], msg.as_string())
                server.quit()
        except :
            self.printInfo("PyKota double crash !", "error")
            raise
        return fullmessage

    def parseCommandline(self, argv, short, long, allownothing=0) :
        """Parses the command line, controlling options."""
        # split options in two lists: those which need an argument, those which don't need any
        short = "%sA:" % short
        long.append("arguments=")
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

        # then we parse the command line
        done = 0
        while not done :
            # we begin with all possible options unset
            parsed = {}
            for option in withoutarg + witharg :
                parsed[option] = None
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
                            raise PyKotaCommandLineError, "Unexpected problem when parsing command line"
                elif (not args) and (not allownothing) and sys.stdin.isatty() : # no option and no argument, we display help if we are a tty
                    self.display_usage_and_quit()
            except getopt.error, msg :
                raise PyKotaCommandLineError, str(msg)
            else :
                if parsed["arguments"] or parsed["A"] :
                    # arguments are in a file, we ignore all other arguments
                    # and reset the list of arguments to the lines read from
                    # the file.
                    argsfile = open(parsed["arguments"] or parsed["A"], "r") # TODO : charset decoding
                    argv = [ l.strip() for l in argsfile.readlines() ]
                    argsfile.close()
                    for i in range(len(argv)) :
                        argi = argv[i]
                        if argi.startswith('"') and argi.endswith('"') :
                            argv[i] = argi[1:-1]
                else :
                    done = 1
        return (parsed, args)

class PyKotaTool(Tool) :
    """Base class for all PyKota command line tools."""
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
                                datelimit = DateTime.ISO.ParseDateTime(str(userpquota.DateLimit)[:19])
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
            balancezero = self.config.getBalanceZero()
            if val <= balancezero :
                action = "DENY"
            elif val <= self.config.getPoorMan() :
                action = "WARN"
            else :
                action = "ALLOW"
            if (enforcement == "STRICT") and (val == balancezero) :
                action = "WARN" # we can still print until account is 0
        else :
            val = grouppquota.PageCounter or 0
            if enforcement == "STRICT" :
                val += int(self.softwareJobSize) # TODO : this is not a fix, problem is elsewhere in grouppquota.PageCounter
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
                                datelimit = DateTime.ISO.ParseDateTime(str(grouppquota.DateLimit)[:19])
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
                    balancezero = self.config.getBalanceZero()
                    if val <= balancezero :
                        action = "DENY"
                    elif val <= self.config.getPoorMan() :
                        action = "WARN"
                    else :
                        action = "ALLOW"
                    if (enforcement == "STRICT") and (val == balancezero) :
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

