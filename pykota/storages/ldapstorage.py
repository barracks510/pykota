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
# Revision 1.7  2003/06/14 22:44:21  jalet
# More work on LDAP storage backend.
#
# Revision 1.6  2003/06/13 19:07:57  jalet
# Two big bugs fixed, time to release something ;-)
#
# Revision 1.5  2003/06/10 16:37:54  jalet
# Deletion of the second user which is not needed anymore.
# Added a debug configuration field in /etc/pykota.conf
# All queries can now be sent to the logger in debug mode, this will
# greatly help improve performance when time for this will come.
#
# Revision 1.4  2003/06/10 10:45:32  jalet
# Not implemented methods now raise an exception when called.
#
# Revision 1.3  2003/06/06 20:49:15  jalet
# Very latest schema. UNTESTED.
#
# Revision 1.2  2003/06/06 14:21:08  jalet
# New LDAP schema.
# Small bug fixes.
#
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
    def __init__(self, pykotatool, host, dbname, user, passwd) :
        """Opens the LDAP connection."""
        # raise PyKotaStorageError, "Sorry, the LDAP backend for PyKota is not yet implemented !"
        self.closed = 1
        self.tool = pykotatool
        self.debug = pykotatool.config.getDebug()
        self.info = pykotatool.config.getLDAPInfo()
        try :
            self.database = ldap.initialize(host) 
            self.database.simple_bind_s(user, passwd)
            self.basedn = dbname
        except ldap.SERVER_DOWN :    
            raise PyKotaStorageError, "LDAP backend for PyKota seems to be down !" # TODO : translate
        else :    
            self.closed = 0
            if self.debug :
                self.tool.logger.log_message("Database opened (host=%s, dbname=%s, user=%s)" % (host, dbname, user), "debug")
            
    def __del__(self) :        
        """Closes the database connection."""
        if not self.closed :
            del self.database
            self.closed = 1
            if self.debug :
                self.tool.logger.log_message("Database closed.", "debug")
        
    def doSearch(self, key, fields, base="", scope=ldap.SCOPE_SUBTREE) :
        """Does an LDAP search query."""
        try :
            # prepends something more restrictive at the beginning of the base dn
            if self.debug :
                self.tool.logger.log_message("QUERY : BaseDN : %s, Scope : %s, Filter : %s, Attributes : %s" % ((base or self.basedn), scope, key, fields), "debug")
            result = self.database.search_s(base or self.basedn, scope, key, fields)
        except ldap.NO_SUCH_OBJECT :    
            return
        else :     
            return result
        
    def getMatchingPrinters(self, printerpattern) :
        """Returns the list of all printers as tuples (id, name) for printer names which match a certain pattern."""
        result = self.doSearch("objectClass=pykotaPrinter", ["pykotaPrinterName"], base=self.info["printerbase"])
        if result :
            return [(printerid, printer["pykotaPrinterName"][0]) for (printerid, printer) in result if fnmatch.fnmatchcase(printer["pykotaPrinterName"][0], printerpattern)]
            
    def getPrinterId(self, printername) :        
        """Returns a printerid given a printername."""
        result = self.doSearch("(&(objectClass=pykotaPrinter)(|(pykotaPrinterName=%s)(%s=%s)))" % (printername, self.info["printerrdn"], printername), ["pykotaPrinterName"], base=self.info["printerbase"])
        if result :
            return result[0][0]
            
    def getPrinterPrices(self, printerid) :        
        """Returns a printer prices per page and per job given a printerid."""
        result = self.doSearch("(|(pykotaPrinterName=*)(%s=*))" % self.info["printerrdn"], ["pykotaPricePerPage", "pykotaPricePerJob"], base=printerid, scope=ldap.SCOPE_BASE)
        if result :
            return (float(result[0][1]["pykotaPricePerPage"][0]), float(result[0][1]["pykotaPricePerJob"][0]))
            
    def setPrinterPrices(self, printerid, perpage, perjob) :
        """Sets prices per job and per page for a given printer."""
        raise PyKotaStorageError, "Not implemented !"
    
    def getUserId(self, username) :
        """Returns a userid given a username."""
        result = self.doSearch("(&(objectClass=pykotaAccount)(|(pykotaUserName=%s)(%s=%s)))" % (username, self.info["userrdn"], username), [self.info["userrdn"]], base=self.info["userbase"])
        if result :
            return result[0][0]
            
    def getGroupId(self, groupname) :
        """Returns a groupid given a grupname."""
        result = self.doSearch("(&(objectClass=pykotaGroup)(|(pykotaGroupName=%s)(%s=%s)))" % (groupname, self.info["grouprdn"], groupname), [self.info["grouprdn"]], base=self.info["groupbase"])
        if result is not None :
            (groupid, dummy) = result[0]
            return groupid
            
    def getJobHistoryId(self, jobid, userid, printerid) :        
        """Returns the history line's id given a (jobid, userid, printerid).
        
           TODO : delete because shouldn't be needed by the LDAP backend
        """
        raise PyKotaStorageError, "Not implemented !"
            
    def getPrinterUsers(self, printerid) :        
        """Returns the list of userids and usernames which uses a given printer."""
        # first get the printer's name from the id
        result = self.doSearch("objectClass=pykotaPrinter", ["pykotaPrinterName", self.info["printerrdn"]], base=printerid, scope=ldap.SCOPE_BASE)
        if result :
            fields = result[0][1]
            printername = (fields.get("pykotaPrinterName") or fields.get(self.info["printerrdn"]))[0]
            result = self.doSearch("(&(objectClass=pykotaUserPQuota)(pykotaPrinterName=%s))" % printername, ["pykotaUserName"], base=self.info["userquotabase"]) 
            if result :
                return [(pquotauserid, fields["pykotaUserName"][0]) for (pquotauserid, fields) in result]
        
    def getPrinterGroups(self, printerid) :        
        """Returns the list of groups which uses a given printer."""
        # first get the printer's name from the id
        result = self.doSearch("objectClass=pykotaPrinter", ["pykotaPrinterName", self.info["printerrdn"]], base=printerid, scope=ldap.SCOPE_BASE)
        if result :
            fields = result[0][1]
            printername = (fields.get("pykotaPrinterName") or fields.get(self.info["printerrdn"]))[0]
            result = self.doSearch("(&(objectClass=pykotaGroupPQuota)(pykotaPrinterName=%s))" % printername, ["pykotaGroupName"], base=self.info["groupquotabase"]) 
            if result :
                return [(pquotagroupid, fields["pykotaGroupName"][0]) for (pquotagroupid, fields) in result]
        
    def getGroupMembersNames(self, groupname) :        
        """Returns the list of user's names which are member of this group."""
        result = self.doSearch("(&(objectClass=pykotaGroup)(|(pykotaGroupName=%s)(%s=%s)))" % (groupname, self.info["grouprdn"], groupname), [self.info["groupmembers"]])
        if result :
            fields = result[0][1]
            return fields.get(self.info["groupmembers"])
        
    def getUserGroupsNames(self, userid) :        
        """Returns the list of groups' names the user is a member of."""
        raise PyKotaStorageError, "Not implemented !"
        
    def addPrinter(self, printername) :        
        """Adds a printer to the quota storage, returns its id."""
        raise PyKotaStorageError, "Not implemented !"
        
    def addUser(self, username) :        
        """Adds a user to the quota storage, returns its id."""
        raise PyKotaStorageError, "Not implemented !"
        
    def addGroup(self, groupname) :        
        """Adds a group to the quota storage, returns its id."""
        raise PyKotaStorageError, "Not implemented !"
        
    def addUserPQuota(self, username, printerid) :
        """Initializes a user print quota on a printer, adds the user to the quota storage if needed."""
        raise PyKotaStorageError, "Not implemented !"
        
    def addGroupPQuota(self, groupname, printerid) :
        """Initializes a group print quota on a printer, adds the group to the quota storage if needed."""
        raise PyKotaStorageError, "Not implemented !"
        
    def increaseUserBalance(self, userid, amount) :    
        """Increases (or decreases) an user's account balance by a given amount."""
        raise PyKotaStorageError, "Not implemented !"
        
    def getUserBalance(self, userquotaid) :    
        """Returns the current account balance for a given user quota identifier."""
        # first get the user's name from the user quota id
        result = self.doSearch("objectClass=pykotaUserPQuota", ["pykotaUserName"], base=userquotaid, scope=ldap.SCOPE_BASE)
        if result :
            username = result[0][1]["pykotaUserName"][0]
            result = self.doSearch("(&(objectClass=pykotaAccountBalance)(|(pykotaUserName=%s)(%s=%s)))" % (username, self.info["userrdn"], username), ["pykotaBalance", "pykotaLifeTimePaid"])
            if result :
                fields = result[0][1]
                return (float(fields["pykotaBalance"][0]), float(fields["pykotaLifeTimePaid"][0]))
        
    def getUserBalanceFromUserId(self, userid) :    
        """Returns the current account balance for a given user id."""
        # first get the user's name from the user id
        result = self.doSearch("objectClass=pykotaAccount", ["pykotaUserName", self.info["userrdn"]], base=userid, scope=ldap.SCOPE_BASE)
        if result :
            fields = result[0][1]
            username = (fields.get("pykotaUserName") or fields.get(self.info["userrdn"]))[0]
            result = self.doSearch("(&(objectClass=pykotaAccountBalance)(|(pykotaUserName=%s)(%s=%s)))" % (username, self.info["userrdn"], username), ["pykotaBalance", "pykotaLifeTimePaid"])
            if result :
                fields = result[0][1]
                return (float(fields["pykotaBalance"][0]), float(fields["pykotaLifeTimePaid"][0]))
        
    def getGroupBalance(self, groupquotaid) :    
        """Returns the current account balance for a given group, as the sum of each of its users' account balance."""
        # first get the group's name from the group quota id
        result = self.doSearch("objectClass=pykotaGroupPQuota", ["pykotaGroupName"], base=groupquotaid, scope=ldap.SCOPE_BASE)
        if result :
            groupname = result[0][1]["pykotaGroupName"][0]
            members = self.getGroupMembersNames(groupname)
            balance = lifetimepaid = 0.0
            for member in members :
                userid = self.getUserId(member)
                if userid :
                    userbal = self.getUserBalanceFromUserId(userid)
                    if userbal :
                        (bal, paid) = userbal
                        balance += bal
                        lifetimepaid += paid
            return (balance, lifetimepaid)            
        
    def getUserLimitBy(self, userquotaid) :    
        """Returns the way in which user printing is limited."""
        result = self.doSearch("objectClass=pykotaUserPQuota", ["pykotaUserName"], base=userquotaid, scope=ldap.SCOPE_BASE)
        if result :
            username = result[0][1]["pykotaUserName"][0]
            result = self.doSearch("(&(objectClass=pykotaAccount)(|(pykotaUserName=%s)(%s=%s)))" % (username, self.info["userrdn"], username), ["pykotaLimitBy"])
            if result :
                return result[0][1]["pykotaLimitBy"][0]
        
    def getGroupLimitBy(self, groupquotaid) :    
        """Returns the way in which group printing is limited."""
        # first get the group's name from the group quota id
        result = self.doSearch("objectClass=pykotaGroupPQuota", ["pykotaGroupName"], base=groupquotaid, scope=ldap.SCOPE_BASE)
        if result :
            groupname = result[0][1]["pykotaGroupName"][0]
            result = self.doSearch("(&(objectClass=pykotaGroup)(|(pykotaGroupName=%s)(%s=%s)))" % (groupname, self.info["grouprdn"], groupname), ["pykotaLimitBy"])
            if result :
                return result[0][1]["pykotaLimitBy"][0]
        
    def setUserBalance(self, userid, balance) :    
        """Sets the account balance for a given user to a fixed value."""
        raise PyKotaStorageError, "Not implemented !"
        
    def limitUserBy(self, userid, limitby) :    
        """Limits a given user based either on print quota or on account balance."""
        raise PyKotaStorageError, "Not implemented !"
        
    def limitGroupBy(self, groupid, limitby) :    
        """Limits a given group based either on print quota or on sum of its users' account balances."""
        raise PyKotaStorageError, "Not implemented !"
        
    def setUserPQuota(self, userid, printerid, softlimit, hardlimit) :
        """Sets soft and hard limits for a user quota on a specific printer given (userid, printerid)."""
        raise PyKotaStorageError, "Not implemented !"
        
    def setGroupPQuota(self, groupid, printerid, softlimit, hardlimit) :
        """Sets soft and hard limits for a group quota on a specific printer given (groupid, printerid)."""
        raise PyKotaStorageError, "Not implemented !"
        
    def resetUserPQuota(self, userid, printerid) :    
        """Resets the page counter to zero for a user on a printer. Life time page counter is kept unchanged."""
        raise PyKotaStorageError, "Not implemented !"
        
    def resetGroupPQuota(self, groupid, printerid) :    
        """Resets the page counter to zero for a group on a printer. Life time page counter is kept unchanged."""
        raise PyKotaStorageError, "Not implemented !"
        
    def updateUserPQuota(self, userid, printerid, pagecount) :
        """Updates the used user Quota information given (userid, printerid) and a job size in pages."""
        raise PyKotaStorageError, "Not implemented !"
        
    def getUserPQuota(self, userquotaid, printerid) :
        """Returns the Print Quota information for a given (userquotaid, printerid)."""
        # first get the user's name from the id
        result = self.doSearch("objectClass=pykotaUserPQuota", ["pykotaUserName", "pykotaPageCounter", "pykotaLifePageCounter", "pykotaSoftLimit", "pykotaHardLimit", "pykotaDateLimit"], base=userquotaid, scope=ldap.SCOPE_BASE)
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
        
    def getGroupPQuota(self, grouppquotaid, printerid) :
        """Returns the Print Quota information for a given (grouppquotaid, printerid)."""
        result = self.doSearch("objectClass=pykotaGroupPQuota", ["pykotaGroupName", "pykotaSoftLimit", "pykotaHardLimit", "pykotaDateLimit"], base=grouppquotaid, scope=ldap.SCOPE_BASE)
        if result :
            fields = result[0][1]
            groupname = fields["pykotaGroupName"][0]
            datelimit = fields["pykotaDateLimit"][0].strip()
            if (not datelimit) or (datelimit.upper() == "NONE") : 
                datelimit = None
            quota = {
                      "softlimit" : int(fields["pykotaSoftLimit"][0]),
                      "hardlimit" : int(fields["pykotaHardLimit"][0]),
                      "datelimit" : datelimit
                    }
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
        
    def setUserDateLimit(self, userid, printerid, datelimit) :
        """Sets the limit date for a soft limit to become an hard one given (userid, printerid)."""
        raise PyKotaStorageError, "Not implemented !"
        
    def setGroupDateLimit(self, groupid, printerid, datelimit) :
        """Sets the limit date for a soft limit to become an hard one given (groupid, printerid)."""
        raise PyKotaStorageError, "Not implemented !"
        
    def addJobToHistory(self, jobid, userid, printerid, pagecounter, action) :
        """Adds a job to the history: (jobid, userid, printerid, last page counter taken from requester)."""
        raise PyKotaStorageError, "Not implemented !"
    
    def updateJobSizeInHistory(self, historyid, jobsize) :
        """Updates a job size in the history given the history line's id."""
        raise PyKotaStorageError, "Not implemented !"
    
    def getPrinterPageCounter(self, printerid) :
        """Returns the last page counter value for a printer given its id, also returns last username, last jobid and history line id."""
        result = self.doSearch("objectClass=pykotaPrinter", ["pykotaPrinterName", self.info["printerrdn"]], base=printerid, scope=ldap.SCOPE_BASE)
        if result :
            fields = result[0][1]
            printername = (fields.get("pykotaPrinterName") or fields.get(self.info["printerrdn"]))[0]
            result = self.doSearch("(&(objectClass=pykotaLastjob)(|(pykotaPrinterName=%s)(%s=%s)))" % (printername, self.info["printerrdn"], printername), ["pykotaLastJobIdent"], base=self.info["lastjobbase"])
            if result :
                lastjobident = result[0][1]["pykotaLastJobIdent"][0]
                result = self.doSearch("(&(objectClass=pykotaJob)(cn=%s))" % lastjobident, ["pykotaUserName", "pykotaPrinterName", "pykotaJobId", "pykotaPrinterPageCounter", "pykotaJobSize", "pykotaAction", "createTimestamp"], base=self.info["jobbase"])
                if result :
                    fields = result[0][1]
                    return { "id": lastjobident, 
                             "jobid" : fields.get("pykotaJobId")[0],
                             "userid" : self.getUserId(fields.get("pykotaUserName")[0]),
                             "username" : fields.get("pykotaUserName")[0], 
                             "pagecounter" : int(fields.get("pykotaPrinterPageCounter")[0]),
                           }
        
    def addUserToGroup(self, userid, groupid) :    
        """Adds an user to a group."""
        raise PyKotaStorageError, "Not implemented !"
        
    def deleteUser(self, userid) :    
        """Completely deletes an user from the Quota Storage."""
        raise PyKotaStorageError, "Not implemented !"
        
    def deleteGroup(self, groupid) :    
        """Completely deletes an user from the Quota Storage."""
        raise PyKotaStorageError, "Not implemented !"
        
    def computePrinterJobPrice(self, printerid, jobsize) :    
        """Returns the price for a job on a given printer."""
        # TODO : create a base class with things like this
        prices = self.getPrinterPrices(printerid)
        if prices is None :
            perpage = perjob = 0.0
        else :    
            (perpage, perjob) = prices
        return perjob + (perpage * jobsize)
