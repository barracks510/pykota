# PyKota
#
# PyKota : Print Quotas for CUPS and LPRng
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
# Revision 1.3  2003/04/30 17:40:02  jalet
# I've got my assigned number for LDAP by the IANA.
#
# Revision 1.2  2003/04/27 08:27:34  jalet
# connection to LDAP backend
#
# Revision 1.1  2003/04/27 08:04:15  jalet
# LDAP storage backend's skeleton added. DOESN'T WORK.
#
#
#

#
# My IANA assigned number, for 
# "Conseil Internet & Logiciels Libres, Jérôme Alet" 
# is 16868. Use this as a base to create the LDAP schema.
#

import fnmatch

from pykota.storage import PyKotaStorageError

try :
    import ldap
except ImportError :    
    import sys
    # TODO : to translate or not to translate ?
    raise PyKotaStorageError, "This python version (%s) doesn't seem to have the python-ldap module installed correctly." % sys.version.split()[0]
    
class Storage :
    def __init__(self, host, dbname, user, passwd) :
        """Opens the LDAP connection."""
        raise PyKotaStorageError, "Sorry, the LDAP backend for PyKota is not yet implemented !"
        self.closed = 1
        try :
            self.database = ldap.initialize(host) 
            self.database.simple_bind_s(user, passwd)
            # TODO : dbname will be the base dn
        except ldap.SERVER_DOWN :    
            raise PyKotaStorageError, "LDAP backend for PyKota seems to be down !" # TODO : translate
        else :    
            self.closed = 0
            
    def __del__(self) :        
        """Closes the database connection."""
        if not self.closed :
            del self.database
            self.closed = 1
        
    def doQuery(self, query) :
        """Does a query."""
        pass
        
    def doQuote(self, field) :
        """Quotes a field for use as a string in LDAP queries."""
        pass
        
    def doParseResult(self, result) :
        """Returns the result as a list of Python mappings."""
        pass
        
    def getMatchingPrinters(self, printerpattern) :
        """Returns the list of all printers as tuples (id, name) for printer names which match a certain pattern."""
        pass
            
    def getPrinterId(self, printername) :        
        """Returns a printerid given a printername."""
        pass
            
    def getPrinterPrices(self, printerid) :        
        """Returns a printer prices per page and per job given a printerid."""
        pass
            
    def setPrinterPrices(self, printerid, perpage, perjob) :
        """Sets prices per job and per page for a given printer."""
        pass
    
    def getUserId(self, username) :
        """Returns a userid given a username."""
        pass
            
    def getGroupId(self, groupname) :
        """Returns a groupid given a grupname."""
        pass
            
    def getJobHistoryId(self, jobid, userid, printerid) :        
        """Returns the history line's id given a (jobid, userid, printerid)."""
        pass
            
    def getPrinterUsers(self, printerid) :        
        """Returns the list of usernames which uses a given printer."""
        pass
        
    def getPrinterGroups(self, printerid) :        
        """Returns the list of groups which uses a given printer."""
        pass
        
    def getGroupMembersNames(self, groupname) :        
        """Returns the list of user's names which are member of this group."""
        pass
        
    def getUserGroupsNames(self, userid) :        
        """Returns the list of groups' names the user is a member of."""
        pass
        
    def addPrinter(self, printername) :        
        """Adds a printer to the quota storage, returns its id."""
        pass
        
    def addUser(self, username) :        
        """Adds a user to the quota storage, returns its id."""
        pass
        
    def addGroup(self, groupname) :        
        """Adds a group to the quota storage, returns its id."""
        pass
        
    def addUserPQuota(self, username, printerid) :
        """Initializes a user print quota on a printer, adds the user to the quota storage if needed."""
        pass
        
    def addGroupPQuota(self, groupname, printerid) :
        """Initializes a group print quota on a printer, adds the group to the quota storage if needed."""
        pass
        
    def increaseUserBalance(self, userid, amount) :    
        """Increases (or decreases) an user's account balance by a given amount."""
        pass
        
    def getUserBalance(self, userid) :    
        """Returns the current account balance for a given user."""
        pass
        
    def getGroupBalance(self, groupid) :    
        """Returns the current account balance for a given group, as the sum of each of its users' account balance."""
        pass
        
    def getUserLimitBy(self, userid) :    
        """Returns the way in which user printing is limited."""
        pass
        
    def getGroupLimitBy(self, groupid) :    
        """Returns the way in which group printing is limited."""
        pass
        
    def setUserBalance(self, userid, balance) :    
        """Sets the account balance for a given user to a fixed value."""
        pass
        
    def limitUserBy(self, userid, limitby) :    
        """Limits a given user based either on print quota or on account balance."""
        pass
        
    def limitGroupBy(self, groupid, limitby) :    
        """Limits a given group based either on print quota or on sum of its users' account balances."""
        pass
        
    def setUserPQuota(self, userid, printerid, softlimit, hardlimit) :
        """Sets soft and hard limits for a user quota on a specific printer given (userid, printerid)."""
        pass
        
    def setGroupPQuota(self, groupid, printerid, softlimit, hardlimit) :
        """Sets soft and hard limits for a group quota on a specific printer given (groupid, printerid)."""
        pass
        
    def resetUserPQuota(self, userid, printerid) :    
        """Resets the page counter to zero for a user on a printer. Life time page counter is kept unchanged."""
        pass
        
    def resetGroupPQuota(self, groupid, printerid) :    
        """Resets the page counter to zero for a group on a printer. Life time page counter is kept unchanged."""
        pass
        
    def updateUserPQuota(self, userid, printerid, pagecount) :
        """Updates the used user Quota information given (userid, printerid) and a job size in pages."""
        pass
        
    def getUserPQuota(self, userid, printerid) :
        """Returns the Print Quota information for a given (userid, printerid)."""
        pass
        
    def getGroupPQuota(self, groupid, printerid) :
        """Returns the Print Quota information for a given (groupid, printerid)."""
        pass
        
    def setUserDateLimit(self, userid, printerid, datelimit) :
        """Sets the limit date for a soft limit to become an hard one given (userid, printerid)."""
        pass
        
    def setGroupDateLimit(self, groupid, printerid, datelimit) :
        """Sets the limit date for a soft limit to become an hard one given (groupid, printerid)."""
        pass
        
    def addJobToHistory(self, jobid, userid, printerid, pagecounter, action) :
        """Adds a job to the history: (jobid, userid, printerid, last page counter taken from requester)."""
        pass
    
    def updateJobSizeInHistory(self, historyid, jobsize) :
        """Updates a job size in the history given the history line's id."""
        pass
    
    def getPrinterPageCounter(self, printerid) :
        """Returns the last page counter value for a printer given its id, also returns last username, last jobid and history line id."""
        pass
        
    def addUserToGroup(self, userid, groupid) :    
        """Adds an user to a group."""
        pass
        
    def deleteUser(self, userid) :    
        """Completely deletes an user from the Quota Storage."""
        pass
        
    def deleteGroup(self, groupid) :    
        """Completely deletes an user from the Quota Storage."""
        pass
        
    def computePrinterJobPrice(self, printerid, jobsize) :    
        """Returns the price for a job on a given printer."""
        # TODO : create a base class with things like this
        prices = self.getPrinterPrices(printerid)
        if prices is None :
            perpage = perjob = 0.0
        else :    
            (perpage, perjob) = prices
        return perjob + (perpage * jobsize)
