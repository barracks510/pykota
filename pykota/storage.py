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
# Revision 1.9  2003/02/17 22:55:01  jalet
# More options can now be set per printer or globally :
#
# 	admin
# 	adminmail
# 	gracedelay
# 	requester
#
# the printer option has priority when both are defined.
#
# Revision 1.8  2003/02/17 22:05:50  jalet
# Storage backend now supports admin and user passwords (untested)
#
# Revision 1.7  2003/02/10 12:07:31  jalet
# Now repykota should output the recorded total page number for each printer too.
#
# Revision 1.6  2003/02/09 13:05:43  jalet
# Internationalization continues...
#
# Revision 1.5  2003/02/08 22:39:46  jalet
# --reset command line option added
#
# Revision 1.4  2003/02/08 09:59:59  jalet
# Added preliminary base class for all storages
#
# Revision 1.3  2003/02/05 22:10:29  jalet
# Typos
#
# Revision 1.2  2003/02/05 22:02:22  jalet
# __import__ statement didn't work as expected
#
# Revision 1.1  2003/02/05 21:28:17  jalet
# Initial import into CVS
#
#
#

class PyKotaStorageError(Exception):
    """An exception for Quota Storage related stuff."""
    def __init__(self, message = ""):
        self.message = message
        Exception.__init__(self, message)
    def __repr__(self):
        return self.message
    __str__ = __repr__
    
class BaseStorage :    
    """Base class for all storages."""
    def getMatchingPrinters(self, printerpattern) :
        """Returns the list of all printers tuples (name, pagecounter) which match a certain pattern for the printer name."""
        pass
            
    def addPrinter(self, printername) :        
        """Adds a printer to the quota storage."""
        pass
        
    def getPrinterUsers(self, printername) :        
        """Returns the list of usernames which uses a given printer."""
        pass
        
    def getPrinterGroups(self, printername) :        
        """Returns the list of groups which uses a given printer."""
        pass
        
    def getPrinterPageCounter(self, printername) :
        """Returns the last page counter value for a printer given its name."""
        pass
        
    def updatePrinterPageCounter(self, printername, username, pagecount) :
        """Updates the last page counter information for a printer given its name, last username and pagecount."""
        pass
        
    def addUserPQuota(self, username, printername) :
        """Initializes a user print quota on a printer, adds the printer and the user to the quota storage if needed."""
        pass
        
    def getUPIds(self, username, printername) :    
        """Returns a tuple (userid, printerid) given a username and a printername."""
        pass
        
    def getUserPQuota(self, username, printername) :
        """Returns the Print Quota information for a given (username, printername)."""
        pass
        
    def setUserPQuota(self, username, printername, softlimit, hardlimit) :
        """Sets soft and hard limits for a user quota on a specific printer given (username, printername)."""
        pass
        
    def resetUserPQuota(self, username, printername) :    
        """Resets the page counter to zero. Life time page counter is kept unchanged."""
        pass
        
    def setDateLimit(self, username, printername, datelimit) :
        """Sets the limit date for a soft limit to become an hard one given (username, printername)."""
        pass
        
    def updateUserPQuota(self, username, printername, pagecount) :
        """Updates the used user Quota information given (username, printername) and a job size in pages."""
        pass
        
    def buyUserPQuota(self, username, printername, pagebought) :
        """Buys pages for a given (username, printername)."""
        pass
        
def openConnection(config, asadmin=0) :
    """Returns a connection handle to the appropriate Quota Storage Database."""
    backendinfo = config.getStorageBackend()
    backend = backendinfo["storagebackend"]
    try :
        if not backend.isalpha() :
            # don't trust user input
            raise ImportError
        exec "from pykota.storages import %s as storagebackend" % backend.lower()    
    except ImportError :
        raise PyKotaStorageError, _("Unsupported quota storage backend %s") % backend
    else :    
        host = backendinfo["storageserver"]
        database = backendinfo["storagename"]
        admin = backendinfo["storageadmin"]
        user = backendinfo["storageuser"]
        adminpw = backendinfo["storageadminpw"]
        userpw = backendinfo["storageuserpw"]
        if asadmin :
            return getattr(storagebackend, "Storage")(host, database, admin, adminpw)
        else :    
            return getattr(storagebackend, "Storage")(host, database, user, userpw)

