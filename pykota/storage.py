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
# Revision 1.41  2004/02/04 17:12:33  jalet
# Removing a printer from a printers group should work now.
#
# Revision 1.40  2004/02/04 13:24:41  jalet
# pkprinters can now remove printers from printers groups.
#
# Revision 1.39  2004/02/04 11:16:59  jalet
# pkprinters command line tool added.
#
# Revision 1.38  2004/01/12 22:43:40  jalet
# New formula to compute a job's price
#
# Revision 1.37  2004/01/12 14:35:01  jalet
# Printing history added to CGI script.
#
# Revision 1.36  2004/01/10 09:44:02  jalet
# Fixed potential accuracy problem if a user printed on several printers at
# the very same time.
#
# Revision 1.35  2004/01/08 16:33:27  jalet
# Additionnal check to not create a circular printers group.
#
# Revision 1.34  2004/01/08 16:24:49  jalet
# edpykota now supports adding printers to printer groups.
#
# Revision 1.33  2004/01/08 14:10:32  jalet
# Copyright year changed.
#
# Revision 1.32  2004/01/06 16:02:57  jalet
# This time printer groups caching works.
#
# Revision 1.31  2004/01/06 15:51:24  jalet
# Fixed caching of printer groups
#
# Revision 1.30  2004/01/06 14:24:59  jalet
# Printer groups should be cached now, if caching is enabled.
#
# Revision 1.29  2003/12/27 16:49:25  uid67467
# Should be ok now.
#
# Revision 1.28  2003/11/25 23:46:40  jalet
# Don't try to verify if module name is valid, Python does this better than us.
#
# Revision 1.27  2003/11/23 19:01:36  jalet
# Job price added to history
#
# Revision 1.26  2003/11/21 14:28:45  jalet
# More complete job history.
#
# Revision 1.25  2003/10/08 21:12:27  jalet
# Do not cache anymore entries which don't exist.
#
# Revision 1.24  2003/10/07 22:06:05  jalet
# Preliminary code to disable job history
#
# Revision 1.23  2003/10/07 09:07:28  jalet
# Character encoding added to please latest version of Python
#
# Revision 1.22  2003/10/06 13:12:27  jalet
# More work on caching
#
# Revision 1.21  2003/10/03 09:02:20  jalet
# Logs cache store actions too
#
# Revision 1.20  2003/10/02 20:23:18  jalet
# Storage caching mechanism added.
#
# Revision 1.19  2003/07/16 21:53:07  jalet
# Really big modifications wrt new configuration file's location and content.
#
# Revision 1.18  2003/07/07 08:33:18  jalet
# Bug fix due to a typo in LDAP code
#
# Revision 1.17  2003/07/05 07:46:50  jalet
# The previous bug fix was incomplete.
#
# Revision 1.16  2003/06/25 19:52:31  jalet
# Should be ready for testing :-)
#
# Revision 1.15  2003/06/25 14:10:58  jalet
# Exception raising for now.
#
# Revision 1.14  2003/06/25 14:10:01  jalet
# Hey, it may work (edpykota --reset excepted) !
#
# Revision 1.13  2003/06/10 16:37:54  jalet
# Deletion of the second user which is not needed anymore.
# Added a debug configuration field in /etc/pykota.conf
# All queries can now be sent to the logger in debug mode, this will
# greatly help improve performance when time for this will come.
#
# Revision 1.12  2003/04/23 22:13:57  jalet
# Preliminary support for LPRng added BUT STILL UNTESTED.
#
# Revision 1.11  2003/04/10 21:47:20  jalet
# Job history added. Upgrade script neutralized for now !
#
# Revision 1.10  2003/03/29 13:45:27  jalet
# GPL paragraphs were incorrectly (from memory) copied into the sources.
# Two README files were added.
# Upgrade script for PostgreSQL pre 1.01 schema was added.
#
# Revision 1.9  2003/02/17 22:55:01  jalet
# More options can now be set per printer or globally :
#
#       admin
#       adminmail
#       gracedelay
#       requester
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
        
    def consumeAccountBalance(self, amount) :     
        """Consumes an amount of money from the user's account balance."""
        self.parent.decreaseUserAccountBalance(self, amount)
        self.AccountBalance = float(self.AccountBalance or 0.0) - amount
        
    def setAccountBalance(self, balance, lifetimepaid) :    
        """Sets the user's account balance in case he pays more money."""
        self.parent.writeUserAccountBalance(self, balance, lifetimepaid)
        self.AccountBalance = balance
        self.LifeTimePaid = lifetimepaid
        
    def setLimitBy(self, limitby) :    
        """Sets the user's limiting factor."""
        try :
            limitby = limitby.lower()
        except AttributeError :    
            limitby = "quota"
        if limitby in ["quota", "balance"] :
            self.parent.writeUserLimitBy(self, limitby)
            self.LimitBy = limitby
        
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
        if limitby in ["quota", "balance"] :
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
        
