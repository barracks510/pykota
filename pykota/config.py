# PyKota
# -*- coding: ISO-8859-15 -*-
#
# PyKota : Print Quotas for CUPS and LPRng
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
# Revision 1.62  2005/02/19 18:16:06  jalet
# Optimize print job parsing by avoiding to pass the job's datas through
# PyKota's internal parser if the special construct "software()" is used
# with no argument in the 'accounter' directive.
#
# Revision 1.61  2005/02/16 00:29:33  jalet
# Fixed the maxdenybanners directive.
# Introduced the denyduplicates directive.
# Fixed some database related glitches.
#
# Revision 1.60  2005/02/14 23:39:50  jalet
# Introduces the new 'trustjobsize' directive to workaround some printers
# generating unstable internal page counter values when queried through SNMP.
#
# Revision 1.59  2005/02/13 22:02:29  jalet
# Big database structure changes. Upgrade script is now included as well as
# the new LDAP schema.
# Introduction of the -o | --overcharge command line option to edpykota.
# The output of repykota is more complete, but doesn't fit in 80 columns anymore.
# Introduction of the new 'maxdenybanners' directive.
#
# Revision 1.58  2004/12/02 22:01:58  jalet
# TLS is now supported with the LDAP backend
#
# Revision 1.57  2004/11/22 21:53:38  jalet
# Added the reject_unknown directive to pykota.conf to reject user/group
# creation if user or group is unknown to the system
#
# Revision 1.56  2004/11/15 15:23:07  jalet
# Strips spaces just in case
#
# Revision 1.55  2004/11/15 15:14:06  jalet
# Preliminary integration of Matt's patch for banners.
#
# Revision 1.54  2004/10/25 14:12:25  jalet
# For URGENT legal reasons (Italy), a new "privacy" directive was added to pykota.conf
# to hide print jobs' title, filename, and options.
#
# Revision 1.53  2004/10/06 10:05:47  jalet
# Minor changes to allow any PyKota administrator to launch enhanced versions
# of the commands, and not only the root user.
#
# Revision 1.52  2004/09/29 20:20:52  jalet
# Added the winbind_separator directive to pykota.conf to allow the admin to
# strip out the Samba/Winbind domain name when users print.
#
# Revision 1.51  2004/08/31 23:29:53  jalet
# Introduction of the new 'onaccountererror' configuration directive.
# Small fix for software accounter's return code which can't be None anymore.
# Make software and hardware accounting code look similar : will be factorized
# later.
#
# Revision 1.50  2004/07/27 07:07:27  jalet
# Typo : treshold ==> threshold
#
# Revision 1.49  2004/06/03 21:53:24  jalet
# crashrecipient directive
#
# Revision 1.48  2004/05/24 22:45:49  jalet
# New 'enforcement' directive added
# Polling loop improvements
#
# Revision 1.47  2004/05/18 14:49:20  jalet
# Big code changes to completely remove the need for "requester" directives,
# jsut use "hardware(... your previous requester directive's content ...)"
#
# Revision 1.46  2004/05/13 13:59:28  jalet
# Code simplifications
#
# Revision 1.45  2004/03/01 10:22:30  jalet
# Can now extract per printer pre and post hooks from the configuration file
#
# Revision 1.44  2004/02/20 14:42:21  jalet
# Experimental ldapcache directive added
#
# Revision 1.43  2004/02/19 14:20:21  jalet
# maildomain pykota.conf directive added.
# Small improvements on mail headers quality.
#
# Revision 1.42  2004/01/08 14:10:32  jalet
# Copyright year changed.
#
# Revision 1.41  2003/11/29 20:06:20  jalet
# Added 'utolower' configuration option to convert all usernames to
# lowercase when printing. All database accesses are still and will
# remain case sensitive though.
#
# Revision 1.40  2003/11/18 23:43:12  jalet
# Mailto can be any external command now, as usual.
#
# Revision 1.39  2003/10/08 21:41:38  jalet
# External policies for printers works !
# We can now auto-add users on first print, and do other useful things if needed.
#
# Revision 1.38  2003/10/07 22:06:05  jalet
# Preliminary code to disable job history
#
# Revision 1.37  2003/10/07 09:07:28  jalet
# Character encoding added to please latest version of Python
#
# Revision 1.36  2003/10/02 20:23:18  jalet
# Storage caching mechanism added.
#
# Revision 1.35  2003/07/29 09:54:03  jalet
# Added configurable LDAP mail attribute support
#
# Revision 1.34  2003/07/28 09:11:12  jalet
# PyKota now tries to add its attributes intelligently in existing LDAP
# directories.
#
# Revision 1.33  2003/07/16 21:53:07  jalet
# Really big modifications wrt new configuration file's location and content.
#
# Revision 1.32  2003/07/08 19:43:51  jalet
# Configurable warning messages.
# Poor man's treshold value added.
#
# Revision 1.31  2003/07/07 11:49:24  jalet
# Lots of small fixes with the help of PyChecker
#
# Revision 1.30  2003/06/25 14:10:01  jalet
# Hey, it may work (edpykota --reset excepted) !
#
# Revision 1.29  2003/06/14 22:44:21  jalet
# More work on LDAP storage backend.
#
# Revision 1.28  2003/06/10 16:37:54  jalet
# Deletion of the second user which is not needed anymore.
# Added a debug configuration field in /etc/pykota.conf
# All queries can now be sent to the logger in debug mode, this will
# greatly help improve performance when time for this will come.
#
# Revision 1.27  2003/05/27 23:00:21  jalet
# Big rewrite of external accounting methods.
# Should work well now.
#
# Revision 1.26  2003/04/30 19:53:58  jalet
# 1.05
#
# Revision 1.25  2003/04/30 13:36:40  jalet
# Stupid accounting method was added.
#
# Revision 1.24  2003/04/29 18:37:54  jalet
# Pluggable accounting methods (actually doesn't support external scripts)
#
# Revision 1.23  2003/04/24 11:53:48  jalet
# Default policy for unknown users/groups is to DENY printing instead
# of the previous default to ALLOW printing. This is to solve an accuracy
# problem. If you set the policy to ALLOW, jobs printed by in nexistant user
# (from PyKota's POV) will be charged to the next user who prints on the
# same printer.
#
# Revision 1.22  2003/04/23 22:13:57  jalet
# Preliminary support for LPRng added BUT STILL UNTESTED.
#
# Revision 1.21  2003/03/29 13:45:27  jalet
# GPL paragraphs were incorrectly (from memory) copied into the sources.
# Two README files were added.
# Upgrade script for PostgreSQL pre 1.01 schema was added.
#
# Revision 1.20  2003/03/29 13:08:28  jalet
# Configuration is now expected to be found in /etc/pykota.conf instead of
# in /etc/cups/pykota.conf
# Installation script can move old config files to the new location if needed.
# Better error handling if configuration file is absent.
#
# Revision 1.19  2003/03/16 09:56:52  jalet
# Mailto option now accepts some additional values which all mean that
# nobody will receive any email message.
# Mailto option now works. Version 1.01 is now officially out.
#
# Revision 1.18  2003/03/16 08:00:50  jalet
# Default hard coded options are now used if they are not set in the
# configuration file.
#
# Revision 1.17  2003/03/15 23:01:28  jalet
# New mailto option in configuration file added.
# No time to test this tonight (although it should work).
#
# Revision 1.16  2003/02/17 23:01:56  jalet
# Typos
#
# Revision 1.15  2003/02/17 22:55:01  jalet
# More options can now be set per printer or globally :
#
#       admin
#       adminmail
#       gracedelay
#       requester
#
# the printer option has priority when both are defined.
#
# Revision 1.14  2003/02/17 22:05:50  jalet
# Storage backend now supports admin and user passwords (untested)
#
# Revision 1.13  2003/02/10 11:47:39  jalet
# Moved some code down into the requesters
#
# Revision 1.12  2003/02/10 10:36:33  jalet
# Small problem wrt external requester
#
# Revision 1.11  2003/02/10 08:50:45  jalet
# External requester seems to be finally ok now
#
# Revision 1.10  2003/02/10 08:19:57  jalet
# tell ConfigParser to return raw data, this allows our own strings
# interpolations in the requester
#
# Revision 1.9  2003/02/10 00:44:38  jalet
# Typos
#
# Revision 1.8  2003/02/10 00:42:17  jalet
# External requester should be ok (untested)
# New syntax for configuration file wrt requesters
#
# Revision 1.7  2003/02/09 13:05:43  jalet
# Internationalization continues...
#
# Revision 1.6  2003/02/07 22:00:09  jalet
# Bad cut&paste
#
# Revision 1.5  2003/02/06 23:58:05  jalet
# repykota should be ok
#
# Revision 1.4  2003/02/06 09:19:02  jalet
# More robust behavior (hopefully) when the user or printer is not managed
# correctly by the Quota System : e.g. cupsFilter added in ppd file, but
# printer and/or user not 'yet?' in storage.
#
# Revision 1.3  2003/02/05 23:26:22  jalet
# Incorrect handling of grace delay
#
# Revision 1.2  2003/02/05 23:09:20  jalet
# Name conflict
#
# Revision 1.1  2003/02/05 21:28:17  jalet
# Initial import into CVS
#
#
#

