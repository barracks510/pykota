#! /usr/bin/env python

# PyKota - Print Quotas for CUPS
#
# (c) 2003 Jerome Alet <alet@librelogiciel.com>
# You're welcome to redistribute this software under the
# terms of the GNU General Public Licence version 2.0
# or, at your option, any higher version.
#
# You can read the complete GNU GPL in the file COPYING
# which should come along with this software, or visit
# the Free Software Foundation's WEB site http://www.fsf.org
#
# $Id$
#
# $Log$
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
import getopt
import smtplib
import gettext
import locale

from mx import DateTime

from pykota import version, config, storage, logger

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
    def __init__(self, isfilter=0, doc="PyKota %s (c) 2003 %s" % (version.__version__, version.__author__)) :
        """Initializes the command line tool."""
        # locale stuff
        try :
            locale.setlocale(locale.LC_ALL, "")
            gettext.install("pykota")
        except (locale.Error, IOError) :
            gettext.NullTranslations().install()
    
        # pykota specific stuff
        self.documentation = doc
        self.config = config.PyKotaConfig(os.environ.get("CUPS_SERVERROOT", "/etc/cups"))
        self.logger = logger.openLogger(self.config)
        self.storage = storage.openConnection(self.config, asadmin=(not isfilter))
        self.printername = os.environ.get("PRINTER", None)
        self.smtpserver = self.config.getSMTPServer()
        
    def display_version_and_quit(self) :
        """Displays version number, then exists successfully."""
        print version.__version__
        sys.exit(0)
    
    def display_usage_and_quit(self) :
        """Displays command line usage, then exists successfully."""
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
        
    def sendMessage(self, adminmail, touser, fullmessage) :
        """Sends an email message containing headers to some user."""
        if "@" not in touser :
            touser = "%s@%s" % (touser, self.smtpserver)
        server = smtplib.SMTP(self.smtpserver)
        server.sendmail(adminmail, [touser], fullmessage)
        server.quit()
        
    def sendMessageToUser(self, admin, adminmail, username, subject, message) :
        """Sends an email message to a user."""
        message += _("\n\nPlease contact your system administrator :\n\n\t%s - <%s>\n") % (admin, adminmail)
        self.sendMessage(adminmail, username, "Subject: %s\n\n%s" % (subject, message))
        
    def sendMessageToAdmin(self, adminmail, subject, message) :
        """Sends an email message to the Print Quota administrator."""
        self.sendMessage(adminmail, adminmail, "Subject: %s\n\n%s" % (subject, message))
        
    def checkUserPQuota(self, username, printername) :
        """Checks the user quota on a printer and deny or accept the job."""
        quota = self.storage.getUserPQuota(username, printername)
        if quota is None :
            # Unknown user or printer or combination
            policy = self.config.getPrinterPolicy(printername)
            if policy in [None, "ALLOW"] :
                action = "ALLOW"
            else :    
                action = "DENY"
            self.logger.log_message(_("Unable to match user %s on printer %s, applying default policy (%s)") % (username, printername, action), "warn")
            return (action, None, None)
        else :    
            pagecounter = quota["pagecounter"]
            softlimit = quota["softlimit"]
            hardlimit = quota["hardlimit"]
            datelimit = quota["datelimit"]
            if datelimit is not None :
                datelimit = DateTime.ISO.ParseDateTime(datelimit)
            if softlimit is not None :
                if pagecounter < softlimit :
                    action = "ALLOW"
                elif hardlimit is not None :
                    if softlimit <= pagecounter < hardlimit :    
                        now = DateTime.now()
                        if datelimit is None :
                            datelimit = now + self.config.getGraceDelay(printername)
                            self.storage.setDateLimit(username, printername, datelimit)
                        if now < datelimit :
                            action = "WARN"
                        else :    
                            action = "DENY"
                    else :         
                        action = "DENY"
                else :        
                    action = "DENY"
            else :        
                action = "ALLOW"
            return (action, (hardlimit - pagecounter), datelimit)
    
    def warnGroupPQuota(self, username, printername=None) :
        """Checks a user quota and send him a message if quota is exceeded on current printer."""
        pname = printername or self.printername
        raise PyKotaToolError, _("Group quotas are currently not implemented.")
        
    def warnUserPQuota(self, username, printername=None) :
        """Checks a user quota and send him a message if quota is exceeded on current printer."""
        pname = printername or self.printername
        admin = self.config.getAdmin(pname)
        adminmail = self.config.getAdminMail(pname)
        (action, grace, gracedate) = self.checkUserPQuota(username, pname)
        if action == "DENY" :
            if (grace is not None) and (gracedate is not None) :
                # only when both user and printer are known
                adminmessage = _("Print Quota exceeded for user %s on printer %s") % (username, pname)
                self.logger.log_message(adminmessage)
                self.sendMessageToUser(admin, adminmail, username, _("Print Quota Exceeded"), _("You are not allowed to print anymore because\nyour Print Quota is exceeded on printer %s.") % pname)
                self.sendMessageToAdmin(adminmail, _("Print Quota"), adminmessage)
        elif action == "WARN" :    
            adminmessage = _("Print Quota soft limit exceeded for user %s on printer %s") % (username, pname)
            self.logger.log_message(adminmessage)
            self.sendMessageToUser(admin, adminmail, username, _("Print Quota Exceeded"), _("You will soon be forbidden to print anymore because\nyour Print Quota is almost reached on printer %s.") % pname)
            self.sendMessageToAdmin(adminmail, _("Print Quota"), adminmessage)
        return action        
    
