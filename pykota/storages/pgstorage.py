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
# Revision 1.2  2003/06/12 21:09:57  jalet
# wrongly placed code.
#
# Revision 1.1  2003/06/10 16:37:54  jalet
# Deletion of the second user which is not needed anymore.
# Added a debug configuration field in /etc/pykota.conf
# All queries can now be sent to the logger in debug mode, this will
# greatly help improve performance when time for this will come.
#
#
#
#

import fnmatch

from pykota.storage import PyKotaStorageError

try :
    import pg
except ImportError :    
    import sys
    # TODO : to translate or not to translate ?
    raise PyKotaStorageError, "This python version (%s) doesn't seem to have the PygreSQL module installed correctly." % sys.version.split()[0]

class Storage :
    def __init__(self, pykotatool, host, dbname, user, passwd) :
        """Opens the PostgreSQL database connection."""
        self.tool = pykotatool
        self.debug = pykotatool.config.getDebug()
        self.closed = 1
        try :
            (host, port) = host.split(":")
            port = int(port)
        except ValueError :    
            port = -1         # Use PostgreSQL's default tcp/ip port (5432).
        
        try :
            self.database = pg.connect(host=host, port=port, dbname=dbname, user=user, passwd=passwd)
        except pg.error, msg :
            raise PyKotaStorageError, msg
        else :    
            self.closed = 0
            if self.debug :
                self.tool.logger.log_message("Database opened (host=%s, port=%s, dbname=%s, user=%s)" % (host, port, dbname, user), "debug")
            
    def __del__(self) :        
        """Closes the database connection."""
        if not self.closed :
            self.database.close()
            self.closed = 1
            if self.debug :
                self.tool.logger.log_message("Database closed.", "debug")
        
    def doQuery(self, query) :
        """Does a query."""
        if type(query) in (type([]), type(())) :
            query = ";".join(query)
        query = query.strip()    
        if not query.endswith(';') :    
            query += ';'
        self.database.query("BEGIN;")
        if self.debug :
            self.tool.logger.log_message("Transaction began.", "debug")
        try :
            if self.debug :
                self.tool.logger.log_message("QUERY : %s" % query, "debug")
            result = self.database.query(query)
        except pg.error, msg :    
            self.database.query("ROLLBACK;")
            if self.debug :
                self.tool.logger.log_message("Transaction aborted.", "debug")
            raise PyKotaStorageError, msg
        else :    
            self.database.query("COMMIT;")
            if self.debug :
                self.tool.logger.log_message("Transaction committed.", "debug")
            return result
        
    def doQuote(self, field) :
        """Quotes a field for use as a string in SQL queries."""
        if type(field) == type(0.0) : 
            typ = "decimal"
        elif type(field) == type(0) :    
            typ = "int"
        else :    
            typ = "text"
        return pg._quote(field, typ)
        
    def doParseResult(self, result) :
        """Returns the result as a list of Python mappings."""
        if (result is not None) and (result.ntuples() > 0) :
            return result.dictresult()
            
    def getMatchingPrinters(self, printerpattern) :
        """Returns the list of all printers as tuples (id, name) for printer names which match a certain pattern."""
        printerslist = []
        # We 'could' do a SELECT printername FROM printers WHERE printername LIKE ...
        # but we don't because other storages semantics may be different, so every
        # storage should use fnmatch to match patterns and be storage agnostic
        result = self.doQuery("SELECT id, printername FROM printers")
        result = self.doParseResult(result)
        if result is not None :
            for printer in result :
                if fnmatch.fnmatchcase(printer["printername"], printerpattern) :
                    printerslist.append((printer["id"], printer["printername"]))
        return printerslist        
            
    def getPrinterId(self, printername) :        
        """Returns a printerid given a printername."""
        result = self.doQuery("SELECT id FROM printers WHERE printername=%s" % self.doQuote(printername))
        try :
            return self.doParseResult(result)[0]["id"]
        except TypeError :      # Not found    
            return
            
    def getPrinterPrices(self, printerid) :        
        """Returns a printer prices per page and per job given a printerid."""
        result = self.doQuery("SELECT priceperpage, priceperjob FROM printers WHERE id=%s" % self.doQuote(printerid))
        try :
            printerprices = self.doParseResult(result)[0]
            return (printerprices["priceperpage"], printerprices["priceperjob"])
        except TypeError :      # Not found    
            return
            
    def setPrinterPrices(self, printerid, perpage, perjob) :
        """Sets prices per job and per page for a given printer."""
        self.doQuery("UPDATE printers SET priceperpage=%s, priceperjob=%s WHERE id=%s" % (self.doQuote(perpage), self.doQuote(perjob), self.doQuote(printerid)))
    
    def getUserId(self, username) :
        """Returns a userid given a username."""
        result = self.doQuery("SELECT id FROM users WHERE username=%s" % self.doQuote(username))
        try :
            return self.doParseResult(result)[0]["id"]
        except TypeError :      # Not found
            return
            
    def getGroupId(self, groupname) :
        """Returns a groupid given a grupname."""
        result = self.doQuery("SELECT id FROM groups WHERE groupname=%s" % self.doQuote(groupname))
        try :
            return self.doParseResult(result)[0]["id"]
        except TypeError :      # Not found
            return
            
    def getJobHistoryId(self, jobid, userid, printerid) :        
        """Returns the history line's id given a (jobid, userid, printerid)."""
        result = self.doQuery("SELECT id FROM jobhistory WHERE jobid=%s AND userid=%s AND printerid=%s" % (self.doQuote(jobid), self.doQuote(userid), self.doQuote(printerid)))
        try :
            return self.doParseResult(result)[0]["id"]
        except TypeError :      # Not found    
            return
            
    def getPrinterUsers(self, printerid) :        
        """Returns the list of userids and usernames which uses a given printer."""
        result = self.doQuery("SELECT DISTINCT id, username FROM users WHERE id IN (SELECT userid FROM userpquota WHERE printerid=%s) ORDER BY username" % self.doQuote(printerid))
        result = self.doParseResult(result)
        if result is None :
            return []
        else :    
            return [(record["id"], record["username"]) for record in result]
        
    def getPrinterGroups(self, printerid) :        
        """Returns the list of groups which uses a given printer."""
        result = self.doQuery("SELECT DISTINCT id, groupname FROM groups WHERE id IN (SELECT groupid FROM grouppquota WHERE printerid=%s)" % self.doQuote(printerid))
        result = self.doParseResult(result)
        if result is None :
            return []
        else :    
            return [(record["id"], record["groupname"]) for record in result]
        
    def getGroupMembersNames(self, groupname) :        
        """Returns the list of user's names which are member of this group."""
        groupid = self.getGroupId(groupname)
        if groupid is None :
            return []
        else :
            result = self.doQuery("SELECT DISTINCT username FROM users WHERE id IN (SELECT userid FROM groupsmembers WHERE groupid=%s)" % self.doQuote(groupid))
            return [record["username"] for record in (self.doParseResult(result) or [])]
        
    def getUserGroupsNames(self, userid) :        
        """Returns the list of groups' names the user is a member of."""
        result = self.doQuery("SELECT DISTINCT groupname FROM groups WHERE id IN (SELECT groupid FROM groupsmembers WHERE userid=%s)" % self.doQuote(userid))
        return [record["groupname"] for record in (self.doParseResult(result) or [])]
        
    def addPrinter(self, printername) :        
        """Adds a printer to the quota storage, returns its id."""
        self.doQuery("INSERT INTO printers (printername) VALUES (%s)" % self.doQuote(printername))
        return self.getPrinterId(printername)
        
    def addUser(self, username) :        
        """Adds a user to the quota storage, returns its id."""
        self.doQuery("INSERT INTO users (username) VALUES (%s)" % self.doQuote(username))
        return self.getUserId(username)
        
    def addGroup(self, groupname) :        
        """Adds a group to the quota storage, returns its id."""
        self.doQuery("INSERT INTO groups (groupname) VALUES (%s)" % self.doQuote(groupname))
        return self.getGroupId(groupname)
        
    def addUserPQuota(self, username, printerid) :
        """Initializes a user print quota on a printer, adds the user to the quota storage if needed."""
        userid = self.getUserId(username)     
        if userid is None :    
            userid = self.addUser(username)
        uqexists = (self.getUserPQuota(userid, printerid) is not None)    
        if not uqexists : 
            self.doQuery("INSERT INTO userpquota (userid, printerid) VALUES (%s, %s)" % (self.doQuote(userid), self.doQuote(printerid)))
        return (userid, printerid)
        
    def addGroupPQuota(self, groupname, printerid) :
        """Initializes a group print quota on a printer, adds the group to the quota storage if needed."""
        groupid = self.getGroupId(groupname)     
        if groupid is None :    
            groupid = self.addGroup(groupname)
        gqexists = (self.getGroupPQuota(groupid, printerid) is not None)    
        if not gqexists : 
            self.doQuery("INSERT INTO grouppquota (groupid, printerid) VALUES (%s, %s)" % (self.doQuote(groupid), self.doQuote(printerid)))
        return (groupid, printerid)
        
    def increaseUserBalance(self, userid, amount) :    
        """Increases (or decreases) an user's account balance by a given amount."""
        self.doQuery("UPDATE users SET balance=balance+(%s), lifetimepaid=lifetimepaid+(%s) WHERE id=%s" % (self.doQuote(amount), self.doQuote(amount), self.doQuote(userid)))
        
    def getUserBalance(self, userid) :    
        """Returns the current account balance for a given user."""
        result = self.doQuery("SELECT balance, lifetimepaid FROM users WHERE id=%s" % self.doQuote(userid))
        try :
            result = self.doParseResult(result)[0]
        except TypeError :      # Not found    
            return
        else :    
            return (result["balance"], result["lifetimepaid"])
        
    def getGroupBalance(self, groupid) :    
        """Returns the current account balance for a given group, as the sum of each of its users' account balance."""
        result = self.doQuery("SELECT SUM(balance) AS balance, SUM(lifetimepaid) AS lifetimepaid FROM users WHERE id in (SELECT userid FROM groupsmembers WHERE groupid=%s)" % self.doQuote(groupid))
        try :
            result = self.doParseResult(result)[0]
        except TypeError :      # Not found    
            return
        else :    
            return (result["balance"], result["lifetimepaid"])
        
    def getUserLimitBy(self, userid) :    
        """Returns the way in which user printing is limited."""
        result = self.doQuery("SELECT limitby FROM users WHERE id=%s" % self.doQuote(userid))
        try :
            return self.doParseResult(result)[0]["limitby"]
        except TypeError :      # Not found    
            return
        
    def getGroupLimitBy(self, groupid) :    
        """Returns the way in which group printing is limited."""
        result = self.doQuery("SELECT limitby FROM groups WHERE id=%s" % self.doQuote(groupid))
        try :
            return self.doParseResult(result)[0]["limitby"]
        except TypeError :      # Not found    
            return
        
    def setUserBalance(self, userid, balance) :    
        """Sets the account balance for a given user to a fixed value."""
        (current, lifetimepaid) = self.getUserBalance(userid)
        difference = balance - current
        self.increaseUserBalance(userid, difference)
        
    def limitUserBy(self, userid, limitby) :    
        """Limits a given user based either on print quota or on account balance."""
        self.doQuery("UPDATE users SET limitby=%s WHERE id=%s" % (self.doQuote(limitby), self.doQuote(userid)))
        
    def limitGroupBy(self, groupid, limitby) :    
        """Limits a given group based either on print quota or on sum of its users' account balances."""
        self.doQuery("UPDATE groups SET limitby=%s WHERE id=%s" % (self.doQuote(limitby), self.doQuote(groupid)))
        
    def setUserPQuota(self, userid, printerid, softlimit, hardlimit) :
        """Sets soft and hard limits for a user quota on a specific printer given (userid, printerid)."""
        self.doQuery("UPDATE userpquota SET softlimit=%s, hardlimit=%s, datelimit=NULL WHERE userid=%s AND printerid=%s" % (self.doQuote(softlimit), self.doQuote(hardlimit), self.doQuote(userid), self.doQuote(printerid)))
        
    def setGroupPQuota(self, groupid, printerid, softlimit, hardlimit) :
        """Sets soft and hard limits for a group quota on a specific printer given (groupid, printerid)."""
        self.doQuery("UPDATE grouppquota SET softlimit=%s, hardlimit=%s, datelimit=NULL WHERE groupid=%s AND printerid=%s" % (self.doQuote(softlimit), self.doQuote(hardlimit), self.doQuote(groupid), self.doQuote(printerid)))
        
    def resetUserPQuota(self, userid, printerid) :    
        """Resets the page counter to zero for a user on a printer. Life time page counter is kept unchanged."""
        self.doQuery("UPDATE userpquota SET pagecounter=0, datelimit=NULL WHERE userid=%s AND printerid=%s" % (self.doQuote(userid), self.doQuote(printerid)))
        
    def resetGroupPQuota(self, groupid, printerid) :    
        """Resets the page counter to zero for a group on a printer. Life time page counter is kept unchanged."""
        self.doQuery("UPDATE grouppquota SET pagecounter=0, datelimit=NULL WHERE groupid=%s AND printerid=%s" % (self.doQuote(groupid), self.doQuote(printerid)))
        
    def updateUserPQuota(self, userid, printerid, pagecount) :
        """Updates the used user Quota information given (userid, printerid) and a job size in pages."""
        jobprice = self.computePrinterJobPrice(printerid, pagecount)
        queries = []    
        queries.append("UPDATE userpquota SET lifepagecounter=lifepagecounter+(%s), pagecounter=pagecounter+(%s) WHERE userid=%s AND printerid=%s" % (self.doQuote(pagecount), self.doQuote(pagecount), self.doQuote(userid), self.doQuote(printerid)))
        queries.append("UPDATE users SET balance=balance-(%s) WHERE id=%s" % (self.doQuote(jobprice), self.doQuote(userid)))
        self.doQuery(queries)
        
    def getUserPQuota(self, userid, printerid) :
        """Returns the Print Quota information for a given (userid, printerid)."""
        result = self.doQuery("SELECT lifepagecounter, pagecounter, softlimit, hardlimit, datelimit FROM userpquota WHERE userid=%s AND printerid=%s" % (self.doQuote(userid), self.doQuote(printerid)))
        try :
            return self.doParseResult(result)[0]
        except TypeError :      # Not found    
            return
        
    def getGroupPQuota(self, groupid, printerid) :
        """Returns the Print Quota information for a given (groupid, printerid)."""
        result = self.doQuery("SELECT softlimit, hardlimit, datelimit FROM grouppquota WHERE groupid=%s AND printerid=%s" % (self.doQuote(groupid), self.doQuote(printerid)))
        try :
            grouppquota = self.doParseResult(result)[0]
        except TypeError :    
            return
        else :    
            result = self.doQuery("SELECT SUM(lifepagecounter) as lifepagecounter, SUM(pagecounter) as pagecounter FROM userpquota WHERE printerid=%s AND userid in (SELECT userid FROM groupsmembers WHERE groupid=%s)" % (self.doQuote(printerid), self.doQuote(groupid)))
            try :
                result = self.doParseResult(result)[0]
            except TypeError :      # Not found    
                return
            else :    
                grouppquota.update({"lifepagecounter": result["lifepagecounter"], "pagecounter": result["pagecounter"]})
                return grouppquota
        
    def setUserDateLimit(self, userid, printerid, datelimit) :
        """Sets the limit date for a soft limit to become an hard one given (userid, printerid)."""
        self.doQuery("UPDATE userpquota SET datelimit=%s::TIMESTAMP WHERE userid=%s AND printerid=%s" % (self.doQuote("%04i-%02i-%02i %02i:%02i:%02i" % (datelimit.year, datelimit.month, datelimit.day, datelimit.hour, datelimit.minute, datelimit.second)), self.doQuote(userid), self.doQuote(printerid)))
        
    def setGroupDateLimit(self, groupid, printerid, datelimit) :
        """Sets the limit date for a soft limit to become an hard one given (groupid, printerid)."""
        self.doQuery("UPDATE grouppquota SET datelimit=%s::TIMESTAMP WHERE groupid=%s AND printerid=%s" % (self.doQuote("%04i-%02i-%02i %02i:%02i:%02i" % (datelimit.year, datelimit.month, datelimit.day, datelimit.hour, datelimit.minute, datelimit.second)), self.doQuote(groupid), self.doQuote(printerid)))
        
    def addJobToHistory(self, jobid, userid, printerid, pagecounter, action, jobsize=None) :
        """Adds a job to the history: (jobid, userid, printerid, last page counter taken from requester)."""
        self.doQuery("INSERT INTO jobhistory (jobid, userid, printerid, pagecounter, action, jobsize) VALUES (%s, %s, %s, %s, %s, %s)" % (self.doQuote(jobid), self.doQuote(userid), self.doQuote(printerid), self.doQuote(pagecounter), self.doQuote(action), self.doQuote(jobsize)))
        return self.getJobHistoryId(jobid, userid, printerid) # in case jobid is not sufficient
    
    def updateJobSizeInHistory(self, historyid, jobsize) :
        """Updates a job size in the history given the history line's id."""
        self.doQuery("UPDATE jobhistory SET jobsize=%s WHERE id=%s" % (self.doQuote(jobsize), self.doQuote(historyid)))
    
    def getPrinterPageCounter(self, printerid) :
        """Returns the last page counter value for a printer given its id, also returns last username, last jobid and history line id."""
        result = self.doQuery("SELECT jobhistory.id, jobid, userid, username, pagecounter, jobsize FROM jobhistory, users WHERE printerid=%s AND userid=users.id ORDER BY jobdate DESC LIMIT 1" % self.doQuote(printerid))
        try :
            return self.doParseResult(result)[0]
        except TypeError :      # Not found
            return
        
    def addUserToGroup(self, userid, groupid) :    
        """Adds an user to a group."""
        result = self.doQuery("SELECT COUNT(*) AS mexists FROM groupsmembers WHERE groupid=%s AND userid=%s" % (self.doQuote(groupid), self.doQuote(userid)))
        try :
            mexists = self.doParseResult(result)[0]["mexists"]
        except TypeError :    
            mexists = 0
        if not mexists :    
            self.doQuery("INSERT INTO groupsmembers (groupid, userid) VALUES (%s, %s)" % (self.doQuote(groupid), self.doQuote(userid)))
        
    def deleteUser(self, userid) :    
        """Completely deletes an user from the Quota Storage."""
        queries = []
        queries.append("DELETE FROM groupsmembers WHERE userid=%s" % self.doQuote(userid))
        queries.append("DELETE FROM jobhistory WHERE userid=%s" % self.doQuote(userid))
        queries.append("DELETE FROM userpquota WHERE userid=%s" % self.doQuote(userid))
        queries.append("DELETE FROM users WHERE id=%s" % self.doQuote(userid))
        # TODO : What should we do if we delete the last person who used a given printer ?
        self.doQuery(queries)
        
    def deleteGroup(self, groupid) :    
        """Completely deletes an user from the Quota Storage."""
        queries = []
        queries.append("DELETE FROM groupsmembers WHERE groupid=%s" % self.doQuote(groupid))
        queries.append("DELETE FROM grouppquota WHERE groupid=%s" % self.doQuote(groupid))
        queries.append("DELETE FROM groups WHERE id=%s" % self.doQuote(groupid))
        self.doQuery(queries)
        
    def computePrinterJobPrice(self, printerid, jobsize) :    
        """Returns the price for a job on a given printer."""
        # TODO : create a base class with things like this
        prices = self.getPrinterPrices(printerid)
        if prices is None :
            perpage = perjob = 0.0
        else :    
            (perpage, perjob) = prices
        return perjob + (perpage * jobsize)
        
