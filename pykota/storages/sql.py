# PyKota
#
# PyKota : Print Quotas for CUPS
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
# Revision 1.27  2003/04/16 12:35:49  jalet
# Groups quota work now !
#
# Revision 1.26  2003/04/16 08:53:14  jalet
# Printing can now be limited either by user's account balance or by
# page quota (the default). Quota report doesn't include account balance
# yet, though.
#
# Revision 1.25  2003/04/15 21:58:33  jalet
# edpykota now accepts a --delete option.
# Preparation to allow edpykota to accept much more command line options
# (WARNING : docstring is OK, but code isn't !)
#
# Revision 1.24  2003/04/15 13:55:28  jalet
# Options --limitby and --balance added to edpykota
#
# Revision 1.23  2003/04/15 11:30:57  jalet
# More work done on money print charging.
# Minor bugs corrected.
# All tools now access to the storage as priviledged users, repykota excepted.
#
# Revision 1.22  2003/04/10 21:47:20  jalet
# Job history added. Upgrade script neutralized for now !
#
# Revision 1.21  2003/04/08 20:38:08  jalet
# The last job Id is saved now for each printer, this will probably
# allow other accounting methods in the future.
#
# Revision 1.20  2003/03/29 13:45:27  jalet
# GPL paragraphs were incorrectly (from memory) copied into the sources.
# Two README files were added.
# Upgrade script for PostgreSQL pre 1.01 schema was added.
#
# Revision 1.19  2003/02/27 08:41:49  jalet
# DATETIME is not supported anymore in PostgreSQL 7.3 it seems, but
# TIMESTAMP is.
#
# Revision 1.18  2003/02/10 12:07:31  jalet
# Now repykota should output the recorded total page number for each printer too.
#
# Revision 1.17  2003/02/10 08:41:36  jalet
# edpykota's --reset command line option resets the limit date too.
#
# Revision 1.16  2003/02/08 22:39:46  jalet
# --reset command line option added
#
# Revision 1.15  2003/02/08 22:12:09  jalet
# Life time counter for users and groups added.
#
# Revision 1.14  2003/02/07 22:13:13  jalet
# Perhaps edpykota is now able to add printers !!! Oh, stupid me !
#
# Revision 1.13  2003/02/07 00:08:52  jalet
# Typos
#
# Revision 1.12  2003/02/06 23:20:03  jalet
# warnpykota doesn't need any user/group name argument, mimicing the
# warnquota disk quota tool.
#
# Revision 1.11  2003/02/06 15:05:13  jalet
# self was forgotten
#
# Revision 1.10  2003/02/06 15:03:11  jalet
# added a method to set the limit date
#
# Revision 1.9  2003/02/06 14:52:35  jalet
# Forgotten import
#
# Revision 1.8  2003/02/06 14:49:04  jalet
# edpykota should be ok now
#
# Revision 1.7  2003/02/06 14:28:59  jalet
# edpykota should be ok, minus some typos
#
# Revision 1.6  2003/02/06 09:19:02  jalet
# More robust behavior (hopefully) when the user or printer is not managed
# correctly by the Quota System : e.g. cupsFilter added in ppd file, but
# printer and/or user not 'yet?' in storage.
#
# Revision 1.5  2003/02/05 23:26:22  jalet
# Incorrect handling of grace delay
#
# Revision 1.4  2003/02/05 23:02:10  jalet
# Typo
#
# Revision 1.3  2003/02/05 23:00:12  jalet
# Forgotten import
# Bad datetime conversion
#
# Revision 1.2  2003/02/05 22:28:38  jalet
# More robust storage
#
# Revision 1.1  2003/02/05 21:28:17  jalet
# Initial import into CVS
#
#
#

import fnmatch

class SQLStorage :    
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
        """Returns the list of usernames which uses a given printer."""
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
        result = self.doQuery("SELECT balance FROM users WHERE id=%s" % self.doQuote(userid))
        try :
            return self.doParseResult(result)[0]["balance"]
        except TypeError :      # Not found    
            return
        
    def getGroupBalance(self, groupid) :    
        """Returns the current account balance for a given group, as the sum of each of its users' account balance."""
        result = self.doQuery("SELECT SUM(balance) AS balance FROM users WHERE id in (SELECT userid FROM groupsmembers WHERE groupid=%s)" % self.doQuote(groupid))
        try :
            return self.doParseResult(result)[0]["balance"]
        except TypeError :      # Not found    
            return
        
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
        current = self.getUserBalance(userid)
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
        
    def addJobToHistory(self, jobid, userid, printerid, pagecounter, action) :
        """Adds a job to the history: (jobid, userid, printerid, last page counter taken from requester)."""
        self.doQuery("INSERT INTO jobhistory (jobid, userid, printerid, pagecounter, action) VALUES (%s, %s, %s, %s, %s)" % (self.doQuote(jobid), self.doQuote(userid), self.doQuote(printerid), self.doQuote(pagecounter), self.doQuote(action)))
        return self.getJobHistoryId(jobid, userid, printerid) # in case jobid is not sufficient
    
    def updateJobSizeInHistory(self, historyid, jobsize) :
        """Updates a job size in the history given the history line's id."""
        self.doQuery("UPDATE jobhistory SET jobsize=%s WHERE id=%s" % (self.doQuote(jobsize), self.doQuote(historyid)))
    
    def getPrinterPageCounter(self, printerid) :
        """Returns the last page counter value for a printer given its id, also returns last username, last jobid and history line id."""
        result = self.doQuery("SELECT jobhistory.id, jobid, userid, username, pagecounter FROM jobhistory, users WHERE printerid=%s AND userid=users.id ORDER BY jobdate DESC LIMIT 1" % self.doQuote(printerid))
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
        prices = self.getPrinterPrices(printerid)
        if prices is None :
            perpage = perjob = 0.0
        else :    
            (perpage, perjob) = prices
        return perjob + (perpage * jobsize)
