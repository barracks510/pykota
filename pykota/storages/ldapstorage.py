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
# Revision 1.15  2003/07/07 11:49:24  jalet
# Lots of small fixes with the help of PyChecker
#
# Revision 1.14  2003/07/07 08:33:18  jalet
# Bug fix due to a typo in LDAP code
#
# Revision 1.13  2003/07/05 07:46:50  jalet
# The previous bug fix was incomplete.
#
# Revision 1.12  2003/06/30 13:54:21  jalet
# Sorts by user / group name
#
# Revision 1.11  2003/06/25 14:10:01  jalet
# Hey, it may work (edpykota --reset excepted) !
#
# Revision 1.10  2003/06/16 21:55:15  jalet
# More work on LDAP, again. Problem detected.
#
# Revision 1.9  2003/06/16 11:59:09  jalet
# More work on LDAP
#
# Revision 1.8  2003/06/15 22:26:52  jalet
# More work on LDAP
#
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

import time
import md5

from pykota.storage import PyKotaStorageError
from pykota.storage import StorageObject,StorageUser,StorageGroup,StoragePrinter,StorageLastJob,StorageUserPQuota,StorageGroupPQuota

try :
    import ldap
    from ldap import modlist
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
        except ldap.LDAPError :    
            raise PyKotaStorageError, "Unable to connect to LDAP server %s as %s." % (host, user) # TODO : translate
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
        
    def genUUID(self) :    
        """Generates an unique identifier.
        
           TODO : this one is not unique accross several print servers, but should be sufficient for testing.
        """
        return md5.md5("%s" % time.time()).hexdigest()
        
    def beginTransaction(self) :    
        """Starts a transaction."""
        if self.debug :
            self.tool.logger.log_message("Transaction begins... WARNING : No transactions in LDAP !", "debug")
        
    def commitTransaction(self) :    
        """Commits a transaction."""
        if self.debug :
            self.tool.logger.log_message("Transaction committed. WARNING : No transactions in LDAP !", "debug")
        
    def rollbackTransaction(self) :     
        """Rollbacks a transaction."""
        if self.debug :
            self.tool.logger.log_message("Transaction aborted. WARNING : No transaction in LDAP !", "debug")
        
    def doSearch(self, key, fields=None, base="", scope=ldap.SCOPE_SUBTREE) :
        """Does an LDAP search query."""
        try :
            base = base or self.basedn
            if self.debug :
                self.tool.logger.log_message("QUERY : Filter : %s, BaseDN : %s, Scope : %s, Attributes : %s" % (key, base, scope, fields), "debug")
            result = self.database.search_s(base or self.basedn, scope, key, fields)
        except ldap.LDAPError :    
            raise PyKotaStorageError, _("Search for %s(%s) from %s(scope=%s) returned no answer.") % (key, fields, base, scope)
        else :     
            if self.debug :
                self.tool.logger.log_message("QUERY : Result : %s" % result, "debug")
            return result
            
    def doAdd(self, dn, fields) :
        """Adds an entry in the LDAP directory."""
        try :
            if self.debug :
                self.tool.logger.log_message("QUERY : ADD(%s, %s)" % (dn, str(fields)), "debug")
            self.database.add_s(dn, modlist.addModlist(fields))
        except ldap.LDAPError :
            raise PyKotaStorageError, _("Problem adding LDAP entry (%s, %s)") % (dn, str(fields))
        else :
            return dn
            
    def doDelete(self, dn) :
        """Deletes an entry from the LDAP directory."""
        try :
            if self.debug :
                self.tool.logger.log_message("QUERY : Delete(%s)" % dn, "debug")
            self.database.delete_s(dn)
        except ldap.LDAPError :
            raise PyKotaStorageError, _("Problem deleting LDAP entry (%s)") % dn
            
    def doModify(self, dn, fields, ignoreold=1) :
        """Modifies an entry in the LDAP directory."""
        try :
            oldentry = self.doSearch("objectClass=*", base=dn, scope=ldap.SCOPE_BASE)
            if self.debug :
                self.tool.logger.log_message("QUERY : Modify(%s, %s ==> %s)" % (dn, oldentry[0][1], fields), "debug")
            self.database.modify_s(dn, modlist.modifyModlist(oldentry[0][1], fields, ignore_oldexistent=ignoreold))
        except ldap.LDAPError :
            raise PyKotaStorageError, _("Problem modifying LDAP entry (%s, %s)") % (dn, fields)
        else :
            return dn
            
    def getUser(self, username) :    
        """Extracts user information given its name."""
        user = StorageUser(self, username)
        result = self.doSearch("(&(objectClass=pykotaAccount)(|(pykotaUserName=%s)(%s=%s)))" % (username, self.info["userrdn"], username), ["pykotaLimitBy"], base=self.info["userbase"])
        if result :
            fields = result[0][1]
            user.ident = result[0][0]
            user.LimitBy = fields.get("pykotaLimitBy")
            if user.LimitBy is not None :
                user.LimitBy = user.LimitBy[0]
            result = self.doSearch("(&(objectClass=pykotaAccountBalance)(|(pykotaUserName=%s)(%s=%s)))" % (username, self.info["balancerdn"], username), ["pykotaBalance", "pykotaLifeTimePaid"], base=self.info["balancebase"])
            if result :
                fields = result[0][1]
                user.idbalance = result[0][0]
                user.AccountBalance = fields.get("pykotaBalance")
                if user.AccountBalance is not None :
                    if user.AccountBalance[0].upper() == "NONE" :
                        user.AccountBalance = None
                    else :    
                        user.AccountBalance = float(user.AccountBalance[0])
                user.AccountBalance = user.AccountBalance or 0.0        
                user.LifeTimePaid = fields.get("pykotaLifeTimePaid")
                if user.LifeTimePaid is not None :
                    if user.LifeTimePaid[0].upper() == "NONE" :
                        user.LifeTimePaid = None
                    else :    
                        user.LifeTimePaid = float(user.LifeTimePaid[0])
                user.LifeTimePaid = user.LifeTimePaid or 0.0        
            user.Exists = 1
        return user
       
    def getGroup(self, groupname) :    
        """Extracts group information given its name."""
        group = StorageGroup(self, groupname)
        result = self.doSearch("(&(objectClass=pykotaGroup)(|(pykotaGroupName=%s)(%s=%s)))" % (groupname, self.info["grouprdn"], groupname), ["pykotaLimitBy"], base=self.info["groupbase"])
        if result :
            fields = result[0][1]
            group.ident = result[0][0]
            group.LimitBy = fields.get("pykotaLimitBy")
            if group.LimitBy is not None :
                group.LimitBy = group.LimitBy[0]
            group.AccountBalance = 0.0
            group.LifeTimePaid = 0.0
            group.Members = self.getGroupMembers(group)
            for member in group.Members :
                group.AccountBalance += member.AccountBalance
                group.LifeTimePaid += member.LifeTimePaid
            group.Exists = 1
        return group
       
    def getPrinter(self, printername) :        
        """Extracts printer information given its name."""
        printer = StoragePrinter(self, printername)
        result = self.doSearch("(&(objectClass=pykotaPrinter)(|(pykotaPrinterName=%s)(%s=%s)))" % (printername, self.info["printerrdn"], printername), ["pykotaPricePerPage", "pykotaPricePerJob"], base=self.info["printerbase"])
        if result :
            fields = result[0][1]
            printer.ident = result[0][0]
            printer.PricePerJob = float(fields.get("pykotaPricePerJob")[0] or 0.0)
            printer.PricePerPage = float(fields.get("pykotaPricePerPage")[0] or 0.0)
            printer.LastJob = self.getPrinterLastJob(printer)
            printer.Exists = 1
        return printer    
            
    def getUserGroups(self, user) :        
        """Returns the user's groups list."""
        groups = []
        result = self.doSearch("(&(objectClass=pykotaGroup)(%s=%s))" % (self.info["groupmembers"], user.Name), [self.info["grouprdn"]], base=self.info["groupbase"])
        if result :
            for (groupid, fields) in result :
                groups.append(self.getGroup(fields.get(self.info["grouprdn"])[0]))
        return groups        
        
    def getGroupMembers(self, group) :        
        """Returns the group's members list."""
        groupmembers = []
        result = self.doSearch("(&(objectClass=pykotaGroup)(|(pykotaGroupName=%s)(%s=%s)))" % (group.Name, self.info["grouprdn"], group.Name), [self.info["groupmembers"]], base=self.info["groupbase"])
        if result :
            for username in result[0][1].get(self.info["groupmembers"], []) :
                groupmembers.append(self.getUser(username))
        return groupmembers        
        
    def getUserPQuota(self, user, printer) :        
        """Extracts a user print quota."""
        userpquota = StorageUserPQuota(self, user, printer)
        if user.Exists :
            result = self.doSearch("(&(objectClass=pykotaUserPQuota)(pykotaUserName=%s)(pykotaPrinterName=%s))" % (user.Name, printer.Name), ["pykotaPageCounter", "pykotaLifePageCounter", "pykotaSoftLimit", "pykotaHardLimit", "pykotaDateLimit"], base=self.info["userquotabase"])
            if result :
                fields = result[0][1]
                userpquota.ident = result[0][0]
                userpquota.PageCounter = int(fields.get("pykotaPageCounter")[0] or 0)
                userpquota.LifePageCounter = int(fields.get("pykotaLifePageCounter")[0] or 0)
                userpquota.SoftLimit = fields.get("pykotaSoftLimit")
                if userpquota.SoftLimit is not None :
                    if userpquota.SoftLimit[0].upper() == "NONE" :
                        userpquota.SoftLimit = None
                    else :    
                        userpquota.SoftLimit = int(userpquota.SoftLimit[0])
                userpquota.HardLimit = fields.get("pykotaHardLimit")
                if userpquota.HardLimit is not None :
                    if userpquota.HardLimit[0].upper() == "NONE" :
                        userpquota.HardLimit = None
                    elif userpquota.HardLimit is not None :    
                        userpquota.HardLimit = int(userpquota.HardLimit[0])
                userpquota.DateLimit = fields.get("pykotaDateLimit")
                if userpquota.DateLimit is not None :
                    if userpquota.DateLimit[0].upper() == "NONE" : 
                        userpquota.DateLimit = None
                    else :    
                        userpquota.DateLimit = userpquota.DateLimit[0]
                userpquota.Exists = 1
        return userpquota
        
    def getGroupPQuota(self, group, printer) :        
        """Extracts a group print quota."""
        grouppquota = StorageGroupPQuota(self, group, printer)
        if group.Exists :
            result = self.doSearch("(&(objectClass=pykotaGroupPQuota)(pykotaGroupName=%s)(pykotaPrinterName=%s))" % (group.Name, printer.Name), ["pykotaSoftLimit", "pykotaHardLimit", "pykotaDateLimit"], base=self.info["groupquotabase"])
            if result :
                fields = result[0][1]
                grouppquota.ident = result[0][0]
                grouppquota.SoftLimit = fields.get("pykotaSoftLimit")
                if grouppquota.SoftLimit is not None :
                    if grouppquota.SoftLimit[0].upper() == "NONE" :
                        grouppquota.SoftLimit = None
                    else :    
                        grouppquota.SoftLimit = int(grouppquota.SoftLimit[0])
                grouppquota.HardLimit = fields.get("pykotaHardLimit")
                if grouppquota.HardLimit is not None :
                    if grouppquota.HardLimit[0].upper() == "NONE" :
                        grouppquota.HardLimit = None
                    else :    
                        grouppquota.HardLimit = int(grouppquota.HardLimit[0])
                grouppquota.DateLimit = fields.get("pykotaDateLimit")
                if grouppquota.DateLimit is not None :
                    if grouppquota.DateLimit[0].upper() == "NONE" : 
                        grouppquota.DateLimit = None
                    else :    
                        grouppquota.DateLimit = grouppquota.DateLimit[0]
                grouppquota.PageCounter = 0
                grouppquota.LifePageCounter = 0
                if (not hasattr(group, "Members")) or (group.Members is None) :
                    group.Members = self.getGroupMembers(group)
                usernamesfilter = "".join(["(pykotaUserName=%s)" % member.Name for member in group.Members])
                result = self.doSearch("(&(objectClass=pykotaUserPQuota)(pykotaPrinterName=%s)(|%s))" % (printer.Name, usernamesfilter), ["pykotaPageCounter", "pykotaLifePageCounter"], base=self.info["userquotabase"])
                if result :
                    for userpquota in result :    
                        grouppquota.PageCounter += int(userpquota[1].get("pykotaPageCounter")[0] or 0)
                        grouppquota.LifePageCounter += int(userpquota[1].get("pykotaLifePageCounter")[0] or 0)
                grouppquota.Exists = 1
        return grouppquota
        
    def getPrinterLastJob(self, printer) :        
        """Extracts a printer's last job information."""
        lastjob = StorageLastJob(self, printer)
        result = self.doSearch("(&(objectClass=pykotaLastjob)(|(pykotaPrinterName=%s)(%s=%s)))" % (printer.Name, self.info["printerrdn"], printer.Name), ["pykotaLastJobIdent"], base=self.info["lastjobbase"])
        if result :
            lastjob.lastjobident = result[0][0]
            lastjobident = result[0][1]["pykotaLastJobIdent"][0]
            result = self.doSearch("objectClass=pykotaJob", ["pykotaUserName", "pykotaJobId", "pykotaPrinterPageCounter", "pykotaJobSize", "pykotaAction", "createTimestamp"], base="cn=%s,%s" % (lastjobident, self.info["jobbase"]), scope=ldap.SCOPE_BASE)
            if result :
                fields = result[0][1]
                lastjob.ident = result[0][0]
                lastjob.JobId = fields.get("pykotaJobId")[0]
                lastjob.User = self.getUser(fields.get("pykotaUserName")[0])
                lastjob.PrinterPageCounter = int(fields.get("pykotaPrinterPageCounter")[0] or 0)
                lastjob.JobSize = int(fields.get("pykotaJobSize", [0])[0])
                lastjob.JobAction = fields.get("pykotaAction")[0]
                date = fields.get("createTimestamp")[0]
                year = int(date[:4])
                month = int(date[4:6])
                day = int(date[6:8])
                hour = int(date[8:10])
                minute = int(date[10:12])
                second = int(date[12:14])
                lastjob.JobDate = "%04i-%02i-%02i %02i:%02i:%02i" % (year, month, day, hour, minute, second)
                lastjob.Exists = 1
        return lastjob
        
    def getMatchingPrinters(self, printerpattern) :
        """Returns the list of all printers for which name matches a certain pattern."""
        printers = []
        # see comment at the same place in pgstorage.py
        result = self.doSearch("objectClass=pykotaPrinter", ["pykotaPrinterName", "pykotaPricePerPage", "pykotaPricePerJob"], base=self.info["printerbase"])
        if result :
            for (printerid, fields) in result :
                printername = fields["pykotaPrinterName"][0]
                if self.tool.matchString(printername, [ printerpattern ]) :
                    printer = StoragePrinter(self, printername)
                    printer.ident = printerid
                    printer.PricePerJob = float(fields.get("pykotaPricePerJob")[0] or 0.0)
                    printer.PricePerPage = float(fields.get("pykotaPricePerPage")[0] or 0.0)
                    printer.LastJob = self.getPrinterLastJob(printer)
                    printer.Exists = 1
                    printers.append(printer)
        return printers        
        
    def getPrinterUsersAndQuotas(self, printer, names=None) :        
        """Returns the list of users who uses a given printer, along with their quotas."""
        usersandquotas = []
        result = self.doSearch("(&(objectClass=pykotaUserPQuota)(pykotaPrinterName=%s))" % printer.Name, ["pykotaUserName", "pykotaPageCounter", "pykotaLifePageCounter", "pykotaSoftLimit", "pykotaHardLimit", "pykotaDateLimit"], base=self.info["userquotabase"])
        if result :
            for (userquotaid, fields) in result :
                user = self.getUser(fields["pykotaUserName"][0])
                if (names is None) or self.tool.matchString(user.Name, names) :
                    userpquota = StorageUserPQuota(self, user, printer)
                    userpquota.ident = userquotaid
                    userpquota.PageCounter = int(fields.get("pykotaPageCounter")[0] or 0)
                    userpquota.LifePageCounter = int(fields.get("pykotaLifePageCounter")[0] or 0)
                    userpquota.SoftLimit = fields.get("pykotaSoftLimit")
                    if userpquota.SoftLimit is not None :
                        if userpquota.SoftLimit[0].upper() == "NONE" :
                            userpquota.SoftLimit = None
                        else :    
                            userpquota.SoftLimit = int(userpquota.SoftLimit[0])
                    userpquota.HardLimit = fields.get("pykotaHardLimit")
                    if userpquota.HardLimit is not None :
                        if userpquota.HardLimit[0].upper() == "NONE" :
                            userpquota.HardLimit = None
                        elif userpquota.HardLimit is not None :    
                            userpquota.HardLimit = int(userpquota.HardLimit[0])
                    userpquota.DateLimit = fields.get("pykotaDateLimit")
                    if userpquota.DateLimit is not None :
                        if userpquota.DateLimit[0].upper() == "NONE" : 
                            userpquota.DateLimit = None
                        else :    
                            userpquota.DateLimit = userpquota.DateLimit[0]
                    userpquota.Exists = 1
                    usersandquotas.append((user, userpquota))
        usersandquotas.sort(lambda x, y : cmp(x[0].Name, y[0].Name))            
        return usersandquotas
                
    def getPrinterGroupsAndQuotas(self, printer, names=None) :        
        """Returns the list of groups which uses a given printer, along with their quotas."""
        groupsandquotas = []
        result = self.doSearch("(&(objectClass=pykotaGroupPQuota)(pykotaPrinterName=%s))" % printer.Name, ["pykotaGroupName"], base=self.info["groupquotabase"])
        if result :
            for (groupquotaid, fields) in result :
                group = self.getGroup(fields.get("pykotaGroupName")[0])
                if (names is None) or self.tool.matchString(group.Name, names) :
                    grouppquota = self.getGroupPQuota(group, printer)
                    groupsandquotas.append((group, grouppquota))
        groupsandquotas.sort(lambda x, y : cmp(x[0].Name, y[0].Name))            
        return groupsandquotas
        
    def addPrinter(self, printername) :        
        """Adds a printer to the quota storage, returns it."""
        fields = { self.info["printerrdn"] : printername,
                   "objectClass" : ["pykotaObject", "pykotaPrinter"],
                   "cn" : printername,
                   "pykotaPrinterName" : printername,
                   "pykotaPricePerPage" : "0.0",
                   "pykotaPricePerJob" : "0.0",
                 } 
        dn = "%s=%s,%s" % (self.info["printerrdn"], printername, self.info["printerbase"])
        self.doAdd(dn, fields)
        return self.getPrinter(printername)
        
    def addUser(self, user) :        
        """Adds a user to the quota storage, returns it."""
        fields = { self.info["userrdn"] : user.Name,
                   "objectClass" : ["pykotaObject", "pykotaAccount"],
                   "cn" : user.Name,
                   "pykotaUserName" : user.Name,
                   "pykotaLimitBY" : (user.LimitBy or "quota"),
                 } 
        dn = "%s=%s,%s" % (self.info["userrdn"], user.Name, self.info["userbase"])
        self.doAdd(dn, fields)
        fields = { 
                   "objectClass" : ["pykotaObject", "pykotaAccountBalance"],
                   "cn" : user.Name,
                   "pykotaUserName" : user.Name,
                   "pykotaBalance" : str(user.AccountBalance or 0.0),
                   "pykotaLifeTimePaid" : str(user.LifeTimePaid or 0.0),
                 } 
        dn = "cn=%s,%s" % (user.Name, self.info["balancebase"])
        self.doAdd(dn, fields)
        return self.getUser(user.Name)
        
    def addGroup(self, group) :        
        """Adds a group to the quota storage, returns it."""
        fields = { self.info["grouprdn"] : group.Name,
                   "objectClass" : ["pykotaObject", "pykotaGroup"],
                   "cn" : group.Name,
                   "pykotaGroupName" : group.Name,
                   "pykotaLimitBY" : (group.LimitBy or "quota"),
                 } 
        dn = "%s=%s,%s" % (self.info["grouprdn"], group.Name, self.info["groupbase"])
        self.doAdd(dn, fields)
        return self.getGroup(group.Name)
        
    def addUserToGroup(self, user, group) :    
        """Adds an user to a group."""
        if user.Name not in [u.Name for u in group.Members] :
            result = self.doSearch("objectClass=pykotaGroup", None, base=group.ident, scope=ldap.SCOPE_BASE)    
            if result :
                fields = result[0][1]
                fields[self.info["groupmembers"]].append(user.Name)
                self.doModify(group.ident, fields)
                group.Members.append(user)
                
    def addUserPQuota(self, user, printer) :
        """Initializes a user print quota on a printer."""
        uuid = self.genUUID()
        fields = { "cn" : uuid,
                   "objectClass" : ["pykotaObject", "pykotaUserPQuota"],
                   "pykotaUserName" : user.Name,
                   "pykotaPrinterName" : printer.Name,
                   "pykotaDateLimit" : "None",
                   "pykotaPageCounter" : "0",
                   "pykotaLifePageCounter" : "0",
                 } 
        dn = "cn=%s,%s" % (uuid, self.info["userquotabase"])
        self.doAdd(dn, fields)
        return self.getUserPQuota(user, printer)
        
    def addGroupPQuota(self, group, printer) :
        """Initializes a group print quota on a printer."""
        uuid = self.genUUID()
        fields = { "cn" : uuid,
                   "objectClass" : ["pykotaObject", "pykotaGroupPQuota"],
                   "pykotaGroupName" : group.Name,
                   "pykotaPrinterName" : printer.Name,
                   "pykotaDateLimit" : "None",
                 } 
        dn = "cn=%s,%s" % (uuid, self.info["groupquotabase"])
        self.doAdd(dn, fields)
        return self.getGroupPQuota(group, printer)
        
    def writePrinterPrices(self, printer) :    
        """Write the printer's prices back into the storage."""
        fields = {
                   "pykotaPricePerPage" : str(printer.PricePerPage),
                   "pykotaPricePerJob" : str(printer.PricePerJob),
                 }
        self.doModify(printer.ident, fields)
        
    def writeUserLimitBy(self, user, limitby) :    
        """Sets the user's limiting factor."""
        fields = {
                   "pykotaLimitBy" : limitby,
                 }
        self.doModify(user.ident, fields)         
        
    def writeGroupLimitBy(self, group, limitby) :    
        """Sets the group's limiting factor."""
        fields = {
                   "pykotaLimitBy" : limitby,
                 }
        self.doModify(group.ident, fields)         
        
    def writeUserPQuotaDateLimit(self, userpquota, datelimit) :    
        """Sets the date limit permanently for a user print quota."""
        fields = {
                   "pykotaDateLimit" : "%04i-%02i-%02i %02i:%02i:%02i" % (datelimit.year, datelimit.month, datelimit.day, datelimit.hour, datelimit.minute, datelimit.second),
                 }
        return self.doModify(userpquota.ident, fields)
            
    def writeGroupPQuotaDateLimit(self, grouppquota, datelimit) :    
        """Sets the date limit permanently for a group print quota."""
        fields = {
                   "pykotaDateLimit" : "%04i-%02i-%02i %02i:%02i:%02i" % (datelimit.year, datelimit.month, datelimit.day, datelimit.hour, datelimit.minute, datelimit.second),
                 }
        return self.doModify(grouppquota.ident, fields)
        
    def writeUserPQuotaPagesCounters(self, userpquota, newpagecounter, newlifepagecounter) :    
        """Sets the new page counters permanently for a user print quota."""
        fields = {
                   "pykotaPageCounter" : str(newpagecounter),
                   "pykotaLifePageCounter" : str(newlifepagecounter),
                 }  
        return self.doModify(userpquota.ident, fields)         
       
    def writeUserAccountBalance(self, user, newbalance, newlifetimepaid=None) :    
        """Sets the new account balance and eventually new lifetime paid."""
        fields = {
                   "pykotaBalance" : str(newbalance),
                 }
        if newlifetimepaid is not None :
            fields.update({ "pykotaLifeTimePaid" : str(newlifetimepaid) })
        return self.doModify(user.idbalance, fields)         
            
    def writeLastJobSize(self, lastjob, jobsize) :        
        """Sets the last job's size permanently."""
        fields = {
                   "pykotaJobSize" : str(jobsize),
                 }
        self.doModify(lastjob.ident, fields)         
        
    def writeJobNew(self, printer, user, jobid, pagecounter, action, jobsize=None) :    
        """Adds a job in a printer's history."""
        uuid = self.genUUID()
        fields = {
                   "objectClass" : ["pykotaObject", "pykotaJob"],
                   "cn" : uuid,
                   "pykotaUserName" : user.Name,
                   "pykotaPrinterName" : printer.Name,
                   "pykotaJobId" : jobid,
                   "pykotaPrinterPageCounter" : str(pagecounter),
                   "pykotaAction" : action,
                 }
        if jobsize is not None :         
            fields.update({ "pykotaJobSize" : str(jobsize) })
        dn = "cn=%s,%s" % (uuid, self.info["jobbase"])
        self.doAdd(dn, fields)
        if printer.LastJob.Exists :
            fields = {
                       "pykotaLastJobIdent" : uuid,
                     }
            self.doModify(printer.LastJob.lastjobident, fields)         
        else :    
            lastjuuid = self.genUUID()
            lastjdn = "cn=%s,%s" % (lastjuuid, self.info["lastjobbase"])
            fields = {
                       "objectClass" : ["pykotaObject", "pykotaLastJob"],
                       "cn" : lastjuuid,
                       "pykotaPrinterName" : printer.Name,
                       "pykotaLastJobIdent" : uuid,
                     }  
            self.doAdd(lastjdn, fields)          
            
    def writeUserPQuotaLimits(self, userpquota, softlimit, hardlimit) :
        """Sets soft and hard limits for a user quota."""
        fields = { 
                   "pykotaSoftLimit" : str(softlimit),
                   "pykotaHardLimit" : str(hardlimit),
                 }
        self.doModify(userpquota.ident, fields)
        
    def writeGroupPQuotaLimits(self, grouppquota, softlimit, hardlimit) :
        """Sets soft and hard limits for a group quota on a specific printer given (groupid, printerid)."""
        fields = { 
                   "pykotaSoftLimit" : str(softlimit),
                   "pykotaHardLimit" : str(hardlimit),
                 }
        self.doModify(grouppquota.ident, fields)
            
    def deleteUser(self, user) :    
        """Completely deletes an user from the Quota Storage."""
        # TODO : What should we do if we delete the last person who used a given printer ?
        # TODO : we can't reassign the last job to the previous one, because next user would be
        # TODO : incorrectly charged (overcharged).
        result = self.doSearch("(&(objectClass=pykotaLastJob)(pykotaUserName=%s))" % user.Name, base=self.info["lastjobbase"])
        for (ident, fields) in result :
            self.doDelete(ident)
        result = self.doSearch("(&(objectClass=pykotaJob)(pykotaUserName=%s))" % user.Name, base=self.info["jobbase"])
        for (ident, fields) in result :
            self.doDelete(ident)
        result = self.doSearch("(&(objectClass=pykotaUserPQuota)(pykotaUserName=%s))" % user.Name, ["pykotaUserName"], base=self.info["userquotabase"])
        for (ident, fields) in result :
            self.doDelete(ident)
        result = self.doSearch("objectClass=pykotaAccount", None, base=user.ident, scope=ldap.SCOPE_BASE)    
        if result :
            fields = result[0][1]
            for k in fields.keys() :
                if k.startswith("pykota") :
                    del fields[k]
                elif k.lower() == "objectclass" :    
                    todelete = []
                    for i in range(len(fields[k])) :
                        if fields[k][i].startswith("pykota") : 
                            todelete.append(i)
                    todelete.sort()        
                    todelete.reverse()
                    for i in todelete :
                        del fields[k][i]
            if fields.get("objectclass") :            
                self.doModify(user.ident, fields, ignoreold=0)        
            else :    
                self.doDelete(user.ident)
        result = self.doSearch("(&(objectClass=pykotaAccountBalance)(pykotaUserName=%s))" % user.Name, ["pykotaUserName"], base=self.info["balancebase"])
        for (ident, fields) in result :
            self.doDelete(ident)
        
    def deleteGroup(self, group) :    
        """Completely deletes a group from the Quota Storage."""
        result = self.doSearch("(&(objectClass=pykotaGroupPQuota)(pykotaGroupName=%s))" % group.Name, ["pykotaGroupName"], base=self.info["groupquotabase"])
        for (ident, fields) in result :
            self.doDelete(ident)
        result = self.doSearch("objectClass=pykotaGroup", None, base=group.ident, scope=ldap.SCOPE_BASE)    
        if result :
            fields = result[0][1]
            for k in fields.keys() :
                if k.startswith("pykota") :
                    del fields[k]
                elif k.lower() == "objectclass" :    
                    todelete = []
                    for i in range(len(fields[k])) :
                        if fields[k][i].startswith("pykota") : 
                            todelete.append(i)
                    todelete.sort()        
                    todelete.reverse()
                    for i in todelete :
                        del fields[k][i]
            if fields.get("objectclass") :            
                self.doModify(group.ident, fields, ignoreold=0)        
            else :    
                self.doDelete(group.ident)
            
