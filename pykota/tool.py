# PyKota
# -*- coding: ISO-8859-15 -*-

# PyKota - Print Quotas for CUPS and LPRng
#
# (c) 2003 Jerome Alet <alet@librelogiciel.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# $Id$
#
# $Log$
# Revision 1.68  2004/01/02 17:38:40  jalet
# This time it should be better...
#
# Revision 1.67  2004/01/02 17:37:09  jalet
# I'm completely stupid !!! Better to not talk while coding !
#
# Revision 1.66  2004/01/02 17:31:26  jalet
# Forgot to remove some code
#
# Revision 1.65  2003/12/06 08:14:38  jalet
# Added support for CUPS device uris which contain authentication information.
#
# Revision 1.64  2003/11/29 22:03:17  jalet
# Some code refactoring work. New code is not used at this time.
#
# Revision 1.63  2003/11/29 20:06:20  jalet
# Added 'utolower' configuration option to convert all usernames to
# lowercase when printing. All database accesses are still and will
# remain case sensitive though.
#
# Revision 1.62  2003/11/25 22:37:22  jalet
# Small code move
#
# Revision 1.61  2003/11/25 22:03:28  jalet
# No more message on stderr when the translation is not available.
#
# Revision 1.60  2003/11/25 21:54:05  jalet
# updated FAQ
#
# Revision 1.59  2003/11/25 13:33:43  jalet
# Puts 'root' instead of '' when printing from CUPS web interface (which
# gives an empty username)
#
# Revision 1.58  2003/11/21 14:28:45  jalet
# More complete job history.
#
# Revision 1.57  2003/11/19 23:19:38  jalet
# Code refactoring work.
# Explicit redirection to /dev/null has to be set in external policy now, just
# like in external mailto.
#
# Revision 1.56  2003/11/19 07:40:20  jalet
# Missing import statement.
# Better documentation for mailto: external(...)
#
# Revision 1.55  2003/11/18 23:43:12  jalet
# Mailto can be any external command now, as usual.
#
# Revision 1.54  2003/10/24 21:52:46  jalet
# Now can force language when coming from CGI script.
#
# Revision 1.53  2003/10/08 21:41:38  jalet
# External policies for printers works !
# We can now auto-add users on first print, and do other useful things if needed.
#
# Revision 1.52  2003/10/07 09:07:28  jalet
# Character encoding added to please latest version of Python
#
# Revision 1.51  2003/10/06 14:21:41  jalet
# Test reversed to not retrieve group members when no messages for them.
#
# Revision 1.50  2003/10/02 20:23:18  jalet
# Storage caching mechanism added.
#
# Revision 1.49  2003/07/29 20:55:17  jalet
# 1.14 is out !
#
# Revision 1.48  2003/07/21 23:01:56  jalet
# Modified some messages aout soft limit
#
# Revision 1.47  2003/07/16 21:53:08  jalet
# Really big modifications wrt new configuration file's location and content.
#
# Revision 1.46  2003/07/09 20:17:07  jalet
# Email field added to PostgreSQL schema
#
# Revision 1.45  2003/07/08 19:43:51  jalet
# Configurable warning messages.
# Poor man's treshold value added.
#
# Revision 1.44  2003/07/07 11:49:24  jalet
# Lots of small fixes with the help of PyChecker
#
# Revision 1.43  2003/07/04 09:06:32  jalet
# Small bug fix wrt undefined "LimitBy" field.
#
# Revision 1.42  2003/06/30 12:46:15  jalet
# Extracted reporting code.
#
# Revision 1.41  2003/06/25 14:10:01  jalet
# Hey, it may work (edpykota --reset excepted) !
#
# Revision 1.40  2003/06/10 16:37:54  jalet
# Deletion of the second user which is not needed anymore.
# Added a debug configuration field in /etc/pykota.conf
# All queries can now be sent to the logger in debug mode, this will
# greatly help improve performance when time for this will come.
#
# Revision 1.39  2003/04/29 18:37:54  jalet
# Pluggable accounting methods (actually doesn't support external scripts)
#
# Revision 1.38  2003/04/24 11:53:48  jalet
# Default policy for unknown users/groups is to DENY printing instead
# of the previous default to ALLOW printing. This is to solve an accuracy
# problem. If you set the policy to ALLOW, jobs printed by in nexistant user
# (from PyKota's POV) will be charged to the next user who prints on the
# same printer.
#
# Revision 1.37  2003/04/24 08:08:27  jalet
# Debug message forgotten
#
# Revision 1.36  2003/04/24 07:59:40  jalet
# LPRng support now works !
#
# Revision 1.35  2003/04/23 22:13:57  jalet
# Preliminary support for LPRng added BUT STILL UNTESTED.
#
# Revision 1.34  2003/04/17 09:26:21  jalet
# repykota now reports account balances too.
#
# Revision 1.33  2003/04/16 12:35:49  jalet
# Groups quota work now !
#
# Revision 1.32  2003/04/16 08:53:14  jalet
# Printing can now be limited either by user's account balance or by
# page quota (the default). Quota report doesn't include account balance
# yet, though.
#
# Revision 1.31  2003/04/15 11:30:57  jalet
# More work done on money print charging.
# Minor bugs corrected.
# All tools now access to the storage as priviledged users, repykota excepted.
#
# Revision 1.30  2003/04/10 21:47:20  jalet
# Job history added. Upgrade script neutralized for now !
#
# Revision 1.29  2003/03/29 13:45:27  jalet
# GPL paragraphs were incorrectly (from memory) copied into the sources.
# Two README files were added.
# Upgrade script for PostgreSQL pre 1.01 schema was added.
#
# Revision 1.28  2003/03/29 13:08:28  jalet
# Configuration is now expected to be found in /etc/pykota.conf instead of
# in /etc/cups/pykota.conf
# Installation script can move old config files to the new location if needed.
# Better error handling if configuration file is absent.
#
# Revision 1.27  2003/03/15 23:01:28  jalet
# New mailto option in configuration file added.
# No time to test this tonight (although it should work).
#
# Revision 1.26  2003/03/09 23:58:16  jalet
# Comment
#
# Revision 1.25  2003/03/07 22:56:14  jalet
# 0.99 is out with some bug fixes.
#
# Revision 1.24  2003/02/27 23:48:41  jalet
# Correctly maps PyKota's log levels to syslog log levels
#
# Revision 1.23  2003/02/27 22:55:20  jalet
# WARN log priority doesn't exist.
#
# Revision 1.22  2003/02/27 09:09:20  jalet
# Added a method to match strings against wildcard patterns
#
# Revision 1.21  2003/02/17 23:01:56  jalet
# Typos
#
# Revision 1.20  2003/02/17 22:55:01  jalet
# More options can now be set per printer or globally :
#
#       admin
#       adminmail
#       gracedelay
#       requester
#
# the printer option has priority when both are defined.
#
# Revision 1.19  2003/02/10 11:28:45  jalet
# Localization
#
# Revision 1.18  2003/02/10 01:02:17  jalet
# External requester is about to work, but I must sleep
#
# Revision 1.17  2003/02/09 13:05:43  jalet
# Internationalization continues...
#
# Revision 1.16  2003/02/09 12:56:53  jalet
# Internationalization begins...
#
# Revision 1.15  2003/02/08 22:09:52  jalet
# Name check method moved here
#
# Revision 1.14  2003/02/07 10:42:45  jalet
# Indentation problem
#
# Revision 1.13  2003/02/07 08:34:16  jalet
# Test wrt date limit was wrong
#
# Revision 1.12  2003/02/06 23:20:02  jalet
# warnpykota doesn't need any user/group name argument, mimicing the
# warnquota disk quota tool.
#
# Revision 1.11  2003/02/06 22:54:33  jalet
# warnpykota should be ok
#
# Revision 1.10  2003/02/06 15:03:11  jalet
# added a method to set the limit date
#
# Revision 1.9  2003/02/06 10:39:23  jalet
# Preliminary edpykota work.
#
# Revision 1.8  2003/02/06 09:19:02  jalet
# More robust behavior (hopefully) when the user or printer is not managed
# correctly by the Quota System : e.g. cupsFilter added in ppd file, but
# printer and/or user not 'yet?' in storage.
#
# Revision 1.7  2003/02/06 00:00:45  jalet
# Now includes the printer name in email messages
#
# Revision 1.6  2003/02/05 23:55:02  jalet
# Cleaner email messages
#
# Revision 1.5  2003/02/05 23:45:09  jalet
# Better DateTime manipulation wrt grace delay
#
# Revision 1.4  2003/02/05 23:26:22  jalet
# Incorrect handling of grace delay
#
# Revision 1.3  2003/02/05 22:16:20  jalet
# DEVICE_URI is undefined outside of CUPS, i.e. for normal command line tools
#
# Revision 1.2  2003/02/05 22:10:29  jalet
# Typos
#
# Revision 1.1  2003/02/05 21:28:17  jalet
# Initial import into CVS
#
#
#

