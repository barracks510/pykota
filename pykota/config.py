# PyKota
#
# PyKota : Print Quotas for CUPS
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

import sys
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
        self.filename = os.path.join(directory, "pykota.conf")
        self.config = ConfigParser.ConfigParser()
        self.config.read([self.filename])
        self.checkConfiguration()
        
    def checkConfiguration(self) :
        """Checks if configuration is correct.
        
           raises PyKotaConfigError in case a problem is detected
        """
        for option in [ "storagebackend", "storageserver", \
                        "storagename", "storageadmin", \
                        "storageuser", # TODO : "storageadminpw", "storageusepw", \
                        "logger", "admin", "adminmail",
                        "smtpserver", "method", "gracedelay" ] :
            if not self.config.has_option("global", option) :            
                raise PyKotaConfigError, "Option %s not found in section global of %s" % (option, self.filename)
                
        # more precise checks        
        validloggers = [ "stderr", "system" ] 
        if self.config.get("global", "logger").lower() not in validloggers :             
            raise PyKotaConfigError, "Option logger only supports values in %s" % str(validloggers)
            
        validmethods = [ "lazy" ] # TODO add more methods            
        if self.config.get("global", "method").lower() not in validmethods :             
            raise PyKotaConfigError, "Option method only supports values in %s" % str(validmethods)
            
        # check all printers now 
        for printer in self.getPrinterNames() :
            for poption in [ "requester", "policy" ] : 
                if not self.config.has_option(printer, poption) :
                    raise PyKotaConfigError, "Option %s not found in section %s of %s" % (option, printer, self.filename)
                    
            validpolicies = [ "ALLOW", "DENY" ]     
            if self.config.get(printer, "policy").upper() not in validpolicies :
                raise PyKotaConfigError, "Option policy in section %s only supports values in %s" % (printer, str(validrequesters))
            
            validrequesters = [ "snmp" ] # TODO : add more requesters
            requester = self.config.get(printer, "requester").lower()
            if requester not in validrequesters :
                raise PyKotaConfigError, "Option requester in section %s only supports values in %s" % (printer, str(validrequesters))
            if requester == "snmp" :
                for poption in [ "snmpcmnty", "snmpoid" ] : 
                    if not self.config.has_option(printer, poption) :
                        raise PyKotaConfigError, "Option %s not found in section %s of %s" % (option, printer, self.filename)
                        
    def getPrinterNames(self) :    
        """Returns the list of configured printers, i.e. all sections names minus 'global'."""
        return [pname for pname in self.config.sections() if pname != "global"]
        
    def getStorageBackend(self) :    
        """Returns the storage backend information as a tuple.
        
           The tuple has the form :
           
             (backend, host, database, admin, user)
        """        
        backendinfo = []
        for option in [ "storagebackend", "storageserver", \
                        "storagename", "storageadmin", \
                        "storageuser", # TODO : "storageadminpw", "storageusepw", \
                      ] :
            backendinfo.append(self.config.get("global", option))
        return tuple(backendinfo)    
        
    def getLoggingBackend(self) :    
        """Returns the logging backend information."""
        return self.config.get("global", "logger").lower()
        
    def getRequesterBackend(self, printer) :    
        """Returns the requester backend to use for a given printer."""
        return self.config.get(printer, "requester").lower()
        
    def getPrinterPolicy(self, printer) :    
        """Returns the default policy for the current printer."""
        return self.config.get(printer, "policy").upper()
        
    def getSMTPServer(self) :    
        """Returns the SMTP server to use to send messages to users."""
        return self.config.get("global", "smtpserver").lower()
        
    def getAdminMail(self) :    
        """Returns the Email address of the Print Quota Administrator."""
        return self.config.get("global", "adminmail")
        
    def getAdmin(self) :    
        """Returns the full name of the Print Quota Administrator."""
        return self.config.get("global", "admin")
        
    def getGraceDelay(self) :    
        """Returns the grace delay in days."""
        gd = self.config.get("global", "gracedelay")
        try :
            return int(gd)
        except ValueError :    
            raise PyKotaConfigError, "Invalid grace delay %s" % gd