class StoragePrinter(StorageObject) :
    """Printer class."""
    def __init__(self, parent, name) :
        StorageObject.__init__(self, parent)
        self.Name = name
        self.PricePerPage = None
        self.PricePerJob = None
        self.LastJob = None
        
    def addJobToHistory(self, jobid, user, pagecounter, action, jobsize=None, jobprice=None, filename=None, title=None, copies=None, options=None) :
        """Adds a job to the printer's history."""
        self.parent.writeJobNew(self, user, jobid, pagecounter, action, jobsize, jobprice, filename, title, copies, options)
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
            priceperpage = self.PricePerPage
        else :    
            self.PricePerPage = float(priceperpage)
        if priceperjob is None :    
            priceperjob = self.PricePerJob
        else :    
            self.PricePerJob = float(priceperjob)
        self.parent.writePrinterPrices(self)
        
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
        self.ParentPrintersUserPQuota = (user.Exists and printer.Exists and parent.getParentPrintersUserPQuota(self)) or []
        
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
        
    def reset(self) :    
        """Resets page counter to 0."""
        self.parent.writeUserPQuotaPagesCounters(self, 0, int(self.LifePageCounter or 0))
        self.PageCounter = 0
        
    def computeJobPrice(self, jobsize) :    
        """Computes the job price as the sum of all parent printers' prices + current printer's ones."""
        totalprice = 0.0    
        if jobsize :
            for upq in [ self ] + self.ParentPrintersUserPQuota :
                price = (float(upq.Printer.PricePerPage or 0.0) * jobsize) + float(upq.Printer.PricePerJob or 0.0)
                totalprice += price
        return totalprice    
            
    def increasePagesUsage(self, jobsize) :
        """Increase the value of used pages and money."""
        jobprice = self.computeJobPrice(jobsize)
        if jobsize :
            self.parent.beginTransaction()
            try :
                self.User.consumeAccountBalance(jobprice)
                for upq in [ self ] + self.ParentPrintersUserPQuota :
                    self.parent.increaseUserPQuotaPagesCounters(upq, jobsize)
                    upq.PageCounter = int(upq.PageCounter or 0) + jobsize
                    upq.LifePageCounter = int(upq.LifePageCounter or 0) + jobsize
            except PyKotaStorageError, msg :    
                self.parent.rollbackTransaction()
                raise PyKotaStorageError, msg
            else :    
                self.parent.commitTransaction()
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
        
    def setDateLimit(self, datelimit) :    
        """Sets the date limit for this quota."""
        date = "%04i-%02i-%02i %02i:%02i:%02i" % (datelimit.year, datelimit.month, datelimit.day, datelimit.hour, datelimit.minute, datelimit.second)
        self.parent.writeGroupPQuotaDateLimit(self, date)
        self.DateLimit = date
        
    def setLimits(self, softlimit, hardlimit) :    
        """Sets the soft and hard limit for this quota."""
        self.parent.writeGroupPQuotaLimits(self, softlimit, hardlimit)
        self.SoftLimit = softlimit
        self.HardLimit = hardlimit
        
class StorageJob(StorageObject) :
    """Printer's Last Job class."""
    def __init__(self, parent) :
        StorageObject.__init__(self, parent)
        self.User = None
        self.Printer = None
        self.JobId = None
        self.PrinterPageCounter = None
        self.JobSize = None
        self.JobAction = None
        self.JobDate = None
        self.JobPrice = None
        self.JobFileName = None
        self.JobTitle = None
        self.JobCopies = None
        self.JobOptions = None
        
class StorageLastJob(StorageJob) :
    """Printer's Last Job class."""
    def __init__(self, parent, printer) :
        StorageJob.__init__(self, parent)
        self.Printer = printer
        
    def setSize(self, jobsize) :
        """Sets the last job's size."""
        jobprice = self.parent.getUserPQuota(self.User, self.Printer).computeJobPrice(jobsize)
        self.parent.writeLastJobSize(self, jobsize, jobprice)
        self.JobSize = jobsize
        self.JobPrice = jobprice
        
class BaseStorage :
    def __init__(self, pykotatool) :
        """Opens the LDAP connection."""
        # raise PyKotaStorageError, "Sorry, the LDAP backend for PyKota is not yet implemented !"
        self.closed = 1
        self.tool = pykotatool
        self.usecache = pykotatool.config.getCaching()
        self.disablehistory = pykotatool.config.getDisableHistory()
        if self.usecache :
            self.tool.logdebug("Caching enabled.")
            self.caches = { "USERS" : {}, "GROUPS" : {}, "PRINTERS" : {}, "USERPQUOTAS" : {}, "GROUPPQUOTAS" : {}, "JOBS" : {}, "LASTJOBS" : {} }
        
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
        """Returns all user print quota on the printer and its parents."""
        upquotas = [ ]
        for printer in self.getParentPrinters(userpquota.Printer) :
            upquotas.append(self.getUserPQuota(userpquota.User, printer))
        return upquotas        
        
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