import sys
import os
import fnmatch
import getopt
import smtplib
import gettext
import locale

from mx import DateTime

from pykota import version, config, storage, logger, accounter

class PyKotaToolError(Exception):
    """An exception for PyKota config related stuff."""
    def __init__(self, message = ""):
        self.message = message
        Exception.__init__(self, message)
    def __repr__(self):
        return self.message
    __str__ = __repr__
    
class PyKotaTool :    
    """Base class for all PyKota command line tools."""
    def __init__(self, lang=None, doc="PyKota %s (c) 2003 %s" % (version.__version__, version.__author__)) :
        """Initializes the command line tool."""
        # locale stuff
        try :
            locale.setlocale(locale.LC_ALL, lang)
            gettext.install("pykota")
        except (locale.Error, IOError) :
            gettext.NullTranslations().install()
            # sys.stderr.write("PyKota : Error while loading translations\n")
    
        # pykota specific stuff
        self.documentation = doc
        self.config = config.PyKotaConfig("/etc/pykota")
        self.logger = logger.openLogger(self.config.getLoggingBackend())
        self.debug = self.config.getDebug()
        self.storage = storage.openConnection(self)
        self.smtpserver = self.config.getSMTPServer()
        
    def logdebug(self, message) :    
        """Logs something to debug output if debug is enabled."""
        if self.debug :
            self.logger.log_message(message, "debug")
        
    def clean(self) :    
        """Ensures that the database is closed."""
        try :
            self.storage.close()
        except (TypeError, NameError, AttributeError) :    
            pass
            
    def display_version_and_quit(self) :
        """Displays version number, then exists successfully."""
        self.clean()
        print version.__version__
        sys.exit(0)
    
    def display_usage_and_quit(self) :
        """Displays command line usage, then exists successfully."""
        self.clean()
        print self.documentation
        sys.exit(0)
        
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
            sys.stderr.write("%s\n" % msg)
            sys.stderr.flush()
            self.display_usage_and_quit()
        return (parsed, args)
    
    def isValidName(self, name) :
        """Checks if a user or printer name is valid."""
        # unfortunately Python 2.1 string modules doesn't define ascii_letters...
        asciiletters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        digits = '0123456789'
        if name[0] in asciiletters :
            validchars = asciiletters + digits + "-_"
            for c in name[1:] :
                if c not in validchars :
                    return 0
            return 1        
        return 0
        
    def matchString(self, s, patterns) :
        """Returns 1 if the string s matches one of the patterns, else 0."""
        for pattern in patterns :
            if fnmatch.fnmatchcase(s, pattern) :
                return 1
        return 0
        
    def sendMessage(self, adminmail, touser, fullmessage) :
        """Sends an email message containing headers to some user."""
        if "@" not in touser :
            touser = "%s@%s" % (touser, self.smtpserver)
        server = smtplib.SMTP(self.smtpserver)
        try :
            server.sendmail(adminmail, [touser], fullmessage)
        except smtplib.SMTPRecipientsRefused, answer :    
            for (k, v) in answer.recipients.items() :
                self.logger.log_message(_("Impossible to send mail to %s, error %s : %s") % (k, v[0], v[1]), "error")
        server.quit()
        
    def sendMessageToUser(self, admin, adminmail, user, subject, message) :
        """Sends an email message to a user."""
        message += _("\n\nPlease contact your system administrator :\n\n\t%s - <%s>\n") % (admin, adminmail)
        self.sendMessage(adminmail, user.Email or user.Name, "Subject: %s\n\n%s" % (subject, message))
        
    def sendMessageToAdmin(self, adminmail, subject, message) :
        """Sends an email message to the Print Quota administrator."""
        self.sendMessage(adminmail, adminmail, "Subject: %s\n\n%s" % (subject, message))
        
    def checkGroupPQuota(self, grouppquota) :    
        """Checks the group quota on a printer and deny or accept the job."""
        group = grouppquota.Group
        printer = grouppquota.Printer
        if group.LimitBy and (group.LimitBy.lower() == "balance") : 
            if group.AccountBalance <= 0.0 :
                action = "DENY"
            elif group.AccountBalance <= self.config.getPoorMan() :    
                action = "WARN"
            else :    
                action = "ALLOW"
        else :
            if grouppquota.SoftLimit is not None :
                softlimit = int(grouppquota.SoftLimit)
                if grouppquota.PageCounter < softlimit :
                    action = "ALLOW"
                else :    
                    if grouppquota.HardLimit is None :
                        # only a soft limit, this is equivalent to having only a hard limit
                        action = "DENY"
                    else :    
                        hardlimit = int(grouppquota.HardLimit)
                        if softlimit <= grouppquota.PageCounter < hardlimit :    
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
                    if grouppquota.PageCounter < hardlimit :
                        action = "ALLOW"
                    else :      
                        action = "DENY"
                else :
                    # Both are unset, no quota, i.e. accounting only
                    action = "ALLOW"
        return action
    
    def checkUserPQuota(self, userpquota) :
        """Checks the user quota on a printer and deny or accept the job."""
        user = userpquota.User
        printer = userpquota.Printer
        
        # first we check any group the user is a member of
        for group in self.storage.getUserGroups(user) :
            grouppquota = self.storage.getGroupPQuota(group, printer)
            if grouppquota.Exists :
                action = self.checkGroupPQuota(grouppquota)
                if action == "DENY" :
                    return action
                
        # then we check the user's own quota
        # if we get there we are sure that policy is not EXTERNAL
        (policy, dummy) = self.config.getPrinterPolicy(printer.Name)
        if user.LimitBy and (user.LimitBy.lower() == "balance") : 
            if user.AccountBalance is None :
                if policy == "ALLOW" :
                    action = "POLICY_ALLOW"
                else :    
                    action = "POLICY_DENY"
                self.logger.log_message(_("Unable to find user %s's account balance, applying default policy (%s) for printer %s") % (user.Name, action, printer.Name))
            else :    
                val = float(user.AccountBalance or 0.0)
                if val <= 0.0 :
                    action = "DENY"
                elif val <= self.config.getPoorMan() :    
                    action = "WARN"
                else :    
                    action = "ALLOW"
        else :
            if not userpquota.Exists :
                # Unknown userquota 
                if policy == "ALLOW" :
                    action = "POLICY_ALLOW"
                else :    
                    action = "POLICY_DENY"
                self.logger.log_message(_("Unable to match user %s on printer %s, applying default policy (%s)") % (user.Name, printer.Name, action))
            else :    
                pagecounter = int(userpquota.PageCounter or 0)
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
    
    def externalMailTo(self, cmd, action, user, printer, message) :
        """Warns the user with an external command."""
        username = user.Name
        printername = printer.Name
        email = user.Email or user.Name
        if "@" not in email :
            email = "%s@%s" % (email, self.smtpserver)
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
            self.logger.log_message(adminmessage)
            if mailto in [ "BOTH", "ADMIN" ] :
                self.sendMessageToAdmin(adminmail, _("Print Quota"), adminmessage)
            if mailto in [ "BOTH", "USER", "EXTERNAL" ] :
                for user in self.storage.getGroupMembers(group) :
                    if mailto != "EXTERNAL" :
                        self.sendMessageToUser(admin, adminmail, user, _("Print Quota Exceeded"), self.config.getHardWarn(printer.Name))
                    else :    
                        self.externalMailTo(arguments, action, user, printer, message)
        elif action == "WARN" :    
            adminmessage = _("Print Quota low for group %s on printer %s") % (group.Name, printer.Name)
            self.logger.log_message(adminmessage)
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
            self.logger.log_message(adminmessage)
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
            self.logger.log_message(adminmessage)
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
        self.username = self.username or 'root' 
        if self.config.getUserNameToLower() :
            self.username = self.username.lower()
        self.preserveinputfile = self.inputfile 
        self.accounter = accounter.openAccounter(self)
    
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
            # TODO : try to extract filename, job's title, and options if available
            jseen = Pseen = nseen = rseen = Kseen = None
            for arg in sys.argv :
                if arg.startswith("-j") :
                    jseen = arg[2:].strip()
                elif arg.startswith("-n") :     
                    nseen = arg[2:].strip()
                elif arg.startswith("-P") :    
                    Pseen = arg[2:].strip()
                elif arg.startswith("-r") :    
                    rseen = arg[2:].strip()
                elif arg.startswith("-K") or arg.startswith("-#") :    
                    Kseen = int(arg[2:].strip())
            if Kseen is None :        
                Kseen = 1       # we assume the user wants at least one copy...
            if (rseen is None) and jseen and Pseen and nseen :    
                self.logger.log_message(_("Printer hostname undefined, set to 'localhost'"), "warn")
                rseen = "localhost"
            if jseen and Pseen and nseen and rseen :        
                # job is always in stdin (None)
                return ("LPRNG", rseen, Pseen, nseen, jseen, None, Kseen, None, None, None)
        self.logger.log_message(_("Printing system unknown, args=%s") % " ".join(sys.argv), "warn")
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
                    self.logger.log_message(_("Printer %s not registered in the PyKota system, applying external policy (%s) for printer %s") % (self.printername, commandline, self.printername), "info")
                if not user.Exists :
                    self.logger.log_message(_("User %s not registered in the PyKota system, applying external policy (%s) for printer %s") % (self.username, commandline, self.printername), "info")
                if not userpquota.Exists :
                    self.logger.log_message(_("User %s doesn't have quota on printer %s in the PyKota system, applying external policy (%s) for printer %s") % (self.username, self.printername, commandline, self.printername), "info")
                if os.system(commandline) :
                    # if an error occured, we die without error,
                    # so that the job doesn't stop the print queue.
                    self.logger.log_message(_("External policy %s for printer %s produced an error. Job rejected. Please check PyKota's configuration files.") % (commandline, self.printername), "error")
                    policy = "EXTERNALERROR"
                    break
            else :        
                break
        return (policy, printer, user, userpquota)
        
    def main(self) :    
        """Main work is done here."""
        (policy, printer, user, userpquota) = self.getPrinterUserAndUserPQuota()
        if policy == "EXTERNALERROR" :
            # Policy was 'EXTERNAL' and the external command returned an error code
            pass # TODO : reject job
        elif policy == "EXTERNAL" :
            # Policy was 'EXTERNAL' and the external command wasn't able
            # to add either the printer, user or user print quota
            pass # TODO : reject job
        elif policy == "ALLOW":
            # Either printer, user or user print quota doesn't exist,
            # but the job should be allowed anyway.
            pass # TODO : accept job
        elif policy == "OK" :
            # Both printer, user and user print quota exist, job should
            # be allowed if current user is allowed to print on this
            # printer
            pass # TODO : decide what to do based on user quota.
        else : # DENY
            # Either printer, user or user print quota doesn't exist,
            # and the job should be rejected.
            pass # TODO : reject job