import os
import ConfigParser

class PyKotaConfigError(Exception):
    """An exception for PyKota config related stuff."""
    def __init__(self, message = ""):
        self.message = message
        Exception.__init__(self, message)
    def __repr__(self):
        return self.message
    __str__ = __repr__
    
class PyKotaConfig :
    """A class to deal with PyKota's configuration."""
    def __init__(self, directory) :
        """Reads and checks the configuration file."""
        self.isAdmin = 0
        self.directory = directory
        self.filename = os.path.join(directory, "pykota.conf")
        if not os.path.isfile(self.filename) :
            raise PyKotaConfigError, _("Configuration file %s not found.") % self.filename
        self.config = ConfigParser.ConfigParser()
        self.config.read([self.filename])
            
    def isTrue(self, option) :        
        """Returns 1 if option is set to true, else 0."""
        if (option is not None) and (option.upper().strip() in ['Y', 'YES', '1', 'ON', 'T', 'TRUE']) :
            return 1
        else :    
            return 0
                        
    def getPrinterNames(self) :    
        """Returns the list of configured printers, i.e. all sections names minus 'global'."""
        return [pname for pname in self.config.sections() if pname != "global"]
        
    def getGlobalOption(self, option, ignore=0) :    
        """Returns an option from the global section, or raises a PyKotaConfigError if ignore is not set, else returns None."""
        try :
            return self.config.get("global", option, raw=1)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) :    
            if ignore :
                return
            else :
                raise PyKotaConfigError, _("Option %s not found in section global of %s") % (option, self.filename)
                
    def getPrinterOption(self, printername, option) :    
        """Returns an option from the printer section, or the global section, or raises a PyKotaConfigError."""
        globaloption = self.getGlobalOption(option, ignore=1)
        try :
            return self.config.get(printername, option, raw=1)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) :    
            if globaloption is not None :
                return globaloption
            else :
                raise PyKotaConfigError, _("Option %s not found in section %s of %s") % (option, printername, self.filename)
        
    def getStorageBackend(self) :    
        """Returns the storage backend information as a Python mapping."""        
        backendinfo = {}
        for option in [ "storagebackend", "storageserver", \
                        "storagename", "storageuser", \
                      ] :
            backendinfo[option] = self.getGlobalOption(option)
        backendinfo["storageuserpw"] = self.getGlobalOption("storageuserpw", ignore=1)  # password is optional
        backendinfo["storageadmin"] = None
        backendinfo["storageadminpw"] = None
        adminconf = ConfigParser.ConfigParser()
        filename = os.path.join(self.directory, "pykotadmin.conf")
        adminconf.read([filename])
        if adminconf.sections() : # were we able to read the file ?
            try :
                backendinfo["storageadmin"] = adminconf.get("global", "storageadmin", raw=1)
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) :    
                raise PyKotaConfigError, _("Option %s not found in section global of %s") % ("storageadmin", filename)
            else :    
                self.isAdmin = 1 # We are a PyKota administrator
            try :
                backendinfo["storageadminpw"] = adminconf.get("global", "storageadminpw", raw=1)
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) :    
                pass # Password is optional
        return backendinfo
        
    def getLDAPInfo(self) :    
        """Returns some hints for the LDAP backend."""        
        ldapinfo = {}
        for option in [ "userbase", "userrdn", \
                        "balancebase", "balancerdn", \
                        "groupbase", "grouprdn", "groupmembers", \
                        "printerbase", "printerrdn", \
                        "userquotabase", "groupquotabase", \
                        "jobbase", "lastjobbase", \
                        "newuser", "newgroup", \
                        "usermail", \
                      ] :
            ldapinfo[option] = self.getGlobalOption(option).strip()
        for field in ["newuser", "newgroup"] :
            if ldapinfo[field].lower().startswith('attach(') :
                ldapinfo[field] = ldapinfo[field][7:-1]
                
        # should we use TLS, by default (if unset) value is NO        
        ldapinfo["ldaptls"] = self.isTrue(self.getGlobalOption("ldaptls", ignore=1))
        ldapinfo["cacert"] = self.getGlobalOption("cacert", ignore=1)
        if ldapinfo["cacert"] :
            ldapinfo["cacert"] = ldapinfo["cacert"].strip()
        if ldapinfo["ldaptls"] :    
            if not os.access(ldapinfo["cacert"] or "", os.R_OK) :
                raise PyKotaConfigError, _("Option ldaptls is set, but certificate %s is not readable.") % str(ldapinfo["cacert"])
        return ldapinfo
        
    def getLoggingBackend(self) :    
        """Returns the logging backend information."""
        validloggers = [ "stderr", "system" ] 
        try :
            logger = self.getGlobalOption("logger").lower()
        except PyKotaConfigError :    
            logger = "system"
        if logger not in validloggers :             
            raise PyKotaConfigError, _("Option logger only supports values in %s") % str(validloggers)
        return logger    
        
    def getAccounterBackend(self, printername) :    
        """Returns the accounter backend to use for a given printer.
        
           if it is not set, it defaults to 'hardware' which means ask printer
           for its internal lifetime page counter.
        """   
        validaccounters = [ "hardware", "software" ]     
        fullaccounter = self.getPrinterOption(printername, "accounter").strip()
        flower = fullaccounter.lower()
        if flower.startswith("software") or flower.startswith("hardware") :    
            try :
                (accounter, args) = [x.strip() for x in fullaccounter.split('(', 1)]
            except ValueError :    
                raise PyKotaConfigError, _("Invalid accounter %s for printer %s") % (fullaccounter, printername)
            if args.endswith(')') :
                args = args[:-1].strip()
            if (accounter == "hardware") and not args :
                raise PyKotaConfigError, _("Invalid accounter %s for printer %s") % (fullaccounter, printername)
            return (accounter.lower(), args)    
        else :
            raise PyKotaConfigError, _("Option accounter in section %s only supports values in %s") % (printername, str(validaccounters))
        
    def getPreHook(self, printername) :    
        """Returns the prehook command line to launch, or None if unset."""
        try :
            return self.getPrinterOption(printername, "prehook").strip()
        except PyKotaConfigError :    
            return      # No command to launch in the pre-hook
            
    def getPostHook(self, printername) :    
        """Returns the posthook command line to launch, or None if unset."""
        try :
            return self.getPrinterOption(printername, "posthook").strip()
        except PyKotaConfigError :    
            return      # No command to launch in the post-hook
            
    def getPrinterEnforcement(self, printername) :    
        """Returns if quota enforcement should be strict or laxist for the current printer."""
        validenforcements = [ "STRICT", "LAXIST" ]     
        try :
            enforcement = self.getPrinterOption(printername, "enforcement")
        except PyKotaConfigError :    
            return "LAXIST"
        else :    
            enforcement = enforcement.upper()
            if enforcement not in validenforcements :
                raise PyKotaConfigError, _("Option enforcement in section %s only supports values in %s") % (printername, str(validenforcements))
            return enforcement    
            
    def getPrinterOnAccounterError(self, printername) :    
        """Returns what must be done whenever the accounter fails."""
        validactions = [ "CONTINUE", "STOP" ]     
        try :
            action = self.getPrinterOption(printername, "onaccountererror")
        except PyKotaConfigError :    
            return "STOP"
        else :    
            action = action.upper()
            if action not in validactions :
                raise PyKotaConfigError, _("Option onaccountererror in section %s only supports values in %s") % (printername, str(validactions))
            return action  
            
    def getPrinterPolicy(self, printername) :    
        """Returns the default policy for the current printer."""
        validpolicies = [ "ALLOW", "DENY", "EXTERNAL" ]     
        try :
            fullpolicy = self.getPrinterOption(printername, "policy")
        except PyKotaConfigError :    
            return ("DENY", None)
        else :    
            try :
                policy = [x.strip() for x in fullpolicy.split('(', 1)]
            except ValueError :    
                raise PyKotaConfigError, _("Invalid policy %s for printer %s") % (fullpolicy, printername)
            if len(policy) == 1 :    
                policy.append("")
            (policy, args) = policy    
            if args.endswith(')') :
                args = args[:-1]
            policy = policy.upper()    
            if (policy == "EXTERNAL") and not args :
                raise PyKotaConfigError, _("Invalid policy %s for printer %s") % (fullpolicy, printername)
            if policy not in validpolicies :
                raise PyKotaConfigError, _("Option policy in section %s only supports values in %s") % (printername, str(validpolicies))
            return (policy, args)
        
    def getCrashRecipient(self) :    
        """Returns the email address of the software crash messages recipient."""
        try :
            return self.getGlobalOption("crashrecipient")
        except :    
            return
            
    def getSMTPServer(self) :    
        """Returns the SMTP server to use to send messages to users."""
        try :
            return self.getGlobalOption("smtpserver")
        except PyKotaConfigError :    
            return "localhost"
        
    def getMailDomain(self) :    
        """Returns the mail domain to use to send messages to users."""
        try :
            return self.getGlobalOption("maildomain")
        except PyKotaConfigError :    
            return 
        
    def getAdminMail(self, printername) :    
        """Returns the Email address of the Print Quota Administrator."""
        try :
            return self.getPrinterOption(printername, "adminmail")
        except PyKotaConfigError :    
            return "root@localhost"
        
    def getAdmin(self, printername) :    
        """Returns the full name of the Print Quota Administrator."""
        try :
            return self.getPrinterOption(printername, "admin")
        except PyKotaConfigError :    
            return "root"
        
    def getMailTo(self, printername) :    
        """Returns the recipient of email messages."""
        validmailtos = [ "EXTERNAL", "NOBODY", "NONE", "NOONE", "BITBUCKET", "DEVNULL", "BOTH", "USER", "ADMIN" ]
        try :
            fullmailto = self.getPrinterOption(printername, "mailto")
        except PyKotaConfigError :    
            return ("BOTH", None)
        else :    
            try :
                mailto = [x.strip() for x in fullmailto.split('(', 1)]
            except ValueError :    
                raise PyKotaConfigError, _("Invalid option mailto %s for printer %s") % (fullmailto, printername)
            if len(mailto) == 1 :    
                mailto.append("")
            (mailto, args) = mailto    
            if args.endswith(')') :
                args = args[:-1]
            mailto = mailto.upper()    
            if (mailto == "EXTERNAL") and not args :
                raise PyKotaConfigError, _("Invalid option mailto %s for printer %s") % (fullmailto, printername)
            if mailto not in validmailtos :
                raise PyKotaConfigError, _("Option mailto in section %s only supports values in %s") % (printername, str(validmailtos))
            return (mailto, args)
        
    def getMaxDenyBanners(self, printername) :    
        """Returns the maximum number of deny banners to be printed for a particular user on a particular printer."""
        try :
            maxdb = self.getPrinterOption(printername, "maxdenybanners")
        except PyKotaConfigError :    
            return 0 # default value is to forbid printing a deny banner.
        try :
            value = int(maxdb.strip())
            if value < 0 :
                raise ValueError
        except (TypeError, ValueError) :    
            raise PyKotaConfigError, _("Invalid maximal deny banners counter %s") % maxdb
        else :    
            return value
            
    def getGraceDelay(self, printername) :    
        """Returns the grace delay in days."""
        try :
            gd = self.getPrinterOption(printername, "gracedelay")
        except PyKotaConfigError :    
            gd = 7      # default value of 7 days
        try :
            return int(gd)
        except (TypeError, ValueError) :    
            raise PyKotaConfigError, _("Invalid grace delay %s") % gd
            
    def getPoorMan(self) :    
        """Returns the poor man's threshold."""
        try :
            pm = self.getGlobalOption("poorman")
        except PyKotaConfigError :    
            pm = 1.0    # default value of 1 unit
        try :
            return float(pm)
        except (TypeError, ValueError) :    
            raise PyKotaConfigError, _("Invalid poor man's threshold %s") % pm
            
    def getPoorWarn(self) :    
        """Returns the poor man's warning message."""
        try :
            return self.getGlobalOption("poorwarn")
        except PyKotaConfigError :    
            return _("Your Print Quota account balance is Low.\nSoon you'll not be allowed to print anymore.\nPlease contact the Print Quota Administrator to solve the problem.")
            
    def getHardWarn(self, printername) :    
        """Returns the hard limit error message."""
        try :
            return self.getPrinterOption(printername, "hardwarn")
        except PyKotaConfigError :    
            return _("You are not allowed to print anymore because\nyour Print Quota is exceeded on printer %s.") % printername
            
    def getSoftWarn(self, printername) :    
        """Returns the soft limit error message."""
        try :
            return self.getPrinterOption(printername, "softwarn")
        except PyKotaConfigError :    
            return _("You will soon be forbidden to print anymore because\nyour Print Quota is almost reached on printer %s.") % printername
            
    def getPrivacy(self) :        
        """Returns 1 if privacy is activated, else 0."""
        return self.isTrue(self.getGlobalOption("privacy", ignore=1))
        
    def getDebug(self) :          
        """Returns 1 if debugging is activated, else 0."""
        return self.isTrue(self.getGlobalOption("debug", ignore=1))
            
    def getCaching(self) :          
        """Returns 1 if database caching is enabled, else 0."""
        return self.isTrue(self.getGlobalOption("storagecaching", ignore=1))
            
    def getLDAPCache(self) :          
        """Returns 1 if low-level LDAP caching is enabled, else 0."""
        return self.isTrue(self.getGlobalOption("ldapcache", ignore=1))
            
    def getDisableHistory(self) :          
        """Returns 1 if we want to disable history, else 0."""
        return self.isTrue(self.getGlobalOption("disablehistory", ignore=1))
            
    def getUserNameToLower(self) :          
        """Returns 1 if we want to convert usernames to lowercase when printing, else 0."""
        return self.isTrue(self.getGlobalOption("utolower", ignore=1))
        
    def getRejectUnknown(self) :          
        """Returns 1 if we want to reject the creation of unknown users or groups, else 0."""
        return self.isTrue(self.getGlobalOption("reject_unknown", ignore=1))
        
    def getDenyDuplicates(self, printername) :          
        """Returns 1 if we want to deny duplicate jobs, else 0."""
        try : 
            return self.isTrue(self.getPrinterOption(printername, "denyduplicates"))
        except PyKotaConfigError :    
            return 0
        
    def getWinbindSeparator(self) :          
        """Returns the winbind separator's value if it is set, else None."""
        return self.getGlobalOption("winbind_separator", ignore=1)

    def getAccountBanner(self, printername) :
        """Returns which banner(s) to account for: NONE, BOTH, STARTING, ENDING."""
        validvalues = [ "NONE", "BOTH", "STARTING", "ENDING" ]     
        try :
            value = self.getPrinterOption(printername, "accountbanner")
        except PyKotaConfigError :    
            return "BOTH"       # Default value of BOTH
        else :    
            value = value.strip().upper()
            if value not in validvalues :
                raise PyKotaConfigError, _("Option accountbanner in section %s only supports values in %s") % (printername, str(validvalues))
            return value  

    def getStartingBanner(self, printername) :
        """Returns the startingbanner value if set, else None."""
        try :
            return self.getPrinterOption(printername, "startingbanner").strip()
        except PyKotaConfigError :
            return None

    def getEndingBanner(self, printername) :
        """Returns the endingbanner value if set, else None."""
        try :
            return self.getPrinterOption(printername, "endingbanner").strip()
        except PyKotaConfigError :
            return None
            
    def getTrustJobSize(self, printername) :
        """Returns the normalized value of the trustjobsize's directive."""
        try :
            value = self.getPrinterOption(printername, "trustjobsize").strip().upper()
        except PyKotaConfigError :
            return (None, "YES")
        else :    
            if value == "YES" :
                return (None, "YES")
            try :    
                (limit, replacement) = [p.strip() for p in value.split(">")[1].split(":")]
                limit = int(limit)
                try :
                    replacement = int(replacement) 
                except ValueError :    
                    if replacement != "PRECOMPUTED" :
                        raise
                if limit < 0 :
                    raise ValueError
                if (replacement != "PRECOMPUTED") and (replacement < 0) :
                    raise ValueError
            except (IndexError, ValueError, TypeError) :
                raise PyKotaConfigError, _("Option trustjobsize for printer %s is incorrect") % printername
            return (limit, replacement)    
