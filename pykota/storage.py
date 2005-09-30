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

from mx import DateTime

class PyKotaStorageError(Exception):
    """An exception for Quota Storage related stuff."""
    def __init__(self, message = ""):
        self.message = message
        Exception.__init__(self, message)
    def __repr__(self):
        return self.message
    __str__ = __repr__
        
class StorageObject :
    """Object present in the Quota Storage."""
    def __init__(self, parent) :
        "Initialize minimal data."""
        self.parent = parent
        self.ident = None
        self.Exists = 0
        
class StorageUser(StorageObject) :        
    """User class."""
    def __init__(self, parent, name) :
        StorageObject.__init__(self, parent)
        self.Name = name
        self.LimitBy = None
        self.AccountBalance = None
        self.LifeTimePaid = None
        self.Email = None
        self.OverCharge = 1.0
        self.Payments = [] # TODO : maybe handle this smartly for SQL, for now just don't retrieve them
        
    def consumeAccountBalance(self, amount) :     
        """Consumes an amount of money from the user's account balance."""
        self.parent.decreaseUserAccountBalance(self, amount)
        self.AccountBalance = float(self.AccountBalance or 0.0) - amount
        
    def setAccountBalance(self, balance, lifetimepaid, comment="") :
        """Sets the user's account balance in case he pays more money."""
        diff = float(lifetimepaid or 0.0) - float(self.LifeTimePaid or 0.0)
        self.parent.beginTransaction()
        try :
            self.parent.writeUserAccountBalance(self, balance, lifetimepaid)
            self.parent.writeNewPayment(self, diff, comment)
        except PyKotaStorageError, msg :    
            self.parent.rollbackTransaction()
            raise PyKotaStorageError, msg
        else :    
            self.parent.commitTransaction()
            self.AccountBalance = balance
            self.LifeTimePaid = lifetimepaid
        
    def setLimitBy(self, limitby) :    
        """Sets the user's limiting factor."""
        try :
            limitby = limitby.lower()
        except AttributeError :    
            limitby = "quota"
        if limitby in ["quota", "balance", \
                       "noquota", "noprint", "nochange"] :
            self.parent.writeUserLimitBy(self, limitby)
            self.LimitBy = limitby
        
    def setOverChargeFactor(self, factor) :    
        """Sets the user's overcharging coefficient."""
        self.parent.writeUserOverCharge(self, factor)
        self.OverCharge = factor
        
    def delete(self) :    
        """Deletes an user from the Quota Storage."""
        self.parent.beginTransaction()
        try :
            self.parent.deleteUser(self)
        except PyKotaStorageError, msg :    
            self.parent.rollbackTransaction()
            raise PyKotaStorageError, msg
        else :    
            self.parent.commitTransaction()
            self.parent.flushEntry("USERS", self.Name)
            if self.parent.usecache :
                for (k, v) in self.parent.caches["USERPQUOTAS"].items() :
                    if v.User.Name == self.Name :
                        self.parent.flushEntry("USERPQUOTAS", "%s@%s" % (v.User.Name, v.Printer.Name))
            self.Exists = 0
        
class StorageGroup(StorageObject) :        
    """User class."""
    def __init__(self, parent, name) :
        StorageObject.__init__(self, parent)
        self.Name = name
        self.LimitBy = None
        self.AccountBalance = None
        self.LifeTimePaid = None
        
    def setLimitBy(self, limitby) :    
        """Sets the user's limiting factor."""
        try :
            limitby = limitby.lower()
        except AttributeError :    
            limitby = "quota"
        if limitby in ["quota", "balance", "noquota"] :
            self.parent.writeGroupLimitBy(self, limitby)
            self.LimitBy = limitby
        
    def delete(self) :    
        """Deletes a group from the Quota Storage."""
        self.parent.beginTransaction()
        try :
            self.parent.deleteGroup(self)
        except PyKotaStorageError, msg :    
            self.parent.rollbackTransaction()
            raise PyKotaStorageError, msg
        else :    
            self.parent.commitTransaction()
            self.parent.flushEntry("GROUPS", self.Name)
            if self.parent.usecache :
                for (k, v) in self.parent.caches["GROUPPQUOTAS"].items() :
                    if v.Group.Name == self.Name :
                        self.parent.flushEntry("GROUPPQUOTAS", "%s@%s" % (v.Group.Name, v.Printer.Name))
            self.Exists = 0
        
