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
# Revision 1.1  2003/06/05 11:19:13  jalet
# More good work on LDAP storage.
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
        # raise PyKotaStorageError, "Sorry, the LDAP backend for PyKota is not yet implemented !"
        self.closed = 1
        try :
            self.database = ldap.initialize(host) 
            self.database.simple_bind_s(user, passwd)
            self.basedn = dbname
        except ldap.SERVER_DOWN :    
            raise PyKotaStorageError, "LDAP backend for PyKota seems to be down !" # TODO : translate
        else :    
            self.closed = 0
            
    def __del__(self) :        
        """Closes the database connection."""
        if not self.closed :
            del self.database
            self.closed = 1
        
    def doSearch(self, key, fields, base="") :
        """Does an LDAP search query."""
        try :
            # prepends something more restrictive at the beginning of the base dn
            result = self.database.search_s(base or self.basedn, ldap.SCOPE_SUBTREE, key, fields)
        except ldap.NO_SUCH_OBJECT :    
            return
        else :     
            return result
        
    def getMatchingPrinters(self, printerpattern) :
        """Returns the list of all printers as tuples (id, name) for printer names which match a certain pattern."""
        result = self.doSearch("objectClass=pykotaPrinter", ["pykotaPrinterName"])
        if result :
            return [(printerid, printer["pykotaPrinterName"][0]) for (printerid, printer) in result if fnmatch.fnmatchcase(printer["pykotaPrinterName"][0], printerpattern)]
        else :    
            return
            
    def getPrinterId(self, printername) :        
        """Returns a printerid given a printername."""
        result = self.doSearch("(&(objectClass=pykotaPrinter)(pykotaPrinterName=%s))" % printername, ["pykotaPrinterName"])
        if result :
            return result[0][0]
        else :    
            return
            
    def getPrinterPrices(self, printerid) :        
        """Returns a printer prices per page and per job given a printerid."""
        result = self.doSearch("pykotaPrinterName=*", ["pykotaPricePerPage", "pykotaPricePerJob"], base=printerid)
        if result :
            return (float(result[0][1]["pykotaPricePerPage"][0]), float(result[0][1]["pykotaPricePerJob"][0]))
        else :
            return 
            
    def setPrinterPrices(self, printerid, perpage, perjob) :
        """Sets prices per job and per page for a given printer."""
        pass
    
    def getUserId(self, username) :
        """Returns a userid given a username."""
        result = self.doSearch("(&(objectClass=pykotaUser)(uid=%s))" % username, ["uid"])
        if result :
            return result[0][0]
        else :    
            return
            
    def getGroupId(self, groupname) :
        """Returns a groupid given a grupname."""
        result = self.doSearch("(&(objectClass=pykotaGroup)(cn=%s))" % groupname, ["cn"])
        if result is not None :
            (groupid, dummy) = result[0]
            return groupid
            
    def getJobHistoryId(self, jobid, userid, printerid) :        
        """Returns the history line's id given a (jobid, userid, printerid)."""
        pass
            
    def getPrinterUsers(self, printerid) :        
        """Returns the list of userids and usernames which uses a given printer."""
        result = self.doSearch("(&(objectClass=pykotaUserPQuota)(uid=*))", ["uid"], base=printerid) 
        if result :
            return [(pquotauserid, fields["uid"][0]) for (pquotauserid, fields) in result]
        else :
            return
        
    def getPrinterGroups(self, printerid) :        
        """Returns the list of groups which uses a given printer."""
        result = self.doSearch("(&(objectClass=pykotaGroupPQuota)(cn=*))", ["cn"], base=printerid) 
        if result :
            return [(pquotagroupid, fields["cn"][0]) for (pquotagroupid, fields) in result]
        else :
            return
        
    def getGroupMembersNames(self, groupname) :        
        """Returns the list of user's names which are member of this group."""
        result = self.doSearch("(&(objectClass=pykotaGroup)(cn=%s))" % groupname, ["memberUid"])
        if result :
            return result[0][1]["memberUid"]
        else :
            return
        
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
        shortuid = userid.split(",")[0]
        result = self.doSearch("(&(objectClass=pykotaUser)(%s))" % shortuid, ["pykotaBalance", "pykotaLifeTimePaid"])
        if result :
            fields = result[0][1]
            return (float(fields["pykotaBalance"][0]), float(fields["pykotaLifeTimePaid"][0]))
        else :    
            return
        
    def getGroupBalance(self, groupid) :    
        """Returns the current account balance for a given group, as the sum of each of its users' account balance."""
        groupname = groupid.split(",")[0].split("=")[1]
        members = self.getGroupMembersNames(groupname)
        balance = lifetimepaid = 0.0
        for member in members :
            userid = self.getUserId(member)
            if userid :
                userbal = self.getUserBalance(userid)
                if userbal :
                    (bal, paid) = userbal
                    balance += bal
                    lifetimepaid += paid
        return (balance, lifetimepaid)            
        
    def getUserLimitBy(self, userid) :    
        """Returns the way in which user printing is limited."""
        shortuid = userid.split(",")[0]
        result = self.doSearch("(&(objectClass=pykotaUser)(%s))" % shortuid, ["pykotaLimitBy"])
        if result :
            return result[0][1]["pykotaLimitBy"][0]
        else :    
            return
        
    def getGroupLimitBy(self, groupid) :    
        """Returns the way in which group printing is limited."""
        shortgid = groupid.split(",")[0]
        result = self.doSearch("(&(objectClass=pykotaGroup)(%s))" % shortgid, ["pykotaLimitBy"])
        if result :
            return result[0][1]["pykotaLimitBy"][0]
        else :    
            return
        
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
        result = self.doSearch("(&(objectClass=pykotaUserPQuota)(uid=*))", ["uid", "pykotaPageCounter", "pykotaLifePageCounter", "pykotaSoftLimit", "pykotaHardLimit", "pykotaDateLimit"], base=userid)
        if result :
            fields = result[0][1]
            datelimit = fields["pykotaDateLimit"][0].strip()
            if (not datelimit) or (datelimit.upper() == "NONE") : 
                datelimit = None
            return { "lifepagecounter" : int(fields["pykotaLifePageCounter"][0]), 
                     "pagecounter" : int(fields["pykotaPageCounter"][0]),
                     "softlimit" : int(fields["pykotaSoftLimit"][0]),
                     "hardlimit" : int(fields["pykotaHardLimit"][0]),
                     "datelimit" : datelimit
                   }
        else :
            return
        
    def getGroupPQuota(self, groupid, printerid) :
        """Returns the Print Quota information for a given (groupid, printerid)."""
        result = self.doSearch("(&(objectClass=pykotaGroupPQuota)(cn=*))", ["pykotaSoftLimit", "pykotaHardLimit", "pykotaDateLimit"], base=groupid)
        if result :
            fields = result[0][1]
            datelimit = fields["pykotaDateLimit"][0].strip()
            if (not datelimit) or (datelimit.upper() == "NONE") : 
                datelimit = None
            quota = {
                      "softlimit" : int(fields["pykotaSoftLimit"][0]),
                      "hardlimit" : int(fields["pykotaHardLimit"][0]),
                      "datelimit" : datelimit
                    }
            groupname = groupid.split(",")[0].split("=")[1]
            members = self.getGroupMembersNames(groupname)
            pagecounter = lifepagecounter = 0
            printerusers = self.getPrinterUsers(printerid)
            if printerusers :
                for (userid, username) in printerusers :
                    if username in members :
                        userpquota = self.getUserPQuota(userid, printerid)
                        if userpquota :
                            pagecounter += userpquota["pagecounter"]
                            lifepagecounter += userpquota["lifepagecounter"]
            quota.update({"pagecounter": pagecounter, "lifepagecounter": lifepagecounter})                
            return quota
        else :
            return
        
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
        return # TODO
        result = self.doSearch("objectClass=pykotaPrinterJob", ["pykotaJobHistoryId", "pykotaJobId", "uid", "pykotaPrinterPageCounter", "pykotaJobSize", "pykotaAction", "pykotaJobDate"], base=printerid)
        if result :
            pass # TODO
        else :
            return 
        
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
