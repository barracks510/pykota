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
# Revision 1.16  2003/10/03 18:01:49  jalet
# Nothing interesting...
#
# Revision 1.15  2003/10/03 12:27:03  jalet
# Several optimizations, especially with LDAP backend
#
# Revision 1.14  2003/10/03 08:57:55  jalet
# Caching mechanism now caches all that's cacheable.
#
# Revision 1.13  2003/10/02 20:23:18  jalet
# Storage caching mechanism added.
#
# Revision 1.12  2003/08/17 14:20:25  jalet
# Bug fix by Oleg Biteryakov
#
# Revision 1.11  2003/07/29 20:55:17  jalet
# 1.14 is out !
#
# Revision 1.10  2003/07/16 21:53:08  jalet
# Really big modifications wrt new configuration file's location and content.
#
# Revision 1.9  2003/07/14 17:20:15  jalet
# Bug in postgresql storage when modifying the prices for a printer
#
# Revision 1.8  2003/07/14 14:18:17  jalet
# Wrong documentation strings
#
# Revision 1.7  2003/07/09 20:17:07  jalet
# Email field added to PostgreSQL schema
#
# Revision 1.6  2003/07/07 11:49:24  jalet
# Lots of small fixes with the help of PyChecker
#
# Revision 1.5  2003/07/07 08:33:19  jalet
# Bug fix due to a typo in LDAP code
#
# Revision 1.4  2003/06/30 13:54:21  jalet
# Sorts by user / group name
#
# Revision 1.3  2003/06/25 14:10:01  jalet
# Hey, it may work (edpykota --reset excepted) !
#
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

from pykota.storage import PyKotaStorageError,BaseStorage,StorageObject,StorageUser,StorageGroup,StoragePrinter,StorageLastJob,StorageUserPQuota,StorageGroupPQuota

try :
    import pg
except ImportError :    
    import sys
    # TODO : to translate or not to translate ?
    raise PyKotaStorageError, "This python version (%s) doesn't seem to have the PygreSQL module installed correctly." % sys.version.split()[0]

