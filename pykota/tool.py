#! /usr/bin/env python

# PyKota - Print Quotas for CUPS
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
    def __init__(self, asadmin=1, doc="PyKota %s (c) 2003 %s" % (version.__version__, version.__author__)) :
        """Initializes the command line tool."""
        # locale stuff
        try :
            locale.setlocale(locale.LC_ALL, "")
            gettext.install("pykota")
        except (locale.Error, IOError) :
            gettext.NullTranslations().install()
    
        # pykota specific stuff
        self.documentation = doc
        self.config = config.PyKotaConfig("/etc")
        self.logger = logger.openLogger(self.config)
        self.storage = storage.openConnection(self.config, asadmin=asadmin)
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
        server.sendmail(adminmail, [touser], fullmessage)
        server.quit()
        
    def sendMessageToUser(self, admin, adminmail, username, subject, message) :
        """Sends an email message to a user."""
        message += _("\n\nPlease contact your system administrator :\n\n\t%s - <%s>\n") % (admin, adminmail)
        self.sendMessage(adminmail, username, "Subject: %s\n\n%s" % (subject, message))
        
    def sendMessageToAdmin(self, adminmail, subject, message) :
        """Sends an email message to the Print Quota administrator."""
        self.sendMessage(adminmail, adminmail, "Subject: %s\n\n%s" % (subject, message))
        
    def checkGroupPQuota(self, groupname, printername) :    
        """Checks the group quota on a printer and deny or accept the job."""
        printerid = self.storage.getPrinterId(printername)
        groupid = self.storage.getGroupId(groupname)
        limitby = self.storage.getGroupLimitBy(groupid)
        if limitby == "balance" : 
            balance = self.storage.getGroupBalance(groupid)
            if balance is None :
                policy = self.config.getPrinterPolicy(printername)
                if policy in [None, "ALLOW"] :
                    action = "POLICY_ALLOW"
                else :    
                    action = "POLICY_DENY"
                self.logger.log_message(_("Unable to find group %s's account balance, applying default policy (%s) for printer %s") % (groupname, action, printername))
            else :    
                # TODO : there's no warning (no account balance soft limit)
                if balance <= 0.0 :
                    action = "DENY"
                else :    
                    action = "ALLOW"
        else :
            quota = self.storage.getGroupPQuota(groupid, printerid)
            if quota is None :
                # Unknown group or printer or combination
                policy = self.config.getPrinterPolicy(printername)
                if policy in [None, "ALLOW"] :
                    action = "POLICY_ALLOW"
                else :    
                    action = "POLICY_DENY"
                self.logger.log_message(_("Unable to match group %s on printer %s, applying default policy (%s)") % (groupname, printername, action))
            else :    
                pagecounter = quota["pagecounter"]
                softlimit = quota["softlimit"]
                hardlimit = quota["hardlimit"]
                datelimit = quota["datelimit"]
                if softlimit is not None :
                    if pagecounter < softlimit :
                        action = "ALLOW"
                    else :    
                        if hardlimit is None :
                            # only a soft limit, this is equivalent to having only a hard limit
                            action = "DENY"
                        else :    
                            if softlimit <= pagecounter < hardlimit :    
                                now = DateTime.now()
                                if datelimit is not None :
                                    datelimit = DateTime.ISO.ParseDateTime(datelimit)
                                else :
                                    datelimit = now + self.config.getGraceDelay(printername)
                                    self.storage.setGroupDateLimit(groupid, printerid, datelimit)
                                if now < datelimit :
                                    action = "WARN"
                                else :    
                                    action = "DENY"
                            else :         
                                action = "DENY"
                else :        
                    if hardlimit is not None :
                        # no soft limit, only a hard one.
                        if pagecounter < hardlimit :
                            action = "ALLOW"
                        else :      
                            action = "DENY"
                    else :
                        # Both are unset, no quota, i.e. accounting only
                        action = "ALLOW"
        return action
    
    def checkUserPQuota(self, username, printername) :
        """Checks the user quota on a printer and deny or accept the job."""
        # first we check any group the user is a member of
        userid = self.storage.getUserId(username)
        for groupname in self.storage.getUserGroupsNames(userid) :
            action = self.checkGroupPQuota(groupname, printername)
            if action in ("DENY", "POLICY_DENY") :
                return action
                
        # then we check the user's own quota
        printerid = self.storage.getPrinterId(printername)
        limitby = self.storage.getUserLimitBy(userid)
        if limitby == "balance" : 
            balance = self.storage.getUserBalance(userid)
            if balance is None :
                policy = self.config.getPrinterPolicy(printername)
                if policy in [None, "ALLOW"] :
                    action = "POLICY_ALLOW"
                else :    
                    action = "POLICY_DENY"
                self.logger.log_message(_("Unable to find user %s's account balance, applying default policy (%s) for printer %s") % (username, action, printername))
            else :    
                # TODO : there's no warning (no account balance soft limit)
                if balance <= 0.0 :
                    action = "DENY"
                else :    
                    action = "ALLOW"
        else :
            quota = self.storage.getUserPQuota(userid, printerid)
            if quota is None :
                # Unknown user or printer or combination
                policy = self.config.getPrinterPolicy(printername)
                if policy in [None, "ALLOW"] :
                    action = "POLICY_ALLOW"
                else :    
                    action = "POLICY_DENY"
                self.logger.log_message(_("Unable to match user %s on printer %s, applying default policy (%s)") % (username, printername, action))
            else :    
                pagecounter = quota["pagecounter"]
                softlimit = quota["softlimit"]
                hardlimit = quota["hardlimit"]
                datelimit = quota["datelimit"]
                if softlimit is not None :
                    if pagecounter < softlimit :
                        action = "ALLOW"
                    else :    
                        if hardlimit is None :
                            # only a soft limit, this is equivalent to having only a hard limit
                            action = "DENY"
                        else :    
                            if softlimit <= pagecounter < hardlimit :    
                                now = DateTime.now()
                                if datelimit is not None :
                                    datelimit = DateTime.ISO.ParseDateTime(datelimit)
                                else :
                                    datelimit = now + self.config.getGraceDelay(printername)
                                    self.storage.setUserDateLimit(userid, printerid, datelimit)
                                if now < datelimit :
                                    action = "WARN"
                                else :    
                                    action = "DENY"
                            else :         
                                action = "DENY"
                else :        
                    if hardlimit is not None :
                        # no soft limit, only a hard one.
                        if pagecounter < hardlimit :
                            action = "ALLOW"
                        else :      
                            action = "DENY"
                    else :
                        # Both are unset, no quota, i.e. accounting only
                        action = "ALLOW"
        return action
    
    def warnGroupPQuota(self, groupname, printername=None) :
        """Checks a group quota and send messages if quota is exceeded on current printer."""
        pname = printername or self.printername
        admin = self.config.getAdmin(pname)
        adminmail = self.config.getAdminMail(pname)
        mailto = self.config.getMailTo(pname)
        action = self.checkGroupPQuota(groupname, pname)
        groupmembers = self.storage.getGroupMembersNames(groupname)
        if action.startswith("POLICY_") :
            action = action[7:]
        if action == "DENY" :
            adminmessage = _("Print Quota exceeded for group %s on printer %s") % (groupname, pname)
            self.logger.log_message(adminmessage)
            if mailto in [ "BOTH", "ADMIN" ] :
                self.sendMessageToAdmin(adminmail, _("Print Quota"), adminmessage)
            for username in groupmembers :
                if mailto in [ "BOTH", "USER" ] :
                    self.sendMessageToUser(admin, adminmail, username, _("Print Quota Exceeded"), _("You are not allowed to print anymore because\nyour group Print Quota is exceeded on printer %s.") % pname)
        elif action == "WARN" :    
            adminmessage = _("Print Quota soft limit exceeded for group %s on printer %s") % (groupname, pname)
            self.logger.log_message(adminmessage)
            if mailto in [ "BOTH", "ADMIN" ] :
                self.sendMessageToAdmin(adminmail, _("Print Quota"), adminmessage)
            for username in groupmembers :
                if mailto in [ "BOTH", "USER" ] :
                    self.sendMessageToUser(admin, adminmail, username, _("Print Quota Exceeded"), _("You will soon be forbidden to print anymore because\nyour group Print Quota is almost reached on printer %s.") % pname)
        return action        
        
    def warnUserPQuota(self, username, printername=None) :
        """Checks a user quota and send him a message if quota is exceeded on current printer."""
        pname = printername or self.printername
        admin = self.config.getAdmin(pname)
        adminmail = self.config.getAdminMail(pname)
        mailto = self.config.getMailTo(pname)
        action = self.checkUserPQuota(username, pname)
        if action.startswith("POLICY_") :
            action = action[7:]
        if action == "DENY" :
            adminmessage = _("Print Quota exceeded for user %s on printer %s") % (username, pname)
            self.logger.log_message(adminmessage)
            if mailto in [ "BOTH", "USER" ] :
                self.sendMessageToUser(admin, adminmail, username, _("Print Quota Exceeded"), _("You are not allowed to print anymore because\nyour Print Quota is exceeded on printer %s.") % pname)
            if mailto in [ "BOTH", "ADMIN" ] :
                self.sendMessageToAdmin(adminmail, _("Print Quota"), adminmessage)
        elif action == "WARN" :    
            adminmessage = _("Print Quota soft limit exceeded for user %s on printer %s") % (username, pname)
            self.logger.log_message(adminmessage)
            if mailto in [ "BOTH", "USER" ] :
                self.sendMessageToUser(admin, adminmail, username, _("Print Quota Exceeded"), _("You will soon be forbidden to print anymore because\nyour Print Quota is almost reached on printer %s.") % pname)
            if mailto in [ "BOTH", "ADMIN" ] :
                self.sendMessageToAdmin(adminmail, _("Print Quota"), adminmessage)
        return action        
    
