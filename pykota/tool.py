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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# $Id$
#
# $Log$
# Revision 1.132  2004/10/19 21:45:25  jalet
# Now correctly logs command line arguments
#
# Revision 1.131  2004/10/19 21:37:57  jalet
# Fixes recently introduced bug
#
# Revision 1.130  2004/10/19 15:21:48  jalet
# Fixed incorrect setting of the user's locale
#
# Revision 1.129  2004/10/13 20:51:27  jalet
# Made debugging levels be the same in cupspykota and lprngpykota.
# Now outputs more information in informational messages : user, printer, jobid
#
# Revision 1.128  2004/10/11 22:53:06  jalet
# Postponed string interpolation to help message's output method
#
# Revision 1.127  2004/10/11 12:48:38  jalet
# Adds fake translation marker
#
# Revision 1.126  2004/10/05 09:41:13  jalet
# Small fix for errors caused by unknown locale
#
# Revision 1.125  2004/10/04 11:18:10  jalet
# Now exports the MD5 sum of the job's datas as an hexadecimal digest
#
# Revision 1.124  2004/10/02 05:48:56  jalet
# Should now correctly deal with charsets both when storing into databases and when
# retrieving datas. Works with both PostgreSQL and LDAP.
#
# Revision 1.123  2004/09/29 20:20:52  jalet
# Added the winbind_separator directive to pykota.conf to allow the admin to
# strip out the Samba/Winbind domain name when users print.
#
# Revision 1.122  2004/09/28 21:38:56  jalet
# Now computes the job's datas MD5 checksum to later forbid duplicate print jobs.
# The checksum is not yet saved into the database.
#
# Revision 1.121  2004/09/15 18:47:58  jalet
# Re-Extends the list of invalid characters in names to prevent
# people from adding user "*" for example, or to prevent
# print administrators to hijack the system by putting dangerous
# datas into the database which would cause commands later run by root
# to compromise the system.
#
# Revision 1.120  2004/09/02 13:26:29  jalet
# Small fix for old versions of LPRng
#
# Revision 1.119  2004/09/02 13:09:58  jalet
# Now exports PYKOTAPRINTERHOSTNAME
#
# Revision 1.118  2004/08/06 20:46:45  jalet
# Finished group quota fix for balance when no user in group has a balance
#
# Revision 1.117  2004/08/06 13:45:51  jalet
# Fixed french translation problem.
# Fixed problem with group quotas and strict enforcement.
#
# Revision 1.116  2004/07/24 20:20:29  jalet
# Unitialized variable
#
# Revision 1.115  2004/07/21 09:35:48  jalet
# Software accounting seems to be OK with LPRng support now
#
# Revision 1.114  2004/07/20 22:19:45  jalet
# Sanitized a bit + use of gettext
#
# Revision 1.113  2004/07/17 20:37:27  jalet
# Missing file... Am I really stupid ?
#
# Revision 1.112  2004/07/16 12:22:47  jalet
# LPRng support early version
#
# Revision 1.111  2004/07/06 18:09:42  jalet
# Reduced the set of invalid characters in names
#
# Revision 1.110  2004/07/01 19:56:42  jalet
# Better dispatching of error messages
#
# Revision 1.109  2004/07/01 17:45:49  jalet
# Added code to handle the description field for printers
#
# Revision 1.108  2004/06/24 23:09:30  jalet
# Also prints read size on last block
#
# Revision 1.107  2004/06/23 13:03:28  jalet
# Catches accounter configuration errors earlier
#
# Revision 1.106  2004/06/22 09:31:18  jalet
# Always send some debug info to CUPS' back channel stream (stderr) as
# informationnal messages.
#
# Revision 1.105  2004/06/21 08:17:38  jalet
# Added version number in subject message for directive crashrecipient.
#
# Revision 1.104  2004/06/18 13:34:49  jalet
# Now all tracebacks include PyKota's version number
#
# Revision 1.103  2004/06/18 13:17:26  jalet
# Now includes PyKota's version number in messages sent by the crashrecipient
# directive.
#
# Revision 1.102  2004/06/17 13:26:51  jalet
# Better exception handling code
#
# Revision 1.101  2004/06/16 20:56:34  jalet
# Smarter initialisation code
#
# Revision 1.100  2004/06/11 08:16:03  jalet
# More exceptions catched in case of very early failure.
#
# Revision 1.99  2004/06/11 07:07:38  jalet
# Now detects and logs configuration syntax errors instead of failing without
# any notice message.
#
# Revision 1.98  2004/06/08 19:27:12  jalet
# Doesn't ignore SIGCHLD anymore
#
# Revision 1.97  2004/06/07 22:45:35  jalet
# Now accepts a job when enforcement is STRICT and predicted account balance
# is equal to 0.0 : since the job hasn't been printed yet, only its printing
# will really render balance equal to 0.0, so we should be allowed to print.
#
# Revision 1.96  2004/06/05 22:18:04  jalet
# Now catches some exceptions earlier.
# storage.py and ldapstorage.py : removed old comments
#
# Revision 1.95  2004/06/03 21:50:34  jalet
# Improved error logging.
# crashrecipient directive added.
# Now exports the job's size in bytes too.
#
# Revision 1.94  2004/06/03 08:51:03  jalet
# logs job's size in bytes now
#
# Revision 1.93  2004/06/02 21:51:02  jalet
# Moved the sigterm capturing elsewhere
#
# Revision 1.92  2004/06/02 13:21:38  jalet
# Debug message added
#
# Revision 1.91  2004/05/25 05:17:52  jalet
# Now precomputes the job's size only if current printer's enforcement
# is "STRICT"
#
# Revision 1.90  2004/05/24 22:45:49  jalet
# New 'enforcement' directive added
# Polling loop improvements
#
# Revision 1.89  2004/05/21 22:02:52  jalet
# Preliminary work on pre-accounting
#
# Revision 1.88  2004/05/18 14:49:20  jalet
# Big code changes to completely remove the need for "requester" directives,
# jsut use "hardware(... your previous requester directive's content ...)"
#
# Revision 1.87  2004/05/17 19:14:59  jalet
# Now catches SIGPIPE and SIGCHLD
#
# Revision 1.86  2004/05/13 13:59:28  jalet
# Code simplifications
#
# Revision 1.85  2004/05/11 08:26:27  jalet
# Now catches connection problems to SMTP server
#
# Revision 1.84  2004/04/21 08:36:32  jalet
# Exports the PYKOTASTATUS environment variable when SIGTERM is received.
#
# Revision 1.83  2004/04/16 17:03:49  jalet
# The list of printers groups the current printer is a member of is
# now exported in the PYKOTAPGROUPS environment variable
#
# Revision 1.82  2004/04/13 09:38:03  jalet
# More work on correct child processes handling
#
# Revision 1.81  2004/04/09 22:24:47  jalet
# Began work on correct handling of child processes when jobs are cancelled by
# the user. Especially important when an external requester is running for a
# long time.
#
# Revision 1.80  2004/04/06 12:00:21  jalet
# uninitialized values caused problems
#
# Revision 1.79  2004/03/28 21:01:29  jalet
# PYKOTALIMITBY environment variable is now exported too
#
# Revision 1.78  2004/03/08 20:13:25  jalet
# Allow names to begin with a digit
#
# Revision 1.77  2004/03/03 13:10:35  jalet
# Now catches all smtplib exceptions when there's a problem sending messages
#
# Revision 1.76  2004/03/01 14:34:15  jalet
# PYKOTAPHASE wasn't set at the right time at the end of data transmission
# to underlying layer (real backend)
#
# Revision 1.75  2004/03/01 11:23:25  jalet
# Pre and Post hooks to external commands are available in the cupspykota
# backend. Forthe pykota filter they will be implemented real soon now.
#
# Revision 1.74  2004/02/26 14:18:07  jalet
# Should fix the remaining bugs wrt printers groups and users groups.
#
# Revision 1.73  2004/02/19 14:20:21  jalet
# maildomain pykota.conf directive added.
# Small improvements on mail headers quality.
#
# Revision 1.72  2004/01/14 15:51:19  jalet
# Docstring added.
#
# Revision 1.71  2004/01/11 23:22:42  jalet
# Major code refactoring, it's way cleaner, and now allows automated addition
# of printers on first print.
#
# Revision 1.70  2004/01/08 14:10:32  jalet
# Copyright year changed.
#
# Revision 1.69  2004/01/05 16:02:18  jalet
# Dots in user, groups and printer names should be allowed.
#
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
import signal
import socket
import tempfile
import md5
import ConfigParser

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
    
