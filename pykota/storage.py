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
        newbalance = float(self.AccountBalance or 0.0) - amount
        self.parent.writeUserAccountBalance(self, newbalance)
        self.AccountBalance = newbalance
        
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
        
    def addJobToHistory(self, jobid, user, pagecounter, action, jobsize=None) :    
        """Adds a job to the printer's history."""
        self.parent.writeJobNew(self, user, jobid, pagecounter, action, jobsize)
        # TODO : update LastJob object ? Probably not needed.
        
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
        
    def increasePagesUsage(self, nbpages) :
        """Increase the value of used pages and money."""
        if nbpages :
            jobprice = (float(self.Printer.PricePerPage or 0.0) * nbpages) + float(self.Printer.PricePerJob or 0.0)
            newpagecounter = int(self.PageCounter or 0) + nbpages
            newlifepagecounter = int(self.LifePageCounter or 0) + nbpages
            self.parent.beginTransaction()
            try :
                if jobprice : # optimization : don't access the database if unneeded.
                    self.User.consumeAccountBalance(jobprice)
                self.parent.writeUserPQuotaPagesCounters(self, newpagecounter, newlifepagecounter)
            except PyKotaStorageError, msg :    
                self.parent.rollbackTransaction()
                raise PyKotaStorageError, msg
            else :    
                self.parent.commitTransaction()
                self.PageCounter = newpagecounter
                self.LifePageCounter = newlifepagecounter
        
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
        
class StorageLastJob(StorageObject) :
    """Printer's Last Job class."""
    def __init__(self, parent, printer) :
        StorageObject.__init__(self, parent)
        self.Printer = printer
        self.JobId = None
        self.User = None
        self.PrinterPageCounter = None
        self.JobSize = None
        self.JobAction = None
        self.JobDate = None
        
    def setSize(self, jobsize) :
        """Sets the last job's size."""
        self.parent.writeLastJobSize(self, jobsize)
        self.JobSize = jobsize
    
class BaseStorage :
    def __init__(self, pykotatool) :
        """Opens the LDAP connection."""
        # raise PyKotaStorageError, "Sorry, the LDAP backend for PyKota is not yet implemented !"
        self.closed = 1
        self.tool = pykotatool
        self.usecache = pykotatool.config.getCaching()
        if self.usecache :
            self.tool.logdebug("Caching enabled.")
            self.caches = { "USERS" : {}, "GROUPS" : {}, "PRINTERS" : {}, "USERPQUOTAS" : {}, "GROUPPQUOTAS" : {}, "JOBS" : {}, "LASTJOBS" : {} }
        
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
        if self.usecache :
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
        
def openConnection(pykotatool) :
    """Returns a connection handle to the appropriate Quota Storage Database."""
    backendinfo = pykotatool.config.getStorageBackend()
    backend = backendinfo["storagebackend"]
    try :
        if not backend.isalpha() :
            # don't trust user input
            raise ImportError
        #    
        # TODO : descending compatibility
        # 
        if backend == "postgresql" :
            backend = "pgstorage"       # TODO : delete, this is for descending compatibility only
        exec "from pykota.storages import %s as storagebackend" % backend.lower()    
    except ImportError :
        raise PyKotaStorageError, _("Unsupported quota storage backend %s") % backend
    else :    
        host = backendinfo["storageserver"]
        database = backendinfo["storagename"]
        admin = backendinfo["storageadmin"] or backendinfo["storageuser"]
        adminpw = backendinfo["storageadminpw"] or backendinfo["storageuserpw"]
        return getattr(storagebackend, "Storage")(pykotatool, host, database, admin, adminpw)