class StoragePrinter(StorageObject) :
    """Printer class."""
    def __init__(self, parent, name) :
        StorageObject.__init__(self, parent)
        self.Name = name
        self.PricePerPage = None
        self.PricePerJob = None
        self.Description = None
        self.MaxJobSize = None
        self.PassThrough = None
        self.Coefficients = None
        
    def __getattr__(self, name) :    
        """Delays data retrieval until it's really needed."""
        if name == "LastJob" : 
            self.LastJob = self.parent.getPrinterLastJob(self)
            return self.LastJob
        else :
            raise AttributeError, name
            
    def addJobToHistory(self, jobid, user, pagecounter, action, jobsize=None, jobprice=None, filename=None, title=None, copies=None, options=None, clienthost=None, jobsizebytes=None, jobmd5sum=None, jobpages=None, jobbilling=None, precomputedsize=None, precomputedprice=None) :
        """Adds a job to the printer's history."""
        self.parent.writeJobNew(self, user, jobid, pagecounter, action, jobsize, jobprice, filename, title, copies, options, clienthost, jobsizebytes, jobmd5sum, jobpages, jobbilling, precomputedsize, precomputedprice)
        # TODO : update LastJob object ? Probably not needed.
        
    def addPrinterToGroup(self, printer) :    
        """Adds a printer to a printer group."""
        if (printer not in self.parent.getParentPrinters(self)) and (printer.ident != self.ident) :
            self.parent.writePrinterToGroup(self, printer)
            # TODO : reset cached value for printer parents, or add new parent to cached value
            
    def delPrinterFromGroup(self, printer) :    
        """Deletes a printer from a printer group."""
        self.parent.removePrinterFromGroup(self, printer)
        # TODO : reset cached value for printer parents, or add new parent to cached value
        
    def setPrices(self, priceperpage = None, priceperjob = None) :    
        """Sets the printer's prices."""
        if priceperpage is None :
            priceperpage = self.PricePerPage or 0.0
        else :    
            self.PricePerPage = float(priceperpage)
        if priceperjob is None :    
            priceperjob = self.PricePerJob or 0.0
        else :    
            self.PricePerJob = float(priceperjob)
        self.parent.writePrinterPrices(self)
        
    def setDescription(self, description=None) :
        """Sets the printer's description."""
        if description is None :
            description = self.Description
        else :    
            self.Description = str(description)
        self.parent.writePrinterDescription(self)
        
    def delete(self) :    
        """Deletes a printer from the Quota Storage."""
        self.parent.beginTransaction()
        try :
            self.parent.deletePrinter(self)
        except PyKotaStorageError, msg :    
            self.parent.rollbackTransaction()
            raise PyKotaStorageError, msg
        else :    
            self.parent.commitTransaction()
            self.parent.flushEntry("PRINTERS", self.Name)
            if self.parent.usecache :
                for (k, v) in self.parent.caches["USERPQUOTAS"].items() :
                    if v.Printer.Name == self.Name :
                        self.parent.flushEntry("USERPQUOTAS", "%s@%s" % (v.User.Name, v.Printer.Name))
                for (k, v) in self.parent.caches["GROUPPQUOTAS"].items() :
                    if v.Printer.Name == self.Name :
                        self.parent.flushEntry("GROUPPQUOTAS", "%s@%s" % (v.Group.Name, v.Printer.Name))
            self.Exists = 0    
        