def crashed(message) :    
    """Minimal crash method."""
    import traceback
    lines = []
    for line in traceback.format_exception(*sys.exc_info()) :
        lines.extend([l for l in line.split("\n") if l])
    msg = "ERROR: ".join(["%s\n" % l for l in (["ERROR: PyKota v%s" % version.__version__, message] + lines)])
    sys.stderr.write(msg)
    sys.stderr.flush()
    return msg

class PyKotaTool :    
    """Base class for all PyKota command line tools."""
    def __init__(self, lang="", charset=None, doc="PyKota %s (c) 2003-2004 %s" % (version.__version__, version.__author__)) :
        """Initializes the command line tool."""
        # locale stuff
        try :
            locale.setlocale(locale.LC_ALL, lang)
            gettext.install("pykota")
        except (locale.Error, IOError) :
            gettext.NullTranslations().install()
            
        # We can force the charset.    
        # The CHARSET environment variable is set by CUPS when printing.
        # Else we use the current locale's one.
        # If nothing is set, we use ISO-8859-15 widely used in western Europe.
        localecharset = locale.getlocale()[1]
        try :
            localecharset = localecharset or locale.getdefaultlocale()[1]
        except ValueError :    
            pass        # Unknown locale, strange...
        self.charset = charset or os.environ.get("CHARSET") or localecharset or "ISO-8859-15"
    
        # pykota specific stuff
        self.documentation = doc
        try :
            self.config = config.PyKotaConfig("/etc/pykota")
        except ConfigParser.ParsingError, msg :    
            sys.stderr.write("ERROR: Problem encountered while parsing configuration file : %s\n" % msg)
            sys.stderr.flush()
            sys.exit(-1)
            
        try :
            self.debug = self.config.getDebug()
            self.smtpserver = self.config.getSMTPServer()
            self.maildomain = self.config.getMailDomain()
            self.logger = logger.openLogger(self.config.getLoggingBackend())
            self.storage = storage.openConnection(self)
        except (config.PyKotaConfigError, logger.PyKotaLoggingError, storage.PyKotaStorageError), msg :
            self.crashed(msg)
            raise
        self.softwareJobSize = 0
        self.softwareJobPrice = 0.0
        self.logdebug("Charset in use : %s" % self.charset)
        
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
        print _(self.documentation) % (version.__version__, version.__author__)
        sys.exit(0)
        
    def crashed(self, message) :    
        """Outputs a crash message, and optionally sends it to software author."""
        msg = crashed(message)
        try :
            crashrecipient = self.config.getCrashRecipient()
            if crashrecipient :
                admin = self.config.getAdminMail("global") # Nice trick, isn't it ?
                fullmessage = "========== Traceback :\n\n%s\n\n========== sys.argv :\n\n%s\n\n========== Environment :\n\n%s\n" % \
                                (msg, \
                                 "\n".join(["    %s" % repr(a) for a in sys.argv]), \
                                 "\n".join(["    %s=%s" % (k, v) for (k, v) in os.environ.items()]))
                server = smtplib.SMTP(self.smtpserver)
                server.sendmail(admin, [admin, crashrecipient], \
                                       "From: %s\nTo: %s\nCc: %s\nSubject: PyKota v%s crash traceback !\n\n%s" % \
                                       (admin, crashrecipient, admin, version.__version__, fullmessage))
                server.quit()
        except :
            pass
        
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
    
    def isValidName(self, name) :
        """Checks if a user or printer name is valid."""
        invalidchars = "/@?*,;&|"
        for c in list(invalidchars) :
            if c in name :
                return 0
        return 1        
        
    def matchString(self, s, patterns) :
        """Returns 1 if the string s matches one of the patterns, else 0."""
        for pattern in patterns :
            if fnmatch.fnmatchcase(s, pattern) :
                return 1
        return 0
        
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
         
        arguments = " ".join(['"%s"' % arg for arg in sys.argv])
        self.logdebug(_("Printing system %s, args=%s") % (str(self.printingsystem), arguments))
        
        self.username = self.username or 'root' # when printing test page from CUPS web interface, username is empty
        
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
        os.environ["PYKOTAJOBSIZEBYTES"] = str(self.jobSizeBytes)
        self.logdebug("Job size is %s bytes" % self.jobSizeBytes)
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
            self.logdebug("Opening data stream %s" % self.preserveinputfile)
            self.jobSizeBytes = os.stat(self.preserveinputfile)[6]
            return open(self.preserveinputfile, "rb")
        
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
        os.environ["PYKOTALIMITBY"] = str(userpquota.User.LimitBy)
        os.environ["PYKOTABALANCE"] = str(userpquota.User.AccountBalance or 0.0)
        os.environ["PYKOTALIFETIMEPAID"] = str(userpquota.User.LifeTimePaid or 0.0)
        os.environ["PYKOTAPAGECOUNTER"] = str(userpquota.PageCounter or 0)
        os.environ["PYKOTALIFEPAGECOUNTER"] = str(userpquota.LifePageCounter or 0)
        os.environ["PYKOTASOFTLIMIT"] = str(userpquota.SoftLimit)
        os.environ["PYKOTAHARDLIMIT"] = str(userpquota.HardLimit)
        os.environ["PYKOTADATELIMIT"] = str(userpquota.DateLimit)
        
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
                self.printInfo(_("Printer hostname undefined, set to 'localhost'"), "warn")
                rseen = "localhost"
                
            spooldir = os.environ.get("SPOOL_DIR", ".")    
            try :    
                df_name = [line[8:] for line in os.environ.get("HF", "").split() if line.startswith("df_name=")][0]
            except IndexError :
                try :
                    cftransfername = [line[15:] for line in os.environ.get("HF", "").split() if line.startswith("cftransfername=")][0]
                except IndexError :    
                    try :
                        df_name = [line[1:] for line in os.environ.get("CONTROL", "").split() if line.startswith("fdf") or line.startswith("Udf")][0]
                    except IndexError :    
                        inputfile = None
                    else :    
                        inputfile = os.path.join(spooldir, df_name)
                else :    
                    inputfile = os.path.join(spooldir, "d" + cftransfername[1:])
            else :    
                inputfile = os.path.join(spooldir, df_name)
                
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
