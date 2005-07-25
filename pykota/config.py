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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# $Id$
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
        if (option is not None) and (option.strip().upper() in ['Y', 'YES', '1', 'ON', 'T', 'TRUE']) :
            return 1
        else :    
            return 0
                        
    def isFalse(self, option) :        
        """Returns 1 if option is set to false, else 0."""
        if (option is not None) and (option.strip().upper() in ['N', 'NO', '0', 'OFF', 'F', 'FALSE']) :
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
                        "jobbase", "lastjobbase", "billingcodebase", \
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
        
    def getLogoURL(self) :
        """Returns the URL to use for the logo in the CGI scripts."""
        url = self.getGlobalOption("logourl", ignore=1) or \
                   "http://www.librelogiciel.com/software/PyKota/pykota.png"
        return url.strip()           
        
    def getLogoLink(self) :
        """Returns the URL to go to when the user clicks on the logo in the CGI scripts."""
        url = self.getGlobalOption("logolink", ignore=1) or \
                   "http://www.librelogiciel.com/software/"
        return url.strip()           
    
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
            
    def getStripTitle(self, printername) :    
        """Returns the striptitle directive's content, or None if unset."""
        try :
            return self.getPrinterOption(printername, "striptitle").strip()
        except PyKotaConfigError :    
            return      # No prefix to strip off
            
    def getOverwriteJobTicket(self, printername) :        
        """Returns the overwrite_jobticket directive's content, or None if unset."""
        try :
            return self.getPrinterOption(printername, "overwrite_jobticket").strip()
        except PyKotaConfigError :    
            return      # No overwriting will be done
        
    def getUnknownBillingCode(self, printername) :        
        """Returns the unknown_billingcode directive's content, or the default value if unset."""
        validvalues = [ "CREATE", "DENY" ]
        try :
            fullvalue = self.getPrinterOption(printername, "unknown_billingcode")
        except PyKotaConfigError :    
            return ("CREATE", None)
        else :    
            try :
                value = [x.strip() for x in fullvalue.split('(', 1)]
            except ValueError :    
                raise PyKotaConfigError, _("Invalid unknown_billingcode directive %s for printer %s") % (fullvalue, printername)
            if len(value) == 1 :    
                value.append("")
            (value, args) = value    
            if args.endswith(')') :
                args = args[:-1]
            value = value.upper()    
            if (value == "DENY") and not args :
                return ("DENY", None)
            if value not in validvalues :
                raise PyKotaConfigError, _("Directive unknown_billingcode in section %s only supports values in %s") % (printername, str(validvalues))
            return (value, args)
        
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
        """Returns 1 or a command if we want to deny duplicate jobs, else 0."""
        try : 
            denyduplicates = self.getPrinterOption(printername, "denyduplicates")
        except PyKotaConfigError :    
            return 0
        else :    
            if self.isTrue(denyduplicates) :
                return 1
            elif self.isFalse(denyduplicates) :
                return 0
            else :    
                # it's a command to run.
                return denyduplicates
        
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