class StorageUserPQuota(StorageObject) :
    """User Print Quota class."""
    def __init__(self, parent, user, printer) :
        StorageObject.__init__(self, parent)
        self.User = user
        self.Printer = printer
        self.PageCounter = None
        self.LifePageCounter = None
        self.SoftLimit = None
        self.HardLimit = None
        self.DateLimit = None
        self.WarnCount = None
        self.MaxJobSize = None
        
    def __getattr__(self, name) :    
        """Delays data retrieval until it's really needed."""
        if name == "ParentPrintersUserPQuota" : 
            self.ParentPrintersUserPQuota = (self.User.Exists and self.Printer.Exists and self.parent.getParentPrintersUserPQuota(self)) or []
            return self.ParentPrintersUserPQuota
        else :
            raise AttributeError, name
        
    def setDateLimit(self, datelimit) :    
        """Sets the date limit for this quota."""
        date = "%04i-%02i-%02i %02i:%02i:%02i" % (datelimit.year, datelimit.month, datelimit.day, datelimit.hour, datelimit.minute, datelimit.second)
        self.parent.writeUserPQuotaDateLimit(self, date)
        self.DateLimit = date
        
    def setLimits(self, softlimit, hardlimit) :    
        """Sets the soft and hard limit for this quota."""
        self.parent.writeUserPQuotaLimits(self, softlimit, hardlimit)
        self.SoftLimit = softlimit
        self.HardLimit = hardlimit
        self.DateLimit = None
        self.WarnCount = 0
        
    def setUsage(self, used) :
        """Sets the PageCounter and LifePageCounter to used, or if used is + or - prefixed, changes the values of {Life,}PageCounter by that amount."""
        vused = int(used)
        if used.startswith("+") or used.startswith("-") :
            self.parent.beginTransaction()
            try :
                self.parent.increaseUserPQuotaPagesCounters(self, vused)
                self.parent.writeUserPQuotaDateLimit(self, None)
                self.parent.writeUserPQuotaWarnCount(self, 0)
            except PyKotaStorageError, msg :    
                self.parent.rollbackTransaction()
                raise PyKotaStorageError, msg
            else :
                self.parent.commitTransaction()
            self.PageCounter += vused
            self.LifePageCounter += vused
        else :
            self.parent.writeUserPQuotaPagesCounters(self, vused, vused)
            self.PageCounter = self.LifePageCounter = vused
        self.DateLimit = None
        self.WarnCount = 0

    def incDenyBannerCounter(self) :
        """Increment the deny banner counter for this user quota."""
        self.parent.increaseUserPQuotaWarnCount(self)
        self.WarnCount = (self.WarnCount or 0) + 1
        
    def resetDenyBannerCounter(self) :
        """Resets the deny banner counter for this user quota."""
        self.parent.writeUserPQuotaWarnCount(self, 0)
        self.WarnCount = 0
        
    def reset(self) :    
        """Resets page counter to 0."""
        self.parent.writeUserPQuotaPagesCounters(self, 0, int(self.LifePageCounter or 0))
        self.PageCounter = 0
        self.DateLimit = None
        
    def hardreset(self) :    
        """Resets actual and life time page counters to 0."""
        self.parent.writeUserPQuotaPagesCounters(self, 0, 0)
        self.PageCounter = self.LifePageCounter = 0
        self.DateLimit = None
        
    def computeJobPrice(self, jobsize) :    
        """Computes the job price as the sum of all parent printers' prices + current printer's ones."""
        totalprice = 0.0    
        if jobsize :
            if self.User.OverCharge != 0.0 :    # optimization, but TODO : beware of rounding errors
                for upq in [ self ] + self.ParentPrintersUserPQuota :
                    price = (float(upq.Printer.PricePerPage or 0.0) * jobsize) + float(upq.Printer.PricePerJob or 0.0)
                    totalprice += price
        if self.User.OverCharge != 1.0 : # TODO : beware of rounding errors
            overcharged = totalprice * self.User.OverCharge        
            self.parent.tool.logdebug("Overcharging %s by a factor of %s ===> User %s will be charged for %s units." % (totalprice, self.User.OverCharge, self.User.Name, overcharged))
            return overcharged
        else :    
            return totalprice
            
    def increasePagesUsage(self, jobsize) :
        """Increase the value of used pages and money."""
        jobprice = self.computeJobPrice(jobsize)
        if jobsize :
            if jobprice :
                self.User.consumeAccountBalance(jobprice)
            for upq in [ self ] + self.ParentPrintersUserPQuota :
                self.parent.increaseUserPQuotaPagesCounters(upq, jobsize)
                upq.PageCounter = int(upq.PageCounter or 0) + jobsize
                upq.LifePageCounter = int(upq.LifePageCounter or 0) + jobsize
        return jobprice
        
