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
# Revision 1.49  2004/10/02 13:33:13  jalet
# Some work done of user's charset handling in database dumps.
#
# Revision 1.48  2004/10/02 05:48:56  jalet
# Should now correctly deal with charsets both when storing into databases and when
# retrieving datas. Works with both PostgreSQL and LDAP.
#
# Revision 1.47  2004/09/15 07:26:20  jalet
# Data dumps are now ordered by entry creation date if applicable.
# Now dumpykota exits with a message when there's a broken pipe like
# in dumpykota --data history | head -3
#
# Revision 1.46  2004/09/15 06:58:25  jalet
# User groups membership and printer groups membership can now be dumped too
#
# Revision 1.45  2004/09/14 22:29:13  jalet
# First version of dumpykota. Works fine but only with PostgreSQL backend
# for now.
#
# Revision 1.44  2004/09/10 21:32:54  jalet
# Small fixes for incomplete entry intialization
#
# Revision 1.43  2004/07/01 17:45:49  jalet
# Added code to handle the description field for printers
#
# Revision 1.42  2004/06/08 17:44:43  jalet
# Payment now gets deleted when the user is deleted
#
# Revision 1.41  2004/06/05 22:03:50  jalet
# Payments history is now stored in database
#
# Revision 1.40  2004/06/03 23:14:11  jalet
# Now stores the job's size in bytes in the database.
# Preliminary work on payments storage : database schemas are OK now,
# but no code to store payments yet.
# Removed schema picture, not relevant anymore.
#
# Revision 1.39  2004/05/26 14:50:12  jalet
# First try at saving the job-originating-hostname in the database
#
# Revision 1.38  2004/05/06 12:37:47  jalet
# pkpgcounter : comments
# pkprinters : when --add is used, existing printers are now skipped.
#
# Revision 1.37  2004/02/23 22:53:21  jalet
# Don't retrieve data when it's not needed, to avoid database queries
#
# Revision 1.36  2004/02/04 13:24:41  jalet
# pkprinters can now remove printers from printers groups.
#
# Revision 1.35  2004/02/04 11:17:00  jalet
# pkprinters command line tool added.
#
# Revision 1.34  2004/02/02 22:44:16  jalet
# Preliminary work on Relationnal Database Independance via DB-API 2.0
#
#
#

from types import StringType
from pykota.storage import PyKotaStorageError,BaseStorage,StorageObject,StorageUser,StorageGroup,StoragePrinter,StorageJob,StorageLastJob,StorageUserPQuota,StorageGroupPQuota