class Storage(BaseStorage) :
    def __init__(self, pykotatool, host, dbname, user, passwd) :
        """Opens the PostgreSQL database connection."""
        BaseStorage.__init__(self, pykotatool)
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
            self.tool.logdebug("Database opened (host=%s, port=%s, dbname=%s, user=%s)" % (host, port, dbname, user))
            
    def close(self) :    
        """Closes the database connection."""
        if not self.closed :
            self.database.close()
            self.closed = 1
            self.tool.logdebug("Database closed.")
        
    def beginTransaction(self) :    
        """Starts a transaction."""
        self.database.query("BEGIN;")
        self.tool.logdebug("Transaction begins...")
        
    def commitTransaction(self) :    
        """Commits a transaction."""
        self.database.query("COMMIT;")
        self.tool.logdebug("Transaction committed.")
        
    def rollbackTransaction(self) :     
        """Rollbacks a transaction."""
        self.database.query("ROLLBACK;")
        self.tool.logdebug("Transaction aborted.")
        
    def doSearch(self, query) :
        """Does a search query."""
        query = query.strip()    
        if not query.endswith(';') :    
            query += ';'
        try :
            self.tool.logdebug("QUERY : %s" % query)
            result = self.database.query(query)
        except pg.error, msg :    
            raise PyKotaStorageError, msg
        else :    
            if (result is not None) and (result.ntuples() > 0) : 
                return result.dictresult()
            
    def doModify(self, query) :
        """Does a (possibly multiple) modify query."""
        query = query.strip()    
        if not query.endswith(';') :    
            query += ';'
        try :
            self.tool.logdebug("QUERY : %s" % query)
            result = self.database.query(query)
        except pg.error, msg :    
            raise PyKotaStorageError, msg
        else :    
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
        
    def getUserFromBackend(self, username) :    
        """Extracts user information given its name."""
        user = StorageUser(self, username)
        result = self.doSearch("SELECT * FROM users WHERE username=%s LIMIT 1" % self.doQuote(username))
        if result :
            fields = result[0]
            user.ident = fields.get("id")
            user.LimitBy = fields.get("limitby")
            user.AccountBalance = fields.get("balance")
            user.LifeTimePaid = fields.get("lifetimepaid")
            user.Email = fields.get("email")
            user.Exists = 1
        return user
       
    def getGroupFromBackend(self, groupname) :    
        """Extracts group information given its name."""
        group = StorageGroup(self, groupname)
        result = self.doSearch("SELECT * FROM groups WHERE groupname=%s LIMIT 1" % self.doQuote(groupname))
        if result :
            fields = result[0]
            group.ident = fields.get("id")
            group.LimitBy = fields.get("limitby")
            result = self.doSearch("SELECT SUM(balance) AS balance, SUM(lifetimepaid) AS lifetimepaid FROM users WHERE id IN (SELECT userid FROM groupsmembers WHERE groupid=%s)" % self.doQuote(group.ident))
            if result :
                fields = result[0]
                group.AccountBalance = fields.get("balance")
                group.LifeTimePaid = fields.get("lifetimepaid")
            group.Exists = 1
        return group
       
    def getPrinterFromBackend(self, printername) :        
        """Extracts printer information given its name."""
        printer = StoragePrinter(self, printername)
        result = self.doSearch("SELECT * FROM printers WHERE printername=%s LIMIT 1" % self.doQuote(printername))
        if result :
            fields = result[0]
            printer.ident = fields.get("id")
            printer.PricePerJob = fields.get("priceperjob")
            printer.PricePerPage = fields.get("priceperpage")
            printer.LastJob = self.getPrinterLastJob(printer)
            printer.Exists = 1
        return printer    
        
    def getUserPQuotaFromBackend(self, user, printer) :        
        """Extracts a user print quota."""
        userpquota = StorageUserPQuota(self, user, printer)
        if user.Exists :
            result = self.doSearch("SELECT id, lifepagecounter, pagecounter, softlimit, hardlimit, datelimit FROM userpquota WHERE userid=%s AND printerid=%s" % (self.doQuote(user.ident), self.doQuote(printer.ident)))
            if result :
                fields = result[0]
                userpquota.ident = fields.get("id")
                userpquota.PageCounter = fields.get("pagecounter")
                userpquota.LifePageCounter = fields.get("lifepagecounter")
                userpquota.SoftLimit = fields.get("softlimit")
                userpquota.HardLimit = fields.get("hardlimit")
                userpquota.DateLimit = fields.get("datelimit")
                userpquota.Exists = 1
        return userpquota
        
    def getGroupPQuotaFromBackend(self, group, printer) :        
        """Extracts a group print quota."""
        grouppquota = StorageGroupPQuota(self, group, printer)
        if group.Exists :
            result = self.doSearch("SELECT id, softlimit, hardlimit, datelimit FROM grouppquota WHERE groupid=%s AND printerid=%s" % (self.doQuote(group.ident), self.doQuote(printer.ident)))
            if result :
                fields = result[0]
                grouppquota.ident = fields.get("id")
                grouppquota.SoftLimit = fields.get("softlimit")
                grouppquota.HardLimit = fields.get("hardlimit")
                grouppquota.DateLimit = fields.get("datelimit")
                result = self.doSearch("SELECT SUM(lifepagecounter) AS lifepagecounter, SUM(pagecounter) AS pagecounter FROM userpquota WHERE printerid=%s AND userid IN (SELECT userid FROM groupsmembers WHERE groupid=%s)" % (self.doQuote(printer.ident), self.doQuote(group.ident)))
                if result :
                    fields = result[0]
                    grouppquota.PageCounter = fields.get("pagecounter")
                    grouppquota.LifePageCounter = fields.get("lifepagecounter")
                grouppquota.Exists = 1
        return grouppquota
        
    def getPrinterLastJobFromBackend(self, printer) :        
        """Extracts a printer's last job information."""
        lastjob = StorageLastJob(self, printer)
        result = self.doSearch("SELECT jobhistory.id, jobid, userid, username, pagecounter, jobsize, jobdate FROM jobhistory, users WHERE printerid=%s AND userid=users.id ORDER BY jobdate DESC LIMIT 1" % self.doQuote(printer.ident))
        if result :
            fields = result[0]
            lastjob.ident = fields.get("id")
            lastjob.JobId = fields.get("jobid")
            lastjob.User = self.getUser(fields.get("username"))
            lastjob.PrinterPageCounter = fields.get("pagecounter")
            lastjob.JobSize = fields.get("jobsize")
            lastjob.JobAction = fields.get("action")
            lastjob.JobDate = fields.get("jobdate")
            lastjob.Exists = 1
        return lastjob
            
    def getUserGroups(self, user) :        
        """Returns the user's groups list."""
        groups = []
        result = self.doSearch("SELECT groupname FROM groupsmembers JOIN groups ON groupsmembers.groupid=groups.id WHERE userid=%s" % self.doQuote(user.ident))
        if result :
            for record in result :
                groups.append(self.getGroup(record.get("groupname")))
        return groups        
        
    def getGroupMembers(self, group) :        
        """Returns the group's members list."""
        groupmembers = []
        result = self.doSearch("SELECT * FROM groupsmembers JOIN users ON groupsmembers.userid=users.id WHERE groupid=%s" % self.doQuote(group.ident))
        if result :
            for record in result :
                user = StorageUser(self, record.get("username"))
                user.ident = record.get("userid")
                user.LimitBy = record.get("limitby")
                user.AccountBalance = record.get("balance")
                user.LifeTimePaid = record.get("lifetimepaid")
                user.Email = record.get("email")
                user.Exists = 1
                groupmembers.append(user)
                self.cacheEntry("USERS", user.Name, user)
        return groupmembers        
        
    def getMatchingPrinters(self, printerpattern) :
        """Returns the list of all printers for which name matches a certain pattern."""
        printers = []
        # We 'could' do a SELECT printername FROM printers WHERE printername LIKE ...
        # but we don't because other storages semantics may be different, so every
        # storage should use fnmatch to match patterns and be storage agnostic
        result = self.doSearch("SELECT * FROM printers")
        if result :
            for record in result :
                if self.tool.matchString(record["printername"], [ printerpattern ]) :
                    printer = StoragePrinter(self, record["printername"])
                    printer.ident = record.get("id")
                    printer.PricePerJob = record.get("priceperjob")
                    printer.PricePerPage = record.get("priceperpage")
                    printer.LastJob = self.getPrinterLastJob(printer)
                    printer.Exists = 1
                    printers.append(printer)
                    self.cacheEntry("PRINTERS", printer.Name, printer)
        return printers        
        
    def getPrinterUsersAndQuotas(self, printer, names=["*"]) :        
        """Returns the list of users who uses a given printer, along with their quotas."""
        usersandquotas = []
        result = self.doSearch("SELECT users.id as uid,username,balance,lifetimepaid,limitby,email,userpquota.id,lifepagecounter,pagecounter,softlimit,hardlimit,datelimit FROM users JOIN userpquota ON users.id=userpquota.userid AND printerid=%s ORDER BY username ASC" % self.doQuote(printer.ident))
        if result :
            for record in result :
                if self.tool.matchString(record.get("username"), names) :
                    user = StorageUser(self, record.get("username"))
                    user.ident = record.get("uid")
                    user.LimitBy = record.get("limitby")
                    user.AccountBalance = record.get("balance")
                    user.LifeTimePaid = record.get("lifetimepaid")
                    user.Email = record.get("email") 
                    user.Exists = 1
                    userpquota = StorageUserPQuota(self, user, printer)
                    userpquota.ident = record.get("id")
                    userpquota.PageCounter = record.get("pagecounter")
                    userpquota.LifePageCounter = record.get("lifepagecounter")
                    userpquota.SoftLimit = record.get("softlimit")
                    userpquota.HardLimit = record.get("hardlimit")
                    userpquota.DateLimit = record.get("datelimit")
                    userpquota.Exists = 1
                    usersandquotas.append((user, userpquota))
                    self.cacheEntry("USERS", user.Name, user)
                    self.cacheEntry("USERPQUOTAS", "%s@%s" % (user.Name, printer.Name), userpquota)
        return usersandquotas
                
    def getPrinterGroupsAndQuotas(self, printer, names=["*"]) :        
        """Returns the list of groups which uses a given printer, along with their quotas."""
        groupsandquotas = []
        result = self.doSearch("SELECT groupname FROM groups JOIN grouppquota ON groups.id=grouppquota.groupid AND printerid=%s ORDER BY groupname ASC" % self.doQuote(printer.ident))
        if result :
            for record in result :
                if self.tool.matchString(record.get("groupname"), names) :
                    group = self.getGroup(record.get("groupname"))
                    grouppquota = self.getGroupPQuota(group, printer)
                    groupsandquotas.append((group, grouppquota))
        return groupsandquotas
        
    def addPrinter(self, printername) :        
        """Adds a printer to the quota storage, returns it."""
        self.doModify("INSERT INTO printers (printername) VALUES (%s)" % self.doQuote(printername))
        return self.getPrinter(printername)
        
    def addUser(self, user) :        
        """Adds a user to the quota storage, returns its id."""
        self.doModify("INSERT INTO users (username, limitby, balance, lifetimepaid, email) VALUES (%s, %s, %s, %s, %s)" % (self.doQuote(user.Name), self.doQuote(user.LimitBy), self.doQuote(user.AccountBalance), self.doQuote(user.LifeTimePaid), self.doQuote(user.Email)))
        return self.getUser(user.Name)
        
    def addGroup(self, group) :        
        """Adds a group to the quota storage, returns its id."""
        self.doModify("INSERT INTO groups (groupname, limitby) VALUES (%s, %s)" % (self.doQuote(group.Name), self.doQuote(group.LimitBy)))
        return self.getGroup(group.Name)

    def addUserToGroup(self, user, group) :    
        """Adds an user to a group."""
        result = self.doSearch("SELECT COUNT(*) AS mexists FROM groupsmembers WHERE groupid=%s AND userid=%s" % (self.doQuote(group.ident), self.doQuote(user.ident)))
        try :
            mexists = int(result[0].get("mexists"))
        except (IndexError, TypeError) :    
            mexists = 0
        if not mexists :    
            self.doModify("INSERT INTO groupsmembers (groupid, userid) VALUES (%s, %s)" % (self.doQuote(group.ident), self.doQuote(user.ident)))
            
    def addUserPQuota(self, user, printer) :
        """Initializes a user print quota on a printer."""
        self.doModify("INSERT INTO userpquota (userid, printerid) VALUES (%s, %s)" % (self.doQuote(user.ident), self.doQuote(printer.ident)))
        return self.getUserPQuota(user, printer)
        
    def addGroupPQuota(self, group, printer) :
        """Initializes a group print quota on a printer."""
        self.doModify("INSERT INTO grouppquota (groupid, printerid) VALUES (%s, %s)" % (self.doQuote(group.ident), self.doQuote(printer.ident)))
        return self.getGroupPQuota(group, printer)
        
    def writePrinterPrices(self, printer) :    
        """Write the printer's prices back into the storage."""
        self.doModify("UPDATE printers SET priceperpage=%s, priceperjob=%s WHERE id=%s" % (self.doQuote(printer.PricePerPage), self.doQuote(printer.PricePerJob), self.doQuote(printer.ident)))
        
    def writeUserLimitBy(self, user, limitby) :    
        """Sets the user's limiting factor."""
        self.doModify("UPDATE users SET limitby=%s WHERE id=%s" % (self.doQuote(limitby), self.doQuote(user.ident)))
        
    def writeGroupLimitBy(self, group, limitby) :    
        """Sets the group's limiting factor."""
        self.doModify("UPDATE groups SET limitby=%s WHERE id=%s" % (self.doQuote(limitby), self.doQuote(group.ident)))
        
    def writeUserPQuotaDateLimit(self, userpquota, datelimit) :    
        """Sets the date limit permanently for a user print quota."""
        self.doModify("UPDATE userpquota SET datelimit=%s WHERE id=%s" % (self.doQuote(datelimit), self.doQuote(userpquota.ident)))
            
    def writeGroupPQuotaDateLimit(self, grouppquota, datelimit) :    
        """Sets the date limit permanently for a group print quota."""
        self.doModify("UPDATE grouppquota SET datelimit=%s WHERE id=%s" % (self.doQuote(datelimit), self.doQuote(grouppquota.ident)))
        
    def writeUserPQuotaPagesCounters(self, userpquota, newpagecounter, newlifepagecounter) :    
       """Sets the new page counters permanently for a user print quota."""
       self.doModify("UPDATE userpquota SET pagecounter=%s,lifepagecounter=%s WHERE id=%s" % (self.doQuote(newpagecounter), self.doQuote(newlifepagecounter), self.doQuote(userpquota.ident)))
       
    def writeUserAccountBalance(self, user, newbalance, newlifetimepaid=None) :    
       """Sets the new account balance and eventually new lifetime paid."""
       if newlifetimepaid is not None :
           self.doModify("UPDATE users SET balance=%s, lifetimepaid=%s WHERE id=%s" % (self.doQuote(newbalance), self.doQuote(newlifetimepaid), self.doQuote(user.ident)))
       else :    
           self.doModify("UPDATE users SET balance=%s WHERE id=%s" % (self.doQuote(newbalance), self.doQuote(user.ident)))
            
    def writeLastJobSize(self, lastjob, jobsize) :        
        """Sets the last job's size permanently."""
        self.doModify("UPDATE jobhistory SET jobsize=%s WHERE id=%s" % (self.doQuote(jobsize), self.doQuote(lastjob.ident)))
        
    def writeJobNew(self, printer, user, jobid, pagecounter, action, jobsize=None) :    
        """Adds a job in a printer's history."""
        if jobsize is not None :
            self.doModify("INSERT INTO jobhistory (userid, printerid, jobid, pagecounter, action, jobsize) VALUES (%s, %s, %s, %s, %s, %s)" % (self.doQuote(user.ident), self.doQuote(printer.ident), self.doQuote(jobid), self.doQuote(pagecounter), self.doQuote(action), self.doQuote(jobsize)))
        else :    
            self.doModify("INSERT INTO jobhistory (userid, printerid, jobid, pagecounter, action) VALUES (%s, %s, %s, %s, %s)" % (self.doQuote(user.ident), self.doQuote(printer.ident), self.doQuote(jobid), self.doQuote(pagecounter), self.doQuote(action)))
            
    def writeUserPQuotaLimits(self, userpquota, softlimit, hardlimit) :
        """Sets soft and hard limits for a user quota."""
        self.doModify("UPDATE userpquota SET softlimit=%s, hardlimit=%s, datelimit=NULL WHERE id=%s" % (self.doQuote(softlimit), self.doQuote(hardlimit), self.doQuote(userpquota.ident)))
        
    def writeGroupPQuotaLimits(self, grouppquota, softlimit, hardlimit) :
        """Sets soft and hard limits for a group quota on a specific printer."""
        self.doModify("UPDATE grouppquota SET softlimit=%s, hardlimit=%s, datelimit=NULL WHERE id=%s" % (self.doQuote(softlimit), self.doQuote(hardlimit), self.doQuote(grouppquota.ident)))

    def deleteUser(self, user) :    
        """Completely deletes an user from the Quota Storage."""
        # TODO : What should we do if we delete the last person who used a given printer ?
        # TODO : we can't reassign the last job to the previous one, because next user would be
        # TODO : incorrectly charged (overcharged).
        for q in [ 
                    "DELETE FROM groupsmembers WHERE userid=%s" % self.doQuote(user.ident),
                    "DELETE FROM jobhistory WHERE userid=%s" % self.doQuote(user.ident),
                    "DELETE FROM userpquota WHERE userid=%s" % self.doQuote(user.ident),
                    "DELETE FROM users WHERE id=%s" % self.doQuote(user.ident),
                  ] :
            self.doModify(q)
        
    def deleteGroup(self, group) :    
        """Completely deletes a group from the Quota Storage."""
        for q in [
                   "DELETE FROM groupsmembers WHERE groupid=%s" % self.doQuote(group.ident),
                   "DELETE FROM grouppquota WHERE groupid=%s" % self.doQuote(group.ident),
                   "DELETE FROM groups WHERE id=%s" % self.doQuote(group.ident),
                 ] :  
            self.doModify(q)
        