class StorageGroupPQuota(StorageObject) :
    """Group Print Quota class."""
    def __init__(self, parent, group, printer) :
        StorageObject.__init__(self, parent)
        self.Group = group
        self.Printer = printer
        self.PageCounter = None
        self.LifePageCounter = None
        self.SoftLimit = None
        self.HardLimit = None
        self.DateLimit = None
        self.MaxJobSize = None
        
    def __getattr__(self, name) :    
        """Delays data retrieval until it's really needed."""
        if name == "ParentPrintersGroupPQuota" : 
            self.ParentPrintersGroupPQuota = (self.Group.Exists and self.Printer.Exists and self.parent.getParentPrintersGroupPQuota(self)) or []
            return self.ParentPrintersGroupPQuota
        else :
            raise AttributeError, name
        
    def reset(self) :    
        """Resets page counter to 0."""
        self.parent.beginTransaction()
        try :
            for user in self.parent.getGroupMembers(self.Group) :
                uq = self.parent.getUserPQuota(user, self.Printer)
                uq.reset()
            self.parent.writeGroupPQuotaDateLimit(self, None)
        except PyKotaStorageError, msg :    
            self.parent.rollbackTransaction()
            raise PyKotaStorageError, msg
        else :    
            self.parent.commitTransaction()
        self.PageCounter = 0
        self.DateLimit = None
        
    def hardreset(self) :    
        """Resets actual and life time page counters to 0."""
        self.parent.beginTransaction()
        try :
            for user in self.parent.getGroupMembers(self.Group) :
                uq = self.parent.getUserPQuota(user, self.Printer)
                uq.hardreset()
            self.parent.writeGroupPQuotaDateLimit(self, None)
        except PyKotaStorageError, msg :    
            self.parent.rollbackTransaction()
            raise PyKotaStorageError, msg
        else :    
            self.parent.commitTransaction()
        self.PageCounter = self.LifePageCounter = 0
        self.DateLimit = None
        
    def setDateLimit(self, datelimit) :    
        """Sets the date limit for this quota."""
        date = "%04i-%02i-%02i %02i:%02i:%02i" % (datelimit.year, \
                                                  datelimit.month, \
                                                  datelimit.day, \
                                                  datelimit.hour, \
                                                  datelimit.minute, \
                                                  datelimit.second)
        self.parent.writeGroupPQuotaDateLimit(self, date)
        self.DateLimit = date
        
    def setLimits(self, softlimit, hardlimit) :    
        """Sets the soft and hard limit for this quota."""
        self.parent.writeGroupPQuotaLimits(self, softlimit, hardlimit)
        self.SoftLimit = softlimit
        self.HardLimit = hardlimit
        self.DateLimit = None
        
class StorageJob(StorageObject) :
    """Printer's Job class."""
    def __init__(self, parent) :
        StorageObject.__init__(self, parent)
        self.UserName = None
        self.PrinterName = None
        self.JobId = None
        self.PrinterPageCounter = None
        self.JobSizeBytes = None
        self.JobSize = None
        self.JobAction = None
        self.JobDate = None
        self.JobPrice = None
        self.JobFileName = None
        self.JobTitle = None
        self.JobCopies = None
        self.JobOptions = None
        self.JobHostName = None
        self.JobMD5Sum = None
        self.JobPages = None
        self.JobBillingCode = None
        self.PrecomputedJobSize = None
        self.PrecomputedJobPrice = None
        
    def __getattr__(self, name) :    
        """Delays data retrieval until it's really needed."""
        if name == "User" : 
            self.User = self.parent.getUser(self.UserName)
            return self.User
        elif name == "Printer" :    
            self.Printer = self.parent.getPrinter(self.PrinterName)
            return self.Printer
        else :
            raise AttributeError, name
        
class StorageLastJob(StorageJob) :
    """Printer's Last Job class."""
    def __init__(self, parent, printer) :
        StorageJob.__init__(self, parent)
        self.PrinterName = printer.Name # not needed
        self.Printer = printer
        