class SQLStorage :
    def prepareRawResult(self, result) :
        """Prepares a raw result by including the headers."""
        if result.ntuples() > 0 :
            entries = [result.listfields()]
            entries.extend(result.getresult())
            #nbfields = len(entries[0])
            #for i in range(1, len(entries)) :
            #    fields = list(entries[i])
            #    for j in range(nbfields) :
            #        field = fields[j]
            #        if type(field) == StringType :
            #            try :
            #                fields[j] = field.decode("UTF-8").encode(self.tool.getCharset()) 
            #            except UnicodeEncodeError : # takes care of old jobs in history not stored as UTF-8    
            #                pass
            #    entries[i] = tuple(fields)    
            return entries
        
    def extractPrinters(self) :
        """Extracts all printer records."""
        result = self.doRawSearch("SELECT * FROM printers ORDER BY id ASC")
        return self.prepareRawResult(result)
        
    def extractUsers(self) :
        """Extracts all user records."""
        result = self.doRawSearch("SELECT * FROM users ORDER BY id ASC")
        return self.prepareRawResult(result)
        
    def extractGroups(self) :
        """Extracts all group records."""
        result = self.doRawSearch("SELECT * FROM groups ORDER BY id ASC")
        return self.prepareRawResult(result)
        
    def extractPayments(self) :
        """Extracts all payment records."""
        result = self.doRawSearch("SELECT username,payments.* FROM users,payments WHERE users.id=payments.userid ORDER BY payments.id ASC")
        return self.prepareRawResult(result)
        
    def extractUpquotas(self) :
        """Extracts all userpquota records."""
        result = self.doRawSearch("SELECT users.username,printers.printername,userpquota.* FROM users,printers,userpquota WHERE users.id=userpquota.userid AND printers.id=userpquota.printerid ORDER BY userpquota.id ASC")
        return self.prepareRawResult(result)
        
    def extractGpquotas(self) :
        """Extracts all grouppquota records."""
        result = self.doRawSearch("SELECT groups.groupname,printers.printername,grouppquota.* FROM groups,printers,grouppquota WHERE groups.id=grouppquota.groupid AND printers.id=grouppquota.printerid ORDER BY grouppquota.id ASC")
        return self.prepareRawResult(result)
        
    def extractUmembers(self) :
        """Extracts all user groups members."""
        result = self.doRawSearch("SELECT groups.groupname, users.username, groupsmembers.* FROM groups,users,groupsmembers WHERE users.id=groupsmembers.userid AND groups.id=groupsmembers.groupid ORDER BY groupsmembers.groupid, groupsmembers.userid ASC")
        return self.prepareRawResult(result)
        
    def extractPmembers(self) :
        """Extracts all printer groups members."""
        result = self.doRawSearch("SELECT p1.printername as pgroupname, p2.printername as printername, printergroupsmembers.* FROM printers p1, printers p2, printergroupsmembers WHERE p1.id=printergroupsmembers.groupid AND p2.id=printergroupsmembers.printerid ORDER BY printergroupsmembers.groupid, printergroupsmembers.printerid ASC")
        return self.prepareRawResult(result)
        
    def extractHistory(self) :
        """Extracts all jobhistory records."""
        result = self.doRawSearch("SELECT users.username,printers.printername,jobhistory.* FROM users,printers,jobhistory WHERE users.id=jobhistory.userid AND printers.id=jobhistory.printerid ORDER BY jobhistory.id ASC")
        return self.prepareRawResult(result)
        
    def getAllUsersNames(self) :    
        """Extracts all user names."""
        usernames = []
        result = self.doSearch("SELECT username FROM users")
        if result :
            usernames = [record["username"] for record in result]
        return usernames
        
    def getAllGroupsNames(self) :    
        """Extracts all group names."""
        groupnames = []
        result = self.doSearch("SELECT groupname FROM groups")
        if result :
            groupnames = [record["groupname"] for record in result]
        return groupnames
        
    def getUserFromBackend(self, username) :    
        """Extracts user information given its name."""
        user = StorageUser(self, username)
        result = self.doSearch("SELECT * FROM users WHERE username=%s LIMIT 1" % self.doQuote(username))
        if result :
            fields = result[0]
            user.ident = fields.get("id")
            user.Name = fields.get("username", username)
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
            group.Name = fields.get("groupname", groupname)
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
            printer.Name = fields.get("printername", printername)
            printer.PricePerJob = fields.get("priceperjob") or 0.0
            printer.PricePerPage = fields.get("priceperpage") or 0.0
            printer.Description = (fields.get("description") or "").decode("UTF-8").encode(self.tool.getCharset()) 
            printer.Exists = 1
        return printer    
        
    def getUserPQuotaFromBackend(self, user, printer) :        
        """Extracts a user print quota."""
        userpquota = StorageUserPQuota(self, user, printer)
        if printer.Exists and user.Exists :
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
        result = self.doSearch("SELECT jobhistory.id, jobid, userid, username, pagecounter, jobsize, jobprice, filename, title, copies, options, hostname, jobdate FROM jobhistory, users WHERE printerid=%s AND userid=users.id ORDER BY jobdate DESC LIMIT 1" % self.doQuote(printer.ident))
        if result :
            fields = result[0]
            lastjob.ident = fields.get("id")
            lastjob.JobId = fields.get("jobid")
            lastjob.UserName = fields.get("username")
            lastjob.PrinterPageCounter = fields.get("pagecounter")
            lastjob.JobSize = fields.get("jobsize")
            lastjob.JobPrice = fields.get("jobprice")
            lastjob.JobAction = fields.get("action")
            lastjob.JobFileName = (fields.get("filename") or "").decode("UTF-8").encode(self.tool.getCharset()) 
            lastjob.JobTitle = (fields.get("title") or "").decode("UTF-8").encode(self.tool.getCharset()) 
            lastjob.JobCopies = fields.get("copies")
            lastjob.JobOptions = (fields.get("options") or "").decode("UTF-8").encode(self.tool.getCharset()) 
            lastjob.JobDate = fields.get("jobdate")
            lastjob.JobHostName = fields.get("hostname")
            lastjob.JobSizeBytes = fields.get("jobsizebytes")
            lastjob.Exists = 1
        return lastjob
            
    def getGroupMembersFromBackend(self, group) :        
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
        
    def getUserGroupsFromBackend(self, user) :        
        """Returns the user's groups list."""
        groups = []
        result = self.doSearch("SELECT groupname FROM groupsmembers JOIN groups ON groupsmembers.groupid=groups.id WHERE userid=%s" % self.doQuote(user.ident))
        if result :
            for record in result :
                groups.append(self.getGroup(record.get("groupname")))
        return groups        
        
    def getParentPrintersFromBackend(self, printer) :    
        """Get all the printer groups this printer is a member of."""
        pgroups = []
        result = self.doSearch("SELECT groupid,printername FROM printergroupsmembers JOIN printers ON groupid=id WHERE printerid=%s" % self.doQuote(printer.ident))
        if result :
            for record in result :
                if record["groupid"] != printer.ident : # in case of integrity violation
                    parentprinter = self.getPrinter(record.get("printername"))
                    if parentprinter.Exists :
                        pgroups.append(parentprinter)
        return pgroups
        
    def getMatchingPrinters(self, printerpattern) :
        """Returns the list of all printers for which name matches a certain pattern."""
        printers = []
        # We 'could' do a SELECT printername FROM printers WHERE printername LIKE ...
        # but we don't because other storages semantics may be different, so every
        # storage should use fnmatch to match patterns and be storage agnostic
        result = self.doSearch("SELECT * FROM printers")
        if result :
            for record in result :
                if self.tool.matchString(record["printername"], printerpattern.split(",")) :
                    printer = StoragePrinter(self, record["printername"])
                    printer.ident = record.get("id")
                    printer.PricePerJob = record.get("priceperjob") or 0.0
                    printer.PricePerPage = record.get("priceperpage") or 0.0
                    printer.Description = (record.get("description") or "").decode("UTF-8").encode(self.tool.getCharset()) 
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
        self.doModify("INSERT INTO users (username, limitby, balance, lifetimepaid, email) VALUES (%s, %s, %s, %s, %s)" % (self.doQuote(user.Name), self.doQuote(user.LimitBy or 'quota'), self.doQuote(user.AccountBalance or 0.0), self.doQuote(user.LifeTimePaid or 0.0), self.doQuote(user.Email)))
        return self.getUser(user.Name)
        
    def addGroup(self, group) :        
        """Adds a group to the quota storage, returns its id."""
        self.doModify("INSERT INTO groups (groupname, limitby) VALUES (%s, %s)" % (self.doQuote(group.Name), self.doQuote(group.LimitBy or "quota")))
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
        
    def writePrinterDescription(self, printer) :    
        """Write the printer's description back into the storage."""
        description = printer.Description
        if description is not None :
            description = printer.Description.decode(self.tool.getCharset()).encode("UTF-8"), 
        self.doModify("UPDATE printers SET description=%s WHERE id=%s" % (self.doQuote(description), self.doQuote(printer.ident)))
        
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
        
    def increaseUserPQuotaPagesCounters(self, userpquota, nbpages) :    
        """Increase page counters for a user print quota."""
        self.doModify("UPDATE userpquota SET pagecounter=pagecounter+%s,lifepagecounter=lifepagecounter+%s WHERE id=%s" % (self.doQuote(nbpages), self.doQuote(nbpages), self.doQuote(userpquota.ident)))
       
    def writeUserPQuotaPagesCounters(self, userpquota, newpagecounter, newlifepagecounter) :    
        """Sets the new page counters permanently for a user print quota."""
        self.doModify("UPDATE userpquota SET pagecounter=%s,lifepagecounter=%s WHERE id=%s" % (self.doQuote(newpagecounter), self.doQuote(newlifepagecounter), self.doQuote(userpquota.ident)))
       
    def decreaseUserAccountBalance(self, user, amount) :    
        """Decreases user's account balance from an amount."""
        self.doModify("UPDATE users SET balance=balance-%s WHERE id=%s" % (self.doQuote(amount), self.doQuote(user.ident)))
       
    def writeUserAccountBalance(self, user, newbalance, newlifetimepaid=None) :    
        """Sets the new account balance and eventually new lifetime paid."""
        if newlifetimepaid is not None :
            self.doModify("UPDATE users SET balance=%s, lifetimepaid=%s WHERE id=%s" % (self.doQuote(newbalance), self.doQuote(newlifetimepaid), self.doQuote(user.ident)))
        else :    
            self.doModify("UPDATE users SET balance=%s WHERE id=%s" % (self.doQuote(newbalance), self.doQuote(user.ident)))
            
    def writeNewPayment(self, user, amount) :        
        """Adds a new payment to the payments history."""
        self.doModify("INSERT INTO payments (userid, amount) VALUES (%s, %s)" % (self.doQuote(user.ident), self.doQuote(amount)))
        
    def writeLastJobSize(self, lastjob, jobsize, jobprice) :        
        """Sets the last job's size permanently."""
        self.doModify("UPDATE jobhistory SET jobsize=%s, jobprice=%s WHERE id=%s" % (self.doQuote(jobsize), self.doQuote(jobprice), self.doQuote(lastjob.ident)))
        
    def writeJobNew(self, printer, user, jobid, pagecounter, action, jobsize=None, jobprice=None, filename=None, title=None, copies=None, options=None, clienthost=None, jobsizebytes=None) :
        """Adds a job in a printer's history."""
        if filename is not None :
            filename = filename.decode(self.tool.getCharset()).encode("UTF-8")
        if title is not None :
            title = title.decode(self.tool.getCharset()).encode("UTF-8")
        if options is not None :
            options = options.decode(self.tool.getCharset()).encode("UTF-8")
        if (not self.disablehistory) or (not printer.LastJob.Exists) :
            if jobsize is not None :
                self.doModify("INSERT INTO jobhistory (userid, printerid, jobid, pagecounter, action, jobsize, jobprice, filename, title, copies, options, hostname, jobsizebytes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (self.doQuote(user.ident), self.doQuote(printer.ident), self.doQuote(jobid), self.doQuote(pagecounter), self.doQuote(action), self.doQuote(jobsize), self.doQuote(jobprice), self.doQuote(filename), self.doQuote(title), self.doQuote(copies), self.doQuote(options), self.doQuote(clienthost), self.doQuote(jobsizebytes)))
            else :    
                self.doModify("INSERT INTO jobhistory (userid, printerid, jobid, pagecounter, action, filename, title, copies, options, hostname, jobsizebytes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (self.doQuote(user.ident), self.doQuote(printer.ident), self.doQuote(jobid), self.doQuote(pagecounter), self.doQuote(action), self.doQuote(filename), self.doQuote(title), self.doQuote(copies), self.doQuote(options), self.doQuote(clienthost), self.doQuote(jobsizebytes)))
        else :        
            # here we explicitly want to reset jobsize to NULL if needed
            self.doModify("UPDATE jobhistory SET userid=%s, jobid=%s, pagecounter=%s, action=%s, jobsize=%s, jobprice=%s, filename=%s, title=%s, copies=%s, options=%s, hostname=%s, jobsizebytes=%s, jobdate=now() WHERE id=%s" % (self.doQuote(user.ident), self.doQuote(jobid), self.doQuote(pagecounter), self.doQuote(action), self.doQuote(jobsize), self.doQuote(jobprice), self.doQuote(filename), self.doQuote(title), self.doQuote(copies), self.doQuote(options), self.doQuote(clienthost), self.doQuote(jobsizebytes), self.doQuote(printer.LastJob.ident)))
            
    def writeUserPQuotaLimits(self, userpquota, softlimit, hardlimit) :
        """Sets soft and hard limits for a user quota."""
        self.doModify("UPDATE userpquota SET softlimit=%s, hardlimit=%s, datelimit=NULL WHERE id=%s" % (self.doQuote(softlimit), self.doQuote(hardlimit), self.doQuote(userpquota.ident)))
        
    def writeGroupPQuotaLimits(self, grouppquota, softlimit, hardlimit) :
        """Sets soft and hard limits for a group quota on a specific printer."""
        self.doModify("UPDATE grouppquota SET softlimit=%s, hardlimit=%s, datelimit=NULL WHERE id=%s" % (self.doQuote(softlimit), self.doQuote(hardlimit), self.doQuote(grouppquota.ident)))

    def writePrinterToGroup(self, pgroup, printer) :
        """Puts a printer into a printer group."""
        children = []
        result = self.doSearch("SELECT printerid FROM printergroupsmembers WHERE groupid=%s" % self.doQuote(pgroup.ident))
        if result :
            for record in result :
                children.append(record.get("printerid")) # TODO : put this into the database integrity rules
        if printer.ident not in children :        
            self.doModify("INSERT INTO printergroupsmembers (groupid, printerid) VALUES (%s, %s)" % (self.doQuote(pgroup.ident), self.doQuote(printer.ident)))
        
    def removePrinterFromGroup(self, pgroup, printer) :
        """Removes a printer from a printer group."""
        self.doModify("DELETE FROM printergroupsmembers WHERE groupid=%s AND printerid=%s" % (self.doQuote(pgroup.ident), self.doQuote(printer.ident)))
        
    def retrieveHistory(self, user=None, printer=None, datelimit=None, hostname=None, limit=100) :    
        """Retrieves all print jobs for user on printer (or all) before date, limited to first 100 results."""
        query = "SELECT jobhistory.*,username,printername FROM jobhistory,users,printers WHERE users.id=userid AND printers.id=printerid"
        where = []
        if (user is not None) and user.Exists :
            where.append("userid=%s" % self.doQuote(user.ident))
        if (printer is not None) and printer.Exists :
            where.append("printerid=%s" % self.doQuote(printer.ident))
        if hostname is not None :    
            where.append("hostname=%s" % self.doQuote(hostname))
        if datelimit is not None :    
            where.append("jobdate<=%s" % self.doQuote(datelimit))
        if where :    
            query += " AND %s" % " AND ".join(where)
        query += " ORDER BY id DESC"
        if limit :
            query += " LIMIT %s" % self.doQuote(int(limit))
        jobs = []    
        result = self.doSearch(query)    
        if result :
            for fields in result :
                job = StorageJob(self)
                job.ident = fields.get("id")
                job.JobId = fields.get("jobid")
                job.PrinterPageCounter = fields.get("pagecounter")
                job.JobSize = fields.get("jobsize")
                job.JobPrice = fields.get("jobprice")
                job.JobAction = fields.get("action")
                job.JobFileName = (fields.get("filename") or "").decode("UTF-8").encode(self.tool.getCharset()) 
                job.JobTitle = (fields.get("title") or "").decode("UTF-8").encode(self.tool.getCharset()) 
                job.JobCopies = fields.get("copies")
                job.JobOptions = (fields.get("options") or "").decode("UTF-8").encode(self.tool.getCharset()) 
                job.JobDate = fields.get("jobdate")
                job.JobHostName = fields.get("hostname")
                job.JobSizeBytes = fields.get("jobsizebytes")
                job.UserName = fields.get("username")
                job.PrinterName = fields.get("printername")
                job.Exists = 1
                jobs.append(job)
        return jobs
        
    def deleteUser(self, user) :    
        """Completely deletes an user from the Quota Storage."""
        # TODO : What should we do if we delete the last person who used a given printer ?
        # TODO : we can't reassign the last job to the previous one, because next user would be
        # TODO : incorrectly charged (overcharged).
        for q in [ 
                    "DELETE FROM payments WHERE userid=%s" % self.doQuote(user.ident),
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
            
    def deletePrinter(self, printer) :    
        """Completely deletes a printer from the Quota Storage."""
        for q in [ 
                    "DELETE FROM printergroupsmembers WHERE groupid=%s OR printerid=%s" % (self.doQuote(printer.ident), self.doQuote(printer.ident)),
                    "DELETE FROM jobhistory WHERE printerid=%s" % self.doQuote(printer.ident),
                    "DELETE FROM grouppquota WHERE printerid=%s" % self.doQuote(printer.ident),
                    "DELETE FROM userpquota WHERE printerid=%s" % self.doQuote(printer.ident),
                    "DELETE FROM printers WHERE id=%s" % self.doQuote(printer.ident),
                  ] :
            self.doModify(q)
        