class StorageBillingCode(StorageObject) :
    """Billing code class."""
    def __init__(self, parent, name) :
        StorageObject.__init__(self, parent)
        self.BillingCode = name
        self.Description = None
        self.PageCounter = None
        self.Balance = None
        
    def delete(self) :    
        """Deletes the billing code from the database."""
        self.parent.deleteBillingCode(self)
        self.parent.flushEntry("BILLINGCODES", self.BillingCode)
        self.Exists = 0
        
    def reset(self, balance=0.0, pagecounter=0) :    
        """Resets the pagecounter and balance for this billing code."""
        self.parent.setBillingCodeValues(self, pagecounter, balance)
        self.Balance = balance
        self.PageCounter = pagecounter
        
    def setDescription(self, description=None) :
        """Modifies the description for this billing code."""
        if description is None :
            description = self.Description
        else :    
            self.Description = str(description)
        self.parent.writeBillingCodeDescription(self)
        
    def consume(self, pages, price) :
        """Consumes some pages and credits for this billing code."""
        if pages :
           self.parent.consumeBillingCode(self, pages, price)
           self.PageCounter += pages
           self.Balance -= price
        
class BaseStorage :
    def __init__(self, pykotatool) :
        """Opens the storage connection."""
        self.closed = 1
        self.tool = pykotatool
        self.usecache = pykotatool.config.getCaching()
        self.disablehistory = pykotatool.config.getDisableHistory()
        self.privacy = pykotatool.config.getPrivacy()
        if self.privacy :
            pykotatool.logdebug("Jobs' title, filename and options will be hidden because of privacy concerns.")
        if self.usecache :
            self.tool.logdebug("Caching enabled.")
            self.caches = { "USERS" : {}, \
                            "GROUPS" : {}, \
                            "PRINTERS" : {}, \
                            "USERPQUOTAS" : {}, \
                            "GROUPPQUOTAS" : {}, \
                            "JOBS" : {}, \
                            "LASTJOBS" : {}, \
                            "BILLINGCODES" : {} }
        
    def close(self) :    
        """Must be overriden in children classes."""
        raise RuntimeError, "BaseStorage.close() must be overriden !"
        
    def __del__(self) :        
        """Ensures that the database connection is closed."""
        self.close()
        
    def getFromCache(self, cachetype, key) :
        """Tries to extract something from the cache."""
        if self.usecache :
            entry = self.caches[cachetype].get(key)
            if entry is not None :
                self.tool.logdebug("Cache hit (%s->%s)" % (cachetype, key))
            else :    
                self.tool.logdebug("Cache miss (%s->%s)" % (cachetype, key))
            return entry    
            
    def cacheEntry(self, cachetype, key, value) :        
        """Puts an entry in the cache."""
        if self.usecache and getattr(value, "Exists", 0) :
            self.caches[cachetype][key] = value
            self.tool.logdebug("Cache store (%s->%s)" % (cachetype, key))
            
    def flushEntry(self, cachetype, key) :        
        """Removes an entry from the cache."""
        if self.usecache :
            try :
                del self.caches[cachetype][key]
            except KeyError :    
                pass
            else :    
                self.tool.logdebug("Cache flush (%s->%s)" % (cachetype, key))
            
    def getUser(self, username) :        
        """Returns the user from cache."""
        user = self.getFromCache("USERS", username)
        if user is None :
            user = self.getUserFromBackend(username)
            self.cacheEntry("USERS", username, user)
        return user    
        
    def getGroup(self, groupname) :        
        """Returns the group from cache."""
        group = self.getFromCache("GROUPS", groupname)
        if group is None :
            group = self.getGroupFromBackend(groupname)
            self.cacheEntry("GROUPS", groupname, group)
        return group    
        
    def getPrinter(self, printername) :        
        """Returns the printer from cache."""
        printer = self.getFromCache("PRINTERS", printername)
        if printer is None :
            printer = self.getPrinterFromBackend(printername)
            self.cacheEntry("PRINTERS", printername, printer)
        return printer    
        
    def getUserPQuota(self, user, printer) :        
        """Returns the user quota information from cache."""
        useratprinter = "%s@%s" % (user.Name, printer.Name)
        upquota = self.getFromCache("USERPQUOTAS", useratprinter)
        if upquota is None :
            upquota = self.getUserPQuotaFromBackend(user, printer)
            self.cacheEntry("USERPQUOTAS", useratprinter, upquota)
        return upquota    
        
    def getGroupPQuota(self, group, printer) :        
        """Returns the group quota information from cache."""
        groupatprinter = "%s@%s" % (group.Name, printer.Name)
        gpquota = self.getFromCache("GROUPPQUOTAS", groupatprinter)
        if gpquota is None :
            gpquota = self.getGroupPQuotaFromBackend(group, printer)
            self.cacheEntry("GROUPPQUOTAS", groupatprinter, gpquota)
        return gpquota    
        
    def getPrinterLastJob(self, printer) :        
        """Extracts last job information for a given printer from cache."""
        lastjob = self.getFromCache("LASTJOBS", printer.Name)
        if lastjob is None :
            lastjob = self.getPrinterLastJobFromBackend(printer)
            self.cacheEntry("LASTJOBS", printer.Name, lastjob)
        return lastjob    
        
    def getBillingCode(self, label) :        
        """Returns the user from cache."""
        code = self.getFromCache("BILLINGCODES", label)
        if code is None :
            code = self.getBillingCodeFromBackend(label)
            self.cacheEntry("BILLINGCODES", label, code)
        return code
        
    def getParentPrinters(self, printer) :    
        """Extracts parent printers information for a given printer from cache."""
        if self.usecache :
            if not hasattr(printer, "Parents") :
                self.tool.logdebug("Cache miss (%s->Parents)" % printer.Name)
                printer.Parents = self.getParentPrintersFromBackend(printer)
                self.tool.logdebug("Cache store (%s->Parents)" % printer.Name)
            else :
                self.tool.logdebug("Cache hit (%s->Parents)" % printer.Name)
        else :        
            printer.Parents = self.getParentPrintersFromBackend(printer)
        for parent in printer.Parents[:] :    
            printer.Parents.extend(self.getParentPrinters(parent))
        uniquedic = {}    
        for parent in printer.Parents :
            uniquedic[parent.Name] = parent
        printer.Parents = uniquedic.values()    
        return printer.Parents
        
    def getGroupMembers(self, group) :        
        """Returns the group's members list from in-group cache."""
        if self.usecache :
            if not hasattr(group, "Members") :
                self.tool.logdebug("Cache miss (%s->Members)" % group.Name)
                group.Members = self.getGroupMembersFromBackend(group)
                self.tool.logdebug("Cache store (%s->Members)" % group.Name)
            else :
                self.tool.logdebug("Cache hit (%s->Members)" % group.Name)
        else :        
            group.Members = self.getGroupMembersFromBackend(group)
        return group.Members    
        
    def getUserGroups(self, user) :        
        """Returns the user's groups list from in-user cache."""
        if self.usecache :
            if not hasattr(user, "Groups") :
                self.tool.logdebug("Cache miss (%s->Groups)" % user.Name)
                user.Groups = self.getUserGroupsFromBackend(user)
                self.tool.logdebug("Cache store (%s->Groups)" % user.Name)
            else :
                self.tool.logdebug("Cache hit (%s->Groups)" % user.Name)
        else :        
            user.Groups = self.getUserGroupsFromBackend(user)
        return user.Groups   
        
    def getParentPrintersUserPQuota(self, userpquota) :     
        """Returns all user print quota on the printer and all its parents recursively."""
        upquotas = [ ]
        for printer in self.getParentPrinters(userpquota.Printer) :
            upq = self.getUserPQuota(userpquota.User, printer)
            if upq.Exists :
                upquotas.append(upq)
        return upquotas        
        
    def getParentPrintersGroupPQuota(self, grouppquota) :     
        """Returns all group print quota on the printer and all its parents recursively."""
        gpquotas = [ ]
        for printer in self.getParentPrinters(grouppquota.Printer) :
            gpq = self.getGroupPQuota(grouppquota.Group, printer)
            if gpq.Exists :
                gpquotas.append(gpq)
        return gpquotas        
        
    def databaseToUserCharset(self, text) :
        """Converts from database format (UTF-8) to user's charset."""
        if text is not None :
            try :
                return unicode(text, "UTF-8").encode(self.tool.getCharset()) 
            except UnicodeError :    
                try :
                    # Incorrect locale settings ?
                    return unicode(text, "UTF-8").encode("ISO-8859-15") 
                except UnicodeError :    
                    pass
        return text
        
    def userCharsetToDatabase(self, text) :
        """Converts from user's charset to database format (UTF-8)."""
        if text is not None :
            try :
                return unicode(text, self.tool.getCharset()).encode("UTF-8") 
            except UnicodeError :    
                try :
                    # Incorrect locale settings ?
                    return unicode(text, "ISO-8859-15").encode("UTF-8") 
                except UnicodeError :    
                    pass
        return text
        
    def cleanDates(self, startdate, enddate) :    
        """Clean the dates to create a correct filter."""
        if startdate is None :
            startdate = enddate
        if enddate is None :    
            enddate = startdate
        if (startdate is None) and (enddate is None) :    
            return (None, None)
            
        now = DateTime.now()    
        nameddates = ('yesterday', 'today', 'now', 'tomorrow')
        datedict = { "start" : startdate.lower(), "end" : enddate.lower() }    
        for limit in datedict.keys() :
            dateval = datedict[limit]
            for name in nameddates :
                if dateval.startswith(name) :
                    try :
                        offset = int(dateval[len(name):])
                    except :    
                        offset = 0
                    dateval = dateval[:len(name)]    
                    if limit == "start" :
                        if dateval == "yesterday" :
                            dateval = (now - 1 + offset).Format("%Y%m%d000000")
                        elif dateval == "today" :
                            dateval = (now + offset).Format("%Y%m%d000000")
                        elif dateval == "now" :
                            dateval = (now + offset).Format("%Y%m%d%H%M%S")
                        else : # tomorrow
                            dateval = (now + 1 + offset).Format("%Y%m%d000000")
                    else :
                        if dateval == "yesterday" :
                            dateval = (now - 1 + offset).Format("%Y%m%d235959")
                        elif dateval == "today" :
                            dateval = (now + offset).Format("%Y%m%d235959")
                        elif dateval == "now" :
                            dateval = (now + offset).Format("%Y%m%d%H%M%S")
                        else : # tomorrow
                            dateval = (now + 1 + offset).Format("%Y%m%d235959")
                    break
                    
            if not dateval.isdigit() :
                dateval = None
            else :    
                lgdateval = len(dateval)
                if lgdateval == 4 :
                    if limit == "start" : 
                        dateval = "%s0101 00:00:00" % dateval
                    else :  
                        dateval = "%s1231 23:59:59" % dateval
                elif lgdateval == 6 :
                    if limit == "start" : 
                        dateval = "%s01 00:00:00" % dateval
                    else :  
                        mxdate = DateTime.ISO.ParseDateTime("%s01 00:00:00" % dateval)
                        dateval = "%s%02i 23:59:59" % (dateval, mxdate.days_in_month)
                elif lgdateval == 8 :
                    if limit == "start" : 
                        dateval = "%s 00:00:00" % dateval
                    else :  
                        dateval = "%s 23:59:59" % dateval
                elif lgdateval == 10 :
                    if limit == "start" : 
                        dateval = "%s %s:00:00" % (dateval[:8], dateval[8:])
                    else :  
                        dateval = "%s %s:59:59" % (dateval[:8], dateval[8:])
                elif lgdateval == 12 :
                    if limit == "start" : 
                        dateval = "%s %s:%s:00" % (dateval[:8], dateval[8:10], dateval[10:])
                    else :  
                        dateval = "%s %s:%s:59" % (dateval[:8], dateval[8:10], dateval[10:])
                elif lgdateval == 14 :        
                    dateval = "%s %s:%s:%s" % (dateval[:8], dateval[8:10], dateval[10:12], dateval[12:])
                else :    
                    dateval = None
                try :    
                    DateTime.ISO.ParseDateTime(dateval)
                except :    
                    dateval = None
            datedict[limit] = dateval    
        (start, end) = (datedict["start"], datedict["end"])
        if start > end :
            (start, end) = (end, start)
        return (start, end)    
        
def openConnection(pykotatool) :
    """Returns a connection handle to the appropriate Quota Storage Database."""
    backendinfo = pykotatool.config.getStorageBackend()
    backend = backendinfo["storagebackend"]
    try :
        exec "from pykota.storages import %s as storagebackend" % backend.lower()
    except ImportError :
        raise PyKotaStorageError, _("Unsupported quota storage backend %s") % backend
    else :    
        host = backendinfo["storageserver"]
        database = backendinfo["storagename"]
        admin = backendinfo["storageadmin"] or backendinfo["storageuser"]
        adminpw = backendinfo["storageadminpw"] or backendinfo["storageuserpw"]
        return storagebackend.Storage(pykotatool, host, database, admin, adminpw)

