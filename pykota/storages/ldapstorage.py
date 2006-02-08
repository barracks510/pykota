# PyKota
# -*- coding: ISO-8859-15 -*-
#
# PyKota : Print Quotas for CUPS and LPRng
#
# (c) 2003, 2004, 2005, 2006 Jerome Alet <alet@librelogiciel.com>
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

#
# My IANA assigned number, for 
# "Conseil Internet & Logiciels Libres, Jérôme Alet" 
# is 16868. Use this as a base to create the LDAP schema.
#

import sys
import os
import types
import time
import md5
import base64
from mx import DateTime

from pykota.storage import PyKotaStorageError, BaseStorage, StorageObject, \
                           StorageUser, StorageGroup, StoragePrinter, \
                           StorageJob, StorageLastJob, StorageUserPQuota, \
                           StorageGroupPQuota, StorageBillingCode

try :
    import ldap
    import ldap.modlist
except ImportError :    
    raise PyKotaStorageError, "This python version (%s) doesn't seem to have the python-ldap module installed correctly." % sys.version.split()[0]
else :    
    try :
        from ldap.cidict import cidict
    except ImportError :    
        import UserDict
        sys.stderr.write("ERROR: PyKota requires a newer version of python-ldap. Workaround activated. Please upgrade python-ldap !\n")
        class cidict(UserDict.UserDict) :
            pass # Fake it all, and don't care for case insensitivity : users who need it will have to upgrade.
    
class Storage(BaseStorage) :
    def __init__(self, pykotatool, host, dbname, user, passwd) :
        """Opens the LDAP connection."""
        self.savedtool = pykotatool
        self.savedhost = host
        self.saveddbname = dbname
        self.saveduser = user
        self.savedpasswd = passwd
        self.secondStageInit()
        
    def secondStageInit(self) :    
        """Second stage initialisation."""
        BaseStorage.__init__(self, self.savedtool)
        self.info = self.tool.config.getLDAPInfo()
        message = ""
        for tryit in range(3) :
            try :
                self.tool.logdebug("Trying to open database (host=%s, dbname=%s, user=%s)..." % (self.savedhost, self.saveddbname, self.saveduser))
                self.database = ldap.initialize(self.savedhost) 
                if self.info["ldaptls"] :
                    # we want TLS
                    ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, self.info["cacert"])
                    self.database.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
                    self.database.start_tls_s()
                self.database.simple_bind_s(self.saveduser, self.savedpasswd)
                self.basedn = self.saveddbname
            except ldap.SERVER_DOWN :    
                message = "LDAP backend for PyKota seems to be down !"
                self.tool.printInfo("%s" % message, "error")
                self.tool.printInfo("Trying again in 2 seconds...", "warn")
                time.sleep(2)
            except ldap.LDAPError :    
                message = "Unable to connect to LDAP server %s as %s." % (self.savedhost, self.saveduser)
                self.tool.printInfo("%s" % message, "error")
                self.tool.printInfo("Trying again in 2 seconds...", "warn")
                time.sleep(2)
            else :    
                self.useldapcache = self.tool.config.getLDAPCache()
                if self.useldapcache :
                    self.tool.logdebug("Low-Level LDAP Caching enabled.")
                    self.ldapcache = {} # low-level cache specific to LDAP backend
                self.closed = 0
                self.tool.logdebug("Database opened (host=%s, dbname=%s, user=%s)" % (self.savedhost, self.saveddbname, self.saveduser))
                return # All is fine here.
        raise PyKotaStorageError, message         
            
    def close(self) :    
        """Closes the database connection."""
        if not self.closed :
            self.database.unbind_s()
            self.closed = 1
            self.tool.logdebug("Database closed.")
        
    def genUUID(self) :    
        """Generates an unique identifier.
        
           TODO : this one is not unique accross several print servers, but should be sufficient for testing.
        """
        return md5.md5("%s" % time.time()).hexdigest()
        
    def normalizeFields(self, fields) :    
        """Ensure all items are lists."""
        for (k, v) in fields.items() :
            if type(v) not in (types.TupleType, types.ListType) :
                if not v :
                    del fields[k]
                else :    
                    fields[k] = [ v ]
        return fields        
        
    def beginTransaction(self) :    
        """Starts a transaction."""
        self.tool.logdebug("Transaction begins... WARNING : No transactions in LDAP !")
        
    def commitTransaction(self) :    
        """Commits a transaction."""
        self.tool.logdebug("Transaction committed. WARNING : No transactions in LDAP !")
        
    def rollbackTransaction(self) :     
        """Rollbacks a transaction."""
        self.tool.logdebug("Transaction aborted. WARNING : No transaction in LDAP !")
        
    def doSearch(self, key, fields=None, base="", scope=ldap.SCOPE_SUBTREE, flushcache=0) :
        """Does an LDAP search query."""
        message = ""
        for tryit in range(3) :
            try :
                base = base or self.basedn
                if self.useldapcache :
                    # Here we overwrite the fields the app want, to try and
                    # retrieve ALL user defined attributes ("*")
                    # + the createTimestamp attribute, needed by job history
                    # 
                    # This may not work with all LDAP servers
                    # but works at least in OpenLDAP (2.1.25) 
                    # and iPlanet Directory Server (5.1 SP3)
                    fields = ["*", "createTimestamp"]         
                    
                if self.useldapcache and (not flushcache) and (scope == ldap.SCOPE_BASE) and self.ldapcache.has_key(base) :
                    entry = self.ldapcache[base]
                    self.tool.logdebug("LDAP cache hit %s => %s" % (base, entry))
                    result = [(base, entry)]
                else :
                    self.tool.logdebug("QUERY : Filter : %s, BaseDN : %s, Scope : %s, Attributes : %s" % (key, base, scope, fields))
                    result = self.database.search_s(base, scope, key, fields)
            except ldap.NO_SUCH_OBJECT, msg :        
                raise PyKotaStorageError, (_("Search base %s doesn't seem to exist. Probable misconfiguration. Please double check /etc/pykota/pykota.conf : %s") % (base, msg))
            except ldap.LDAPError, msg :    
                message = (_("Search for %s(%s) from %s(scope=%s) returned no answer.") % (key, fields, base, scope)) + " : %s" % str(msg)
                self.tool.printInfo("LDAP error : %s" % message, "error")
                self.tool.printInfo("LDAP connection will be closed and reopened.", "warn")
                self.close()
                self.secondStageInit()
            else :     
                self.tool.logdebug("QUERY : Result : %s" % result)
                result = [ (dn, cidict(attrs)) for (dn, attrs) in result ]
                if self.useldapcache :
                    for (dn, attributes) in result :
                        self.tool.logdebug("LDAP cache store %s => %s" % (dn, attributes))
                        self.ldapcache[dn] = attributes
                return result
        raise PyKotaStorageError, message
            
    def doAdd(self, dn, fields) :
        """Adds an entry in the LDAP directory."""
        fields = self.normalizeFields(cidict(fields))
        message = ""
        for tryit in range(3) :
            try :
                self.tool.logdebug("QUERY : ADD(%s, %s)" % (dn, str(fields)))
                entry = ldap.modlist.addModlist(fields)
                self.tool.logdebug("%s" % entry)
                self.database.add_s(dn, entry)
            except ldap.LDAPError, msg :
                message = (_("Problem adding LDAP entry (%s, %s)") % (dn, str(fields))) + " : %s" % str(msg)
                self.tool.printInfo("LDAP error : %s" % message, "error")
                self.tool.printInfo("LDAP connection will be closed and reopened.", "warn")
                self.close()
                self.secondStageInit()
            else :
                if self.useldapcache :
                    self.tool.logdebug("LDAP cache add %s => %s" % (dn, fields))
                    self.ldapcache[dn] = fields
                return dn
        raise PyKotaStorageError, message
            
    def doDelete(self, dn) :
        """Deletes an entry from the LDAP directory."""
        message = ""
        for tryit in range(3) :
            try :
                self.tool.logdebug("QUERY : Delete(%s)" % dn)
                self.database.delete_s(dn)
            except ldap.LDAPError, msg :
                message = (_("Problem deleting LDAP entry (%s)") % dn) + " : %s" % str(msg)
                self.tool.printInfo("LDAP error : %s" % message, "error")
                self.tool.printInfo("LDAP connection will be closed and reopened.", "warn")
                self.close()
                self.secondStageInit()
            else :    
                if self.useldapcache :
                    try :
                        self.tool.logdebug("LDAP cache del %s" % dn)
                        del self.ldapcache[dn]
                    except KeyError :    
                        pass
                return        
        raise PyKotaStorageError, message
            
    def doModify(self, dn, fields, ignoreold=1, flushcache=0) :
        """Modifies an entry in the LDAP directory."""
        fields = cidict(fields)
        for tryit in range(3) :
            try :
                # TODO : take care of, and update LDAP specific cache
                if self.useldapcache and not flushcache :
                    if self.ldapcache.has_key(dn) :
                        old = self.ldapcache[dn]
                        self.tool.logdebug("LDAP cache hit %s => %s" % (dn, old))
                        oldentry = {}
                        for (k, v) in old.items() :
                            if k != "createTimestamp" :
                                oldentry[k] = v
                    else :    
                        self.tool.logdebug("LDAP cache miss %s" % dn)
                        oldentry = self.doSearch("objectClass=*", base=dn, scope=ldap.SCOPE_BASE)[0][1]
                else :        
                    oldentry = self.doSearch("objectClass=*", base=dn, scope=ldap.SCOPE_BASE, flushcache=flushcache)[0][1]
                for (k, v) in fields.items() :
                    if type(v) == type({}) :
                        try :
                            oldvalue = v["convert"](oldentry.get(k, [0])[0])
                        except ValueError :    
                            self.tool.logdebug("Error converting %s with %s(%s)" % (oldentry.get(k), k, v))
                            oldvalue = 0
                        if v["operator"] == '+' :
                            newvalue = oldvalue + v["value"]
                        else :    
                            newvalue = oldvalue - v["value"]
                        fields[k] = str(newvalue)
                fields = self.normalizeFields(fields)
                self.tool.logdebug("QUERY : Modify(%s, %s ==> %s)" % (dn, oldentry, fields))
                entry = ldap.modlist.modifyModlist(oldentry, fields, ignore_oldexistent=ignoreold)
                modentry = []
                for (mop, mtyp, mval) in entry :
                    if mtyp and (mtyp.lower() != "createtimestamp") :
                        modentry.append((mop, mtyp, mval))
                self.tool.logdebug("MODIFY : %s ==> %s ==> %s" % (fields, entry, modentry))
                if modentry :
                    self.database.modify_s(dn, modentry)
            except ldap.LDAPError, msg :
                message = (_("Problem modifying LDAP entry (%s, %s)") % (dn, fields)) + " : %s" % str(msg)
                self.tool.printInfo("LDAP error : %s" % message, "error")
                self.tool.printInfo("LDAP connection will be closed and reopened.", "warn")
                self.close()
                self.secondStageInit()
            else :
                if self.useldapcache :
                    cachedentry = self.ldapcache[dn]
                    for (mop, mtyp, mval) in entry :
                        if mop in (ldap.MOD_ADD, ldap.MOD_REPLACE) :
                            cachedentry[mtyp] = mval
                        else :
                            try :
                                del cachedentry[mtyp]
                            except KeyError :    
                                pass
                    self.tool.logdebug("LDAP cache update %s => %s" % (dn, cachedentry))
                return dn
        raise PyKotaStorageError, message
            
    def filterNames(self, records, attribute, patterns=None) :
        """Returns a list of 'attribute' from a list of records.
        
           Logs any missing attribute.
        """   
        result = []
        for (dn, record) in records :
            attrval = record.get(attribute, [None])[0]
            if attrval is None :
                self.tool.printInfo("Object %s has no %s attribute !" % (dn, attribute), "error")
            else :
                attrval = self.databaseToUserCharset(attrval)
                if patterns :
                    if (not isinstance(patterns, type([]))) and (not isinstance(patterns, type(()))) :
                        patterns = [ patterns ]
                    if self.tool.matchString(attrval, patterns) :   
                        result.append(attrval)
                else :    
                    result.append(attrval)
        return result        
                
    def getAllBillingCodes(self, billingcode=None) :    
        """Extracts all billing codes or only the billing codes matching the optional parameter."""
        ldapfilter = "objectClass=pykotaBilling"
        result = self.doSearch(ldapfilter, ["pykotaBillingCode"], base=self.info["billingcodebase"])
        if result :
            return [self.databaseToUserCharset(bc) for bc in self.filterNames(result, "pykotaBillingCode", billingcode)]
        else :    
            return []
        
    def getAllPrintersNames(self, printername=None) :    
        """Extracts all printer names or only the printers' names matching the optional parameter."""
        ldapfilter = "objectClass=pykotaPrinter"
        result = self.doSearch(ldapfilter, ["pykotaPrinterName"], base=self.info["printerbase"])
        if result :
            return self.filterNames(result, "pykotaPrinterName", printername)
        else :    
            return []
        
    def getAllUsersNames(self, username=None) :    
        """Extracts all user names or only the users' names matching the optional parameter."""
        ldapfilter = "objectClass=pykotaAccount"
        result = self.doSearch(ldapfilter, ["pykotaUserName"], base=self.info["userbase"])
        if result :
            return self.filterNames(result, "pykotaUserName", username)
        else :    
            return []
        
    def getAllGroupsNames(self, groupname=None) :    
        """Extracts all group names or only the groups' names matching the optional parameter."""
        ldapfilter = "objectClass=pykotaGroup"
        result = self.doSearch(ldapfilter, ["pykotaGroupName"], base=self.info["groupbase"])
        if result :
            return self.filterNames(result, "pykotaGroupName", groupname)
        else :    
            return []
        
    def getUserNbJobsFromHistory(self, user) :
        """Returns the number of jobs the user has in history."""
        result = self.doSearch("(&(pykotaUserName=%s)(objectClass=pykotaJob))" % self.userCharsetToDatabase(user.Name), None, base=self.info["jobbase"])
        return len(result)
        
    def getUserFromBackend(self, username) :    
        """Extracts user information given its name."""
        user = StorageUser(self, username)
        username = self.userCharsetToDatabase(username)
        result = self.doSearch("(&(objectClass=pykotaAccount)(|(pykotaUserName=%s)(%s=%s)))" % (username, self.info["userrdn"], username), ["pykotaUserName", "pykotaLimitBy", self.info["usermail"], "pykotaOverCharge"], base=self.info["userbase"])
        if result :
            fields = result[0][1]
            user.ident = result[0][0]
            user.Email = fields.get(self.info["usermail"], [None])[0]
            user.LimitBy = fields.get("pykotaLimitBy", ["quota"])[0]
            user.OverCharge = float(fields.get("pykotaOverCharge", [1.0])[0])
            result = self.doSearch("(&(objectClass=pykotaAccountBalance)(|(pykotaUserName=%s)(%s=%s)))" % (username, self.info["balancerdn"], username), ["pykotaBalance", "pykotaLifeTimePaid", "pykotaPayments"], base=self.info["balancebase"])
            if not result :
                raise PyKotaStorageError, _("No pykotaAccountBalance object found for user %s. Did you create LDAP entries manually ?") % username
            else :
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
                user.Payments = []
                for payment in fields.get("pykotaPayments", []) :
                    try :
                        (date, amount, description) = payment.split(" # ")
                    except ValueError :
                        # Payment with no description (old Payment)
                        (date, amount) = payment.split(" # ")
                        description = ""
                    else :    
                        description = self.databaseToUserCharset(base64.decodestring(description))
                    user.Payments.append((date, float(amount), description))
            user.Exists = 1
        return user
       
    def getGroupFromBackend(self, groupname) :    
        """Extracts group information given its name."""
        group = StorageGroup(self, groupname)
        groupname = self.userCharsetToDatabase(groupname)
        result = self.doSearch("(&(objectClass=pykotaGroup)(|(pykotaGroupName=%s)(%s=%s)))" % (groupname, self.info["grouprdn"], groupname), ["pykotaGroupName", "pykotaLimitBy"], base=self.info["groupbase"])
        if result :
            fields = result[0][1]
            group.ident = result[0][0]
            group.Name = fields.get("pykotaGroupName", [self.databaseToUserCharset(groupname)])[0] 
            group.LimitBy = fields.get("pykotaLimitBy", ["quota"])[0]
            group.AccountBalance = 0.0
            group.LifeTimePaid = 0.0
            for member in self.getGroupMembers(group) :
                if member.Exists :
                    group.AccountBalance += member.AccountBalance
                    group.LifeTimePaid += member.LifeTimePaid
            group.Exists = 1
        return group
       
    def getPrinterFromBackend(self, printername) :        
        """Extracts printer information given its name : returns first matching printer."""
        printer = StoragePrinter(self, printername)
        printername = self.userCharsetToDatabase(printername)
        result = self.doSearch("(&(objectClass=pykotaPrinter)(|(pykotaPrinterName=%s)(%s=%s)))" \
                      % (printername, self.info["printerrdn"], printername), \
                        ["pykotaPrinterName", "pykotaPricePerPage", \
                         "pykotaPricePerJob", "pykotaMaxJobSize", \
                         "pykotaPassThrough", "uniqueMember", "description"], \
                      base=self.info["printerbase"])
        if result :
            fields = result[0][1]       # take only first matching printer, ignore the rest
            printer.ident = result[0][0]
            printer.Name = fields.get("pykotaPrinterName", [self.databaseToUserCharset(printername)])[0] 
            printer.PricePerJob = float(fields.get("pykotaPricePerJob", [0.0])[0])
            printer.PricePerPage = float(fields.get("pykotaPricePerPage", [0.0])[0])
            printer.MaxJobSize = int(fields.get("pykotaMaxJobSize", [0])[0])
            printer.PassThrough = fields.get("pykotaPassThrough", [None])[0]
            if printer.PassThrough in (1, "1", "t", "true", "TRUE", "True") :
                printer.PassThrough = 1
            else :
                printer.PassThrough = 0
            printer.uniqueMember = fields.get("uniqueMember", [])
            printer.Description = self.databaseToUserCharset(fields.get("description", [""])[0]) 
            printer.Exists = 1
        return printer    
        
    def getUserPQuotaFromBackend(self, user, printer) :        
        """Extracts a user print quota."""
        userpquota = StorageUserPQuota(self, user, printer)
        if printer.Exists and user.Exists :
            if self.info["userquotabase"].lower() == "user" :
                base = user.ident
            else :    
                base = self.info["userquotabase"]
            result = self.doSearch("(&(objectClass=pykotaUserPQuota)(pykotaUserName=%s)(pykotaPrinterName=%s))" % \
                                      (self.userCharsetToDatabase(user.Name), self.userCharsetToDatabase(printer.Name)), \
                                      ["pykotaPageCounter", "pykotaLifePageCounter", "pykotaSoftLimit", "pykotaHardLimit", "pykotaDateLimit", "pykotaWarnCount"], \
                                      base=base)
            if result :
                fields = result[0][1]
                userpquota.ident = result[0][0]
                userpquota.PageCounter = int(fields.get("pykotaPageCounter", [0])[0])
                userpquota.LifePageCounter = int(fields.get("pykotaLifePageCounter", [0])[0])
                userpquota.WarnCount = int(fields.get("pykotaWarnCount", [0])[0])
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
        
    def getGroupPQuotaFromBackend(self, group, printer) :        
        """Extracts a group print quota."""
        grouppquota = StorageGroupPQuota(self, group, printer)
        if group.Exists :
            if self.info["groupquotabase"].lower() == "group" :
                base = group.ident
            else :    
                base = self.info["groupquotabase"]
            result = self.doSearch("(&(objectClass=pykotaGroupPQuota)(pykotaGroupName=%s)(pykotaPrinterName=%s))" % \
                                      (self.userCharsetToDatabase(group.Name), self.userCharsetToDatabase(printer.Name)), \
                                      ["pykotaSoftLimit", "pykotaHardLimit", "pykotaDateLimit"], \
                                      base=base)
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
                usernamesfilter = "".join(["(pykotaUserName=%s)" % self.userCharsetToDatabase(member.Name) for member in self.getGroupMembers(group)])
                if usernamesfilter :
                    usernamesfilter = "(|%s)" % usernamesfilter
                if self.info["userquotabase"].lower() == "user" :
                    base = self.info["userbase"]
                else :
                    base = self.info["userquotabase"]
                result = self.doSearch("(&(objectClass=pykotaUserPQuota)(pykotaPrinterName=%s)%s)" % \
                                          (self.userCharsetToDatabase(printer.Name), usernamesfilter), \
                                          ["pykotaPageCounter", "pykotaLifePageCounter"], base=base)
                if result :
                    for userpquota in result :    
                        grouppquota.PageCounter += int(userpquota[1].get("pykotaPageCounter", [0])[0] or 0)
                        grouppquota.LifePageCounter += int(userpquota[1].get("pykotaLifePageCounter", [0])[0] or 0)
                grouppquota.Exists = 1
        return grouppquota
        
    def getPrinterLastJobFromBackend(self, printer) :        
        """Extracts a printer's last job information."""
        lastjob = StorageLastJob(self, printer)
        pname = self.userCharsetToDatabase(printer.Name)
        result = self.doSearch("(&(objectClass=pykotaLastjob)(|(pykotaPrinterName=%s)(%s=%s)))" % \
                                  (pname, self.info["printerrdn"], pname), \
                                  ["pykotaLastJobIdent"], \
                                  base=self.info["lastjobbase"])
        if result :
            lastjob.lastjobident = result[0][0]
            lastjobident = result[0][1]["pykotaLastJobIdent"][0]
            result = None
            try :
                result = self.doSearch("objectClass=pykotaJob", [ "pykotaJobSizeBytes", 
                                                                  "pykotaHostName", 
                                                                  "pykotaUserName", 
                                                                  "pykotaPrinterName", 
                                                                  "pykotaJobId", 
                                                                  "pykotaPrinterPageCounter", 
                                                                  "pykotaJobSize", 
                                                                  "pykotaAction", 
                                                                  "pykotaJobPrice", 
                                                                  "pykotaFileName", 
                                                                  "pykotaTitle", 
                                                                  "pykotaCopies", 
                                                                  "pykotaOptions", 
                                                                  "pykotaBillingCode", 
                                                                  "pykotaPages", 
                                                                  "pykotaMD5Sum", 
                                                                  "pykotaPrecomputedJobSize",
                                                                  "pykotaPrecomputedJobPrice",
                                                                  "createTimestamp" ], 
                                                                base="cn=%s,%s" % (lastjobident, self.info["jobbase"]), scope=ldap.SCOPE_BASE)
            except PyKotaStorageError :    
                pass # Last job entry exists, but job probably doesn't exist anymore. 
            if result :
                fields = result[0][1]
                lastjob.ident = result[0][0]
                lastjob.JobId = fields.get("pykotaJobId")[0]
                lastjob.UserName = self.databaseToUserCharset(fields.get("pykotaUserName")[0])
                lastjob.PrinterPageCounter = int(fields.get("pykotaPrinterPageCounter", [0])[0])
                try :
                    lastjob.JobSize = int(fields.get("pykotaJobSize", [0])[0])
                except ValueError :    
                    lastjob.JobSize = None
                try :    
                    lastjob.JobPrice = float(fields.get("pykotaJobPrice", [0.0])[0])
                except ValueError :    
                    lastjob.JobPrice = None
                lastjob.JobAction = fields.get("pykotaAction", [""])[0]
                lastjob.JobFileName = self.databaseToUserCharset(fields.get("pykotaFileName", [""])[0]) 
                lastjob.JobTitle = self.databaseToUserCharset(fields.get("pykotaTitle", [""])[0]) 
                lastjob.JobCopies = int(fields.get("pykotaCopies", [0])[0])
                lastjob.JobOptions = self.databaseToUserCharset(fields.get("pykotaOptions", [""])[0]) 
                lastjob.JobHostName = fields.get("pykotaHostName", [""])[0]
                lastjob.JobSizeBytes = fields.get("pykotaJobSizeBytes", [0L])[0]
                lastjob.JobBillingCode = self.databaseToUserCharset(fields.get("pykotaBillingCode", [None])[0])
                lastjob.JobMD5Sum = fields.get("pykotaMD5Sum", [None])[0]
                lastjob.JobPages = fields.get("pykotaPages", [""])[0]
                try :
                    lastjob.PrecomputedJobSize = int(fields.get("pykotaPrecomputedJobSize", [0])[0])
                except ValueError :    
                    lastjob.PrecomputedJobSize = None
                try :    
                    lastjob.PrecomputedJobPrice = float(fields.get("pykotaPrecomputedJobPrice", [0.0])[0])
                except ValueError :    
                    lastjob.PrecomputedJobPrice = None
                if lastjob.JobTitle == lastjob.JobFileName == lastjob.JobOptions == "hidden" :
                    (lastjob.JobTitle, lastjob.JobFileName, lastjob.JobOptions) = (_("Hidden because of privacy concerns"),) * 3
                date = fields.get("createTimestamp", ["19700101000000Z"])[0] # It's in UTC !
                mxtime = DateTime.strptime(date[:14], "%Y%m%d%H%M%S").localtime()
                lastjob.JobDate = mxtime.strftime("%Y%m%d %H:%M:%S")
                lastjob.Exists = 1
        return lastjob
        
    def getGroupMembersFromBackend(self, group) :        
        """Returns the group's members list."""
        groupmembers = []
        gname = self.userCharsetToDatabase(group.Name)
        result = self.doSearch("(&(objectClass=pykotaGroup)(|(pykotaGroupName=%s)(%s=%s)))" % \
                                  (gname, self.info["grouprdn"], gname), \
                                  [self.info["groupmembers"]], \
                                  base=self.info["groupbase"])
        if result :
            for username in result[0][1].get(self.info["groupmembers"], []) :
                groupmembers.append(self.getUser(self.databaseToUserCharset(username)))
        return groupmembers        
        
    def getUserGroupsFromBackend(self, user) :        
        """Returns the user's groups list."""
        groups = []
        uname = self.userCharsetToDatabase(user.Name)
        result = self.doSearch("(&(objectClass=pykotaGroup)(%s=%s))" % \
                                  (self.info["groupmembers"], uname), \
                                  [self.info["grouprdn"], "pykotaGroupName", "pykotaLimitBy"], \
                                  base=self.info["groupbase"])
        if result :
            for (groupid, fields) in result :
                groupname = self.databaseToUserCharset((fields.get("pykotaGroupName", [None]) or fields.get(self.info["grouprdn"], [None]))[0])
                group = self.getFromCache("GROUPS", groupname)
                if group is None :
                    group = StorageGroup(self, groupname)
                    group.ident = groupid
                    group.LimitBy = fields.get("pykotaLimitBy")
                    if group.LimitBy is not None :
                        group.LimitBy = group.LimitBy[0]
                    else :    
                        group.LimitBy = "quota"
                    group.AccountBalance = 0.0
                    group.LifeTimePaid = 0.0
                    for member in self.getGroupMembers(group) :
                        if member.Exists :
                            group.AccountBalance += member.AccountBalance
                            group.LifeTimePaid += member.LifeTimePaid
                    group.Exists = 1
                    self.cacheEntry("GROUPS", group.Name, group)
                groups.append(group)
        return groups        
        
    def getParentPrintersFromBackend(self, printer) :    
        """Get all the printer groups this printer is a member of."""
        pgroups = []
        result = self.doSearch("(&(objectClass=pykotaPrinter)(uniqueMember=%s))" % \
                                  printer.ident, \
                                  ["pykotaPrinterName"], \
                                  base=self.info["printerbase"])
        if result :
            for (printerid, fields) in result :
                if printerid != printer.ident : # In case of integrity violation.
                    parentprinter = self.getPrinter(self.databaseToUserCharset(fields.get("pykotaPrinterName")[0]))
                    if parentprinter.Exists :
                        pgroups.append(parentprinter)
        return pgroups
        
    def getMatchingPrinters(self, printerpattern) :
        """Returns the list of all printers for which name matches a certain pattern."""
        printers = []
        # see comment at the same place in pgstorage.py
        result = self.doSearch("objectClass=pykotaPrinter", \
                                  ["pykotaPrinterName", "pykotaPricePerPage", "pykotaPricePerJob", "pykotaMaxJobSize", "pykotaPassThrough", "uniqueMember", "description"], \
                                  base=self.info["printerbase"])
        if result :
            patterns = printerpattern.split(",")
            for (printerid, fields) in result :
                printername = self.databaseToUserCharset(fields.get("pykotaPrinterName", [""])[0] or fields.get(self.info["printerrdn"], [""])[0])
                if self.tool.matchString(printername, patterns) :
                    printer = StoragePrinter(self, printername)
                    printer.ident = printerid
                    printer.PricePerJob = float(fields.get("pykotaPricePerJob", [0.0])[0] or 0.0)
                    printer.PricePerPage = float(fields.get("pykotaPricePerPage", [0.0])[0] or 0.0)
                    printer.MaxJobSize = int(fields.get("pykotaMaxJobSize", [0])[0])
                    printer.PassThrough = fields.get("pykotaPassThrough", [None])[0]
                    if printer.PassThrough in (1, "1", "t", "true", "TRUE", "True") :
                        printer.PassThrough = 1
                    else :
                        printer.PassThrough = 0
                    printer.uniqueMember = fields.get("uniqueMember", [])
                    printer.Description = self.databaseToUserCharset(fields.get("description", [""])[0]) 
                    printer.Exists = 1
                    printers.append(printer)
                    self.cacheEntry("PRINTERS", printer.Name, printer)
        return printers        
        
    def getMatchingUsers(self, userpattern) :
        """Returns the list of all users for which name matches a certain pattern."""
        users = []
        # see comment at the same place in pgstorage.py
        result = self.doSearch("objectClass=pykotaAccount", \
                                  ["pykotaUserName", "pykotaLimitBy", self.info["usermail"], "pykotaOverCharge"], \
                                  base=self.info["userbase"])
        if result :
            patterns = userpattern.split(",")
            for (userid, fields) in result :
                username = self.databaseToUserCharset(fields.get("pykotaUserName", [""])[0] or fields.get(self.info["userrdn"], [""])[0])
                if self.tool.matchString(username, patterns) :
                    user = StorageUser(self, username)
                    user.ident = userid
                    user.Email = fields.get(self.info["usermail"], [None])[0]
                    user.LimitBy = fields.get("pykotaLimitBy", ["quota"])[0]
                    user.OverCharge = float(fields.get("pykotaOverCharge", [1.0])[0])
                    uname = self.userCharsetToDatabase(username)
                    result = self.doSearch("(&(objectClass=pykotaAccountBalance)(|(pykotaUserName=%s)(%s=%s)))" % \
                                              (uname, self.info["balancerdn"], uname), \
                                              ["pykotaBalance", "pykotaLifeTimePaid", "pykotaPayments"], \
                                              base=self.info["balancebase"])
                    if not result :
                        raise PyKotaStorageError, _("No pykotaAccountBalance object found for user %s. Did you create LDAP entries manually ?") % username
                    else :
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
                        user.Payments = []
                        for payment in fields.get("pykotaPayments", []) :
                            try :
                                (date, amount, description) = payment.split(" # ")
                            except ValueError :
                                # Payment with no description (old Payment)
                                (date, amount) = payment.split(" # ")
                                description = ""
                            else :    
                                description = self.databaseToUserCharset(base64.decodestring(description))
                            user.Payments.append((date, float(amount), description))
                    user.Exists = 1
                    users.append(user)
                    self.cacheEntry("USERS", user.Name, user)
        return users       
        
    def getMatchingGroups(self, grouppattern) :
        """Returns the list of all groups for which name matches a certain pattern."""
        groups = []
        # see comment at the same place in pgstorage.py
        result = self.doSearch("objectClass=pykotaGroup", \
                                  ["pykotaGroupName", "pykotaLimitBy"], \
                                  base=self.info["groupbase"])
        if result :
            patterns = grouppattern.split(",")
            for (groupid, fields) in result :
                groupname = self.databaseToUserCharset(fields.get("pykotaGroupName", [""])[0] or fields.get(self.info["grouprdn"], [""])[0])
                if self.tool.matchString(groupname, patterns) :
                    group = StorageGroup(self, groupname)
                    group.ident = groupid
                    group.Name = fields.get("pykotaGroupName", [self.databaseToUserCharset(groupname)])[0] 
                    group.LimitBy = fields.get("pykotaLimitBy", ["quota"])[0]
                    group.AccountBalance = 0.0
                    group.LifeTimePaid = 0.0
                    for member in self.getGroupMembers(group) :
                        if member.Exists :
                            group.AccountBalance += member.AccountBalance
                            group.LifeTimePaid += member.LifeTimePaid
                    group.Exists = 1
        return groups
        
    def getPrinterUsersAndQuotas(self, printer, names=["*"]) :        
        """Returns the list of users who uses a given printer, along with their quotas."""
        usersandquotas = []
        pname = self.userCharsetToDatabase(printer.Name)
        names = [self.userCharsetToDatabase(n) for n in names]
        if self.info["userquotabase"].lower() == "user" :
           base = self.info["userbase"]
        else :
           base = self.info["userquotabase"]
        result = self.doSearch("(&(objectClass=pykotaUserPQuota)(pykotaPrinterName=%s)(|%s))" % \
                                  (pname, "".join(["(pykotaUserName=%s)" % uname for uname in names])), \
                                  ["pykotaUserName", "pykotaPageCounter", "pykotaLifePageCounter", "pykotaSoftLimit", "pykotaHardLimit", "pykotaDateLimit", "pykotaWarnCount"], \
                                  base=base)
        if result :
            for (userquotaid, fields) in result :
                user = self.getUser(self.databaseToUserCharset(fields.get("pykotaUserName")[0]))
                userpquota = StorageUserPQuota(self, user, printer)
                userpquota.ident = userquotaid
                userpquota.PageCounter = int(fields.get("pykotaPageCounter", [0])[0])
                userpquota.LifePageCounter = int(fields.get("pykotaLifePageCounter", [0])[0])
                userpquota.WarnCount = int(fields.get("pykotaWarnCount", [0])[0])
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
                self.cacheEntry("USERPQUOTAS", "%s@%s" % (user.Name, printer.Name), userpquota)
        usersandquotas.sort(lambda x, y : cmp(x[0].Name, y[0].Name))            
        return usersandquotas
                
    def getPrinterGroupsAndQuotas(self, printer, names=["*"]) :        
        """Returns the list of groups which uses a given printer, along with their quotas."""
        groupsandquotas = []
        pname = self.userCharsetToDatabase(printer.Name)
        names = [self.userCharsetToDatabase(n) for n in names]
        if self.info["groupquotabase"].lower() == "group" :
           base = self.info["groupbase"]
        else :
           base = self.info["groupquotabase"]
        result = self.doSearch("(&(objectClass=pykotaGroupPQuota)(pykotaPrinterName=%s)(|%s))" % \
                                  (pname, "".join(["(pykotaGroupName=%s)" % gname for gname in names])), \
                                  ["pykotaGroupName"], \
                                  base=base)
        if result :
            for (groupquotaid, fields) in result :
                group = self.getGroup(self.databaseToUserCharset(fields.get("pykotaGroupName")[0]))
                grouppquota = self.getGroupPQuota(group, printer)
                groupsandquotas.append((group, grouppquota))
        groupsandquotas.sort(lambda x, y : cmp(x[0].Name, y[0].Name))            
        return groupsandquotas
        
    def addPrinter(self, printername) :        
        """Adds a printer to the quota storage, returns it."""
        printername = self.userCharsetToDatabase(printername)
        fields = { self.info["printerrdn"] : printername,
                   "objectClass" : ["pykotaObject", "pykotaPrinter"],
                   "cn" : printername,
                   "pykotaPrinterName" : printername,
                   "pykotaPricePerPage" : "0.0",
                   "pykotaPricePerJob" : "0.0",
                   "pykotaMaxJobSize" : "0",
                   "pykotaPassThrough" : "0",
                 } 
        dn = "%s=%s,%s" % (self.info["printerrdn"], printername, self.info["printerbase"])
        self.doAdd(dn, fields)
        return self.getPrinter(printername)
        
    def addUser(self, user) :        
        """Adds a user to the quota storage, returns it."""
        uname = self.userCharsetToDatabase(user.Name)
        newfields = {
                       "pykotaUserName" : uname,
                       "pykotaLimitBy" : (user.LimitBy or "quota"),
                       "pykotaOverCharge" : str(user.OverCharge),
                    }   
                       
        if user.Email :
            newfields.update({self.info["usermail"]: user.Email})
        mustadd = 1
        if self.info["newuser"].lower() != 'below' :
            try :
                (where, action) = [s.strip() for s in self.info["newuser"].split(",")]
            except ValueError :
                (where, action) = (self.info["newuser"].strip(), "fail")
            result = self.doSearch("(&(objectClass=%s)(%s=%s))" % \
                                      (where, self.info["userrdn"], uname), \
                                      None, \
                                      base=self.info["userbase"])
            if result :
                (dn, fields) = result[0]
                oc = fields.get("objectClass", fields.get("objectclass", []))
                oc.extend(["pykotaAccount", "pykotaAccountBalance"])
                fields.update(newfields)
                fields.update({ "pykotaBalance" : str(user.AccountBalance or 0.0),
                                "pykotaLifeTimePaid" : str(user.LifeTimePaid or 0.0), })   
                self.doModify(dn, fields)
                mustadd = 0
            else :
                message = _("Unable to find an existing objectClass %s entry with %s=%s to attach pykotaAccount objectClass") % (where, self.info["userrdn"], user.Name)
                if action.lower() == "warn" :    
                    self.tool.printInfo(_("%s. A new entry will be created instead.") % message, "warn")
                else : # 'fail' or incorrect setting
                    raise PyKotaStorageError, "%s. Action aborted. Please check your configuration." % message
                
        if mustadd :
            if self.info["userbase"] == self.info["balancebase"] :            
                fields = { self.info["userrdn"] : uname,
                           "objectClass" : ["pykotaObject", "pykotaAccount", "pykotaAccountBalance"],
                           "cn" : uname,
                           "pykotaBalance" : str(user.AccountBalance or 0.0),
                           "pykotaLifeTimePaid" : str(user.LifeTimePaid or 0.0), 
                         } 
            else :             
                fields = { self.info["userrdn"] : uname,
                           "objectClass" : ["pykotaObject", "pykotaAccount"],
                           "cn" : uname,
                         } 
            fields.update(newfields)         
            dn = "%s=%s,%s" % (self.info["userrdn"], uname, self.info["userbase"])
            self.doAdd(dn, fields)
            if self.info["userbase"] != self.info["balancebase"] :            
                fields = { self.info["balancerdn"] : uname,
                           "objectClass" : ["pykotaObject", "pykotaAccountBalance"],
                           "cn" : uname,
                           "pykotaBalance" : str(user.AccountBalance or 0.0),
                           "pykotaLifeTimePaid" : str(user.LifeTimePaid or 0.0),  
                         } 
                dn = "%s=%s,%s" % (self.info["balancerdn"], uname, self.info["balancebase"])
                self.doAdd(dn, fields)
            
        return self.getUser(user.Name)
        
    def addGroup(self, group) :        
        """Adds a group to the quota storage, returns it."""
        gname = self.userCharsetToDatabase(group.Name)
        newfields = { 
                      "pykotaGroupName" : gname,
                      "pykotaLimitBy" : (group.LimitBy or "quota"),
                    } 
        mustadd = 1
        if self.info["newgroup"].lower() != 'below' :
            try :
                (where, action) = [s.strip() for s in self.info["newgroup"].split(",")]
            except ValueError :
                (where, action) = (self.info["newgroup"].strip(), "fail")
            result = self.doSearch("(&(objectClass=%s)(%s=%s))" % \
                                      (where, self.info["grouprdn"], gname), \
                                      None, \
                                      base=self.info["groupbase"])
            if result :
                (dn, fields) = result[0]
                oc = fields.get("objectClass", fields.get("objectclass", []))
                oc.extend(["pykotaGroup"])
                fields.update(newfields)
                self.doModify(dn, fields)
                mustadd = 0
            else :
                message = _("Unable to find an existing entry to attach pykotaGroup objectclass %s") % group.Name
                if action.lower() == "warn" :    
                    self.tool.printInfo("%s. A new entry will be created instead." % message, "warn")
                else : # 'fail' or incorrect setting
                    raise PyKotaStorageError, "%s. Action aborted. Please check your configuration." % message
                
        if mustadd :
            fields = { self.info["grouprdn"] : gname,
                       "objectClass" : ["pykotaObject", "pykotaGroup"],
                       "cn" : gname,
                     } 
            fields.update(newfields)         
            dn = "%s=%s,%s" % (self.info["grouprdn"], gname, self.info["groupbase"])
            self.doAdd(dn, fields)
        return self.getGroup(group.Name)
        
    def addUserToGroup(self, user, group) :    
        """Adds an user to a group."""
        if user.Name not in [u.Name for u in self.getGroupMembers(group)] :
            result = self.doSearch("objectClass=pykotaGroup", None, base=group.ident, scope=ldap.SCOPE_BASE)    
            if result :
                fields = result[0][1]
                if not fields.has_key(self.info["groupmembers"]) :
                    fields[self.info["groupmembers"]] = []
                fields[self.info["groupmembers"]].append(self.userCharsetToDatabase(user.Name))
                self.doModify(group.ident, fields)
                group.Members.append(user)
                
    def addUserPQuota(self, user, printer) :
        """Initializes a user print quota on a printer."""
        uuid = self.genUUID()
        uname = self.userCharsetToDatabase(user.Name)
        pname = self.userCharsetToDatabase(printer.Name)
        fields = { "cn" : uuid,
                   "objectClass" : ["pykotaObject", "pykotaUserPQuota"],
                   "pykotaUserName" : uname,
                   "pykotaPrinterName" : pname,
                   "pykotaDateLimit" : "None",
                   "pykotaPageCounter" : "0",
                   "pykotaLifePageCounter" : "0",
                   "pykotaWarnCount" : "0",
                 } 
        if self.info["userquotabase"].lower() == "user" :
            dn = "cn=%s,%s" % (uuid, user.ident)
        else :    
            dn = "cn=%s,%s" % (uuid, self.info["userquotabase"])
        self.doAdd(dn, fields)
        return self.getUserPQuota(user, printer)
        
    def addGroupPQuota(self, group, printer) :
        """Initializes a group print quota on a printer."""
        uuid = self.genUUID()
        gname = self.userCharsetToDatabase(group.Name)
        pname = self.userCharsetToDatabase(printer.Name)
        fields = { "cn" : uuid,
                   "objectClass" : ["pykotaObject", "pykotaGroupPQuota"],
                   "pykotaGroupName" : gname,
                   "pykotaPrinterName" : pname,
                   "pykotaDateLimit" : "None",
                 } 
        if self.info["groupquotabase"].lower() == "group" :
            dn = "cn=%s,%s" % (uuid, group.ident)
        else :    
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
        
    def writePrinterDescription(self, printer) :    
        """Write the printer's description back into the storage."""
        fields = {
                   "description" : self.userCharsetToDatabase(printer.Description or ""),
                 }
        if fields["description"] :
            self.doModify(printer.ident, fields)
            
    def setPrinterMaxJobSize(self, printer, maxjobsize) :     
        """Write the printer's maxjobsize attribute."""
        fields = {
                   "pykotaMaxJobSize" : (maxjobsize and str(maxjobsize)) or "0",
                 }
        self.doModify(printer.ident, fields)
        
    def setPrinterPassThroughMode(self, printer, passthrough) :
        """Write the printer's passthrough attribute."""
        fields = {
                   "pykotaPassThrough" : (passthrough and "t") or "f",
                 }
        self.doModify(printer.ident, fields)
        
    def writeUserOverCharge(self, user, factor) :
        """Sets the user's overcharging coefficient."""
        fields = {
                   "pykotaOverCharge" : str(factor),
                 }
        self.doModify(user.ident, fields)
        
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
                   "pykotaDateLimit" : datelimit,
                 }
        return self.doModify(userpquota.ident, fields)
            
    def writeGroupPQuotaDateLimit(self, grouppquota, datelimit) :    
        """Sets the date limit permanently for a group print quota."""
        fields = {
                   "pykotaDateLimit" : datelimit,
                 }
        return self.doModify(grouppquota.ident, fields)
        
    def increaseUserPQuotaPagesCounters(self, userpquota, nbpages) :    
        """Increase page counters for a user print quota."""
        fields = {
                   "pykotaPageCounter" : { "operator" : "+", "value" : nbpages, "convert" : int },
                   "pykotaLifePageCounter" : { "operator" : "+", "value" : nbpages, "convert" : int },
                 }
        return self.doModify(userpquota.ident, fields)         
        
    def writeUserPQuotaPagesCounters(self, userpquota, newpagecounter, newlifepagecounter) :    
        """Sets the new page counters permanently for a user print quota."""
        fields = {
                   "pykotaPageCounter" : str(newpagecounter),
                   "pykotaLifePageCounter" : str(newlifepagecounter),
                   "pykotaDateLimit" : None,
                   "pykotaWarnCount" : "0",
                 }  
        return self.doModify(userpquota.ident, fields)         
       
    def decreaseUserAccountBalance(self, user, amount) :    
        """Decreases user's account balance from an amount."""
        fields = {
                   "pykotaBalance" : { "operator" : "-", "value" : amount, "convert" : float },
                 }
        return self.doModify(user.idbalance, fields, flushcache=1)         
       
    def writeUserAccountBalance(self, user, newbalance, newlifetimepaid=None) :    
        """Sets the new account balance and eventually new lifetime paid."""
        fields = {
                   "pykotaBalance" : str(newbalance),
                 }
        if newlifetimepaid is not None :
            fields.update({ "pykotaLifeTimePaid" : str(newlifetimepaid) })
        return self.doModify(user.idbalance, fields)         
            
    def writeNewPayment(self, user, amount, comment="") :
        """Adds a new payment to the payments history."""
        payments = []
        for payment in user.Payments :
            payments.append("%s # %s # %s" % (payment[0], str(payment[1]), base64.encodestring(self.userCharsetToDatabase(payment[2])).strip()))
        payments.append("%s # %s # %s" % (str(DateTime.now()), str(amount), base64.encodestring(self.userCharsetToDatabase(comment)).strip()))
        fields = {
                   "pykotaPayments" : payments,
                 }
        return self.doModify(user.idbalance, fields)         
        
    def writeLastJobSize(self, lastjob, jobsize, jobprice) :        
        """Sets the last job's size permanently."""
        fields = {
                   "pykotaJobSize" : str(jobsize),
                   "pykotaJobPrice" : str(jobprice),
                 }
        self.doModify(lastjob.ident, fields)         
        
    def writeJobNew(self, printer, user, jobid, pagecounter, action, jobsize=None, jobprice=None, filename=None, title=None, copies=None, options=None, clienthost=None, jobsizebytes=None, jobmd5sum=None, jobpages=None, jobbilling=None, precomputedsize=None, precomputedprice=None) :
        """Adds a job in a printer's history."""
        uname = self.userCharsetToDatabase(user.Name)
        pname = self.userCharsetToDatabase(printer.Name)
        if (not self.disablehistory) or (not printer.LastJob.Exists) :
            uuid = self.genUUID()
            dn = "cn=%s,%s" % (uuid, self.info["jobbase"])
        else :    
            uuid = printer.LastJob.ident[3:].split(",")[0]
            dn = printer.LastJob.ident
        if self.privacy :    
            # For legal reasons, we want to hide the title, filename and options
            title = filename = options = "hidden"
        fields = {
                   "objectClass" : ["pykotaObject", "pykotaJob"],
                   "cn" : uuid,
                   "pykotaUserName" : uname,
                   "pykotaPrinterName" : pname,
                   "pykotaJobId" : jobid,
                   "pykotaPrinterPageCounter" : str(pagecounter),
                   "pykotaAction" : action,
                   "pykotaFileName" : ((filename is None) and "None") or self.userCharsetToDatabase(filename), 
                   "pykotaTitle" : ((title is None) and "None") or self.userCharsetToDatabase(title), 
                   "pykotaCopies" : str(copies), 
                   "pykotaOptions" : ((options is None) and "None") or self.userCharsetToDatabase(options), 
                   "pykotaHostName" : str(clienthost), 
                   "pykotaJobSizeBytes" : str(jobsizebytes),
                   "pykotaMD5Sum" : str(jobmd5sum),
                   "pykotaPages" : jobpages,            # don't add this attribute if it is not set, so no string conversion
                   "pykotaBillingCode" : self.userCharsetToDatabase(jobbilling), # don't add this attribute if it is not set, so no string conversion
                   "pykotaPrecomputedJobSize" : str(precomputedsize),
                   "pykotaPrecomputedJobPrice" : str(precomputedprice),
                 }
        if (not self.disablehistory) or (not printer.LastJob.Exists) :
            if jobsize is not None :         
                fields.update({ "pykotaJobSize" : str(jobsize), "pykotaJobPrice" : str(jobprice) })
            self.doAdd(dn, fields)
        else :    
            # here we explicitly want to reset jobsize to 'None' if needed
            fields.update({ "pykotaJobSize" : str(jobsize), "pykotaJobPrice" : str(jobprice) })
            self.doModify(dn, fields)
            
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
                       "pykotaPrinterName" : pname,
                       "pykotaLastJobIdent" : uuid,
                     }  
            self.doAdd(lastjdn, fields)          
            
    def writeUserPQuotaLimits(self, userpquota, softlimit, hardlimit) :
        """Sets soft and hard limits for a user quota."""
        fields = { 
                   "pykotaSoftLimit" : str(softlimit),
                   "pykotaHardLimit" : str(hardlimit),
                   "pykotaDateLimit" : "None",
                   "pykotaWarnCount" : "0",
                 }
        self.doModify(userpquota.ident, fields)
        
    def writeUserPQuotaWarnCount(self, userpquota, warncount) :
        """Sets the warn counter value for a user quota."""
        fields = { 
                   "pykotaWarnCount" : str(warncount or 0),
                 }
        self.doModify(userpquota.ident, fields)
        
    def increaseUserPQuotaWarnCount(self, userpquota) :
        """Increases the warn counter value for a user quota."""
        fields = {
                   "pykotaWarnCount" : { "operator" : "+", "value" : 1, "convert" : int },
                 }
        return self.doModify(userpquota.ident, fields)         
        
    def writeGroupPQuotaLimits(self, grouppquota, softlimit, hardlimit) :
        """Sets soft and hard limits for a group quota on a specific printer."""
        fields = { 
                   "pykotaSoftLimit" : str(softlimit),
                   "pykotaHardLimit" : str(hardlimit),
                   "pykotaDateLimit" : "None",
                 }
        self.doModify(grouppquota.ident, fields)
            
    def writePrinterToGroup(self, pgroup, printer) :
        """Puts a printer into a printer group."""
        if printer.ident not in pgroup.uniqueMember :
            pgroup.uniqueMember.append(printer.ident)
            fields = {
                       "uniqueMember" : pgroup.uniqueMember
                     }  
            self.doModify(pgroup.ident, fields)         
            
    def removePrinterFromGroup(self, pgroup, printer) :
        """Removes a printer from a printer group."""
        try :
            pgroup.uniqueMember.remove(printer.ident)
        except ValueError :    
            pass
        else :    
            fields = {
                       "uniqueMember" : pgroup.uniqueMember,
                     }  
            self.doModify(pgroup.ident, fields)         
            
    def retrieveHistory(self, user=None, printer=None, hostname=None, billingcode=None, limit=100, start=None, end=None) :
        """Retrieves all print jobs for user on printer (or all) between start and end date, limited to first 100 results."""
        precond = "(objectClass=pykotaJob)"
        where = []
        if user is not None :
            where.append("(pykotaUserName=%s)" % self.userCharsetToDatabase(user.Name))
        if printer is not None :
            where.append("(pykotaPrinterName=%s)" % self.userCharsetToDatabase(printer.Name))
        if hostname is not None :
            where.append("(pykotaHostName=%s)" % hostname)
        if billingcode is not None :
            where.append("(pykotaBillingCode=%s)" % self.userCharsetToDatabase(billingcode))
        if where :    
            where = "(&%s)" % "".join([precond] + where)
        else :    
            where = precond
        jobs = []    
        result = self.doSearch(where, fields=[ "pykotaJobSizeBytes", 
                                               "pykotaHostName", 
                                               "pykotaUserName", 
                                               "pykotaPrinterName", 
                                               "pykotaJobId", 
                                               "pykotaPrinterPageCounter", 
                                               "pykotaAction", 
                                               "pykotaJobSize", 
                                               "pykotaJobPrice", 
                                               "pykotaFileName", 
                                               "pykotaTitle", 
                                               "pykotaCopies", 
                                               "pykotaOptions", 
                                               "pykotaBillingCode", 
                                               "pykotaPages", 
                                               "pykotaMD5Sum", 
                                               "pykotaPrecomputedJobSize",
                                               "pykotaPrecomputedJobPrice",
                                               "createTimestamp" ], 
                                      base=self.info["jobbase"])
        if result :
            for (ident, fields) in result :
                job = StorageJob(self)
                job.ident = ident
                job.JobId = fields.get("pykotaJobId")[0]
                job.PrinterPageCounter = int(fields.get("pykotaPrinterPageCounter", [0])[0] or 0)
                try :
                    job.JobSize = int(fields.get("pykotaJobSize", [0])[0])
                except ValueError :    
                    job.JobSize = None
                try :    
                    job.JobPrice = float(fields.get("pykotaJobPrice", [0.0])[0])
                except ValueError :
                    job.JobPrice = None
                job.JobAction = fields.get("pykotaAction", [""])[0]
                job.JobFileName = self.databaseToUserCharset(fields.get("pykotaFileName", [""])[0]) 
                job.JobTitle = self.databaseToUserCharset(fields.get("pykotaTitle", [""])[0]) 
                job.JobCopies = int(fields.get("pykotaCopies", [0])[0])
                job.JobOptions = self.databaseToUserCharset(fields.get("pykotaOptions", [""])[0]) 
                job.JobHostName = fields.get("pykotaHostName", [""])[0]
                job.JobSizeBytes = fields.get("pykotaJobSizeBytes", [0L])[0]
                job.JobBillingCode = self.databaseToUserCharset(fields.get("pykotaBillingCode", [None])[0])
                job.JobMD5Sum = fields.get("pykotaMD5Sum", [None])[0]
                job.JobPages = fields.get("pykotaPages", [""])[0]
                try :
                    job.PrecomputedJobSize = int(fields.get("pykotaPrecomputedJobSize", [0])[0])
                except ValueError :    
                    job.PrecomputedJobSize = None
                try :    
                    job.PrecomputedJobPrice = float(fields.get("pykotaPrecomputedJobPrice", [0.0])[0])
                except ValueError :
                    job.PrecomputedJobPrice = None
                if job.JobTitle == job.JobFileName == job.JobOptions == "hidden" :
                    (job.JobTitle, job.JobFileName, job.JobOptions) = (_("Hidden because of privacy concerns"),) * 3
                date = fields.get("createTimestamp", ["19700101000000Z"])[0] # It's in UTC !
                mxtime = DateTime.strptime(date[:14], "%Y%m%d%H%M%S").localtime()
                job.JobDate = mxtime.strftime("%Y%m%d %H:%M:%S")
                if ((start is None) and (end is None)) or \
                   ((start is None) and (job.JobDate <= end)) or \
                   ((end is None) and (job.JobDate >= start)) or \
                   ((job.JobDate >= start) and (job.JobDate <= end)) :
                    job.UserName = self.databaseToUserCharset(fields.get("pykotaUserName")[0])
                    job.PrinterName = self.databaseToUserCharset(fields.get("pykotaPrinterName")[0])
                    job.Exists = 1
                    jobs.append(job)
            jobs.sort(lambda x, y : cmp(y.JobDate, x.JobDate))        
            if limit :    
                jobs = jobs[:int(limit)]
        return jobs
        
    def deleteUser(self, user) :    
        """Completely deletes an user from the Quota Storage."""
        uname = self.userCharsetToDatabase(user.Name)
        todelete = []    
        result = self.doSearch("(&(objectClass=pykotaJob)(pykotaUserName=%s))" % uname, base=self.info["jobbase"])
        for (ident, fields) in result :
            todelete.append(ident)
        if self.info["userquotabase"].lower() == "user" :
            base = self.info["userbase"]
        else :
            base = self.info["userquotabase"]
        result = self.doSearch("(&(objectClass=pykotaUserPQuota)(pykotaUserName=%s))" % uname, \
                                  ["pykotaPrinterName", "pykotaUserName"], \
                                  base=base)
        for (ident, fields) in result :
            # ensure the user print quota entry will be deleted
            todelete.append(ident)
            
            # if last job of current printer was printed by the user
            # to delete, we also need to delete the printer's last job entry.
            printer = self.getPrinter(self.databaseToUserCharset(fields["pykotaPrinterName"][0]))
            if printer.LastJob.UserName == user.Name :
                todelete.append(printer.LastJob.lastjobident)
            
        for ident in todelete :    
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
            if fields.get("objectClass") or fields.get("objectclass") :
                self.doModify(user.ident, fields, ignoreold=0)        
            else :    
                self.doDelete(user.ident)
        result = self.doSearch("(&(objectClass=pykotaAccountBalance)(pykotaUserName=%s))" % \
                                   uname, \
                                   ["pykotaUserName"], \
                                   base=self.info["balancebase"])
        for (ident, fields) in result :
            self.doDelete(ident)
        
    def deleteGroup(self, group) :    
        """Completely deletes a group from the Quota Storage."""
        gname = self.userCharsetToDatabase(group.Name)
        if self.info["groupquotabase"].lower() == "group" :
            base = self.info["groupbase"]
        else :
            base = self.info["groupquotabase"]
        result = self.doSearch("(&(objectClass=pykotaGroupPQuota)(pykotaGroupName=%s))" % \
                                  gname, \
                                  ["pykotaGroupName"], \
                                  base=base)
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
            if fields.get("objectClass") or fields.get("objectclass") :
                self.doModify(group.ident, fields, ignoreold=0)        
            else :    
                self.doDelete(group.ident)
                
    def deletePrinter(self, printer) :    
        """Completely deletes a printer from the Quota Storage."""
        pname = self.userCharsetToDatabase(printer.Name)
        result = self.doSearch("(&(objectClass=pykotaLastJob)(pykotaPrinterName=%s))" % pname, base=self.info["lastjobbase"])
        for (ident, fields) in result :
            self.doDelete(ident)
        result = self.doSearch("(&(objectClass=pykotaJob)(pykotaPrinterName=%s))" % pname, base=self.info["jobbase"])
        for (ident, fields) in result :
            self.doDelete(ident)
        if self.info["groupquotabase"].lower() == "group" :
            base = self.info["groupbase"]
        else :
            base = self.info["groupquotabase"]
        result = self.doSearch("(&(objectClass=pykotaGroupPQuota)(pykotaPrinterName=%s))" % pname, base=base)
        for (ident, fields) in result :
            self.doDelete(ident)
        if self.info["userquotabase"].lower() == "user" :
            base = self.info["userbase"]
        else :
            base = self.info["userquotabase"]
        result = self.doSearch("(&(objectClass=pykotaUserPQuota)(pykotaPrinterName=%s))" % pname, base=base)
        for (ident, fields) in result :
            self.doDelete(ident)
        for parent in self.getParentPrinters(printer) :  
            try :
                parent.uniqueMember.remove(printer.ident)
            except ValueError :    
                pass
            else :    
                fields = {
                           "uniqueMember" : parent.uniqueMember,
                         }  
                self.doModify(parent.ident, fields)         
        self.doDelete(printer.ident)    
        
    def deleteBillingCode(self, code) :
        """Deletes a billing code from the Quota Storage (no entries are deleted from the history)"""
        self.doDelete(code.ident)
        
    def extractPrinters(self, extractonly={}) :
        """Extracts all printer records."""
        pname = extractonly.get("printername")
        entries = [p for p in [self.getPrinter(name) for name in self.getAllPrintersNames(pname)] if p.Exists]
        if entries :
            result = [ ("dn", "printername", "priceperpage", "priceperjob", "description", "maxjobsize", "passthrough") ]
            for entry in entries :
                if entry.PassThrough in (1, "1", "t", "true", "T", "TRUE", "True") :
                    passthrough = "t"
                else :    
                    passthrough = "f"
                result.append((entry.ident, entry.Name, entry.PricePerPage, entry.PricePerJob, entry.Description, entry.MaxJobSize, passthrough))
            return result 
        
    def extractUsers(self, extractonly={}) :
        """Extracts all user records."""
        uname = extractonly.get("username")
        entries = [u for u in [self.getUser(name) for name in self.getAllUsersNames(uname)] if u.Exists]
        if entries :
            result = [ ("dn", "username", "balance", "lifetimepaid", "limitby", "email") ]
            for entry in entries :
                result.append((entry.ident, entry.Name, entry.AccountBalance, entry.LifeTimePaid, entry.LimitBy, entry.Email))
            return result 
        
    def extractBillingcodes(self, extractonly={}) :
        """Extracts all billing codes records."""
        billingcode = extractonly.get("billingcode")
        entries = [b for b in [self.getBillingCode(label) for label in self.getAllBillingCodes(billingcode)] if b.Exists]
        if entries :
            result = [ ("dn", "billingcode", "balance", "pagecounter", "description") ]
            for entry in entries :
                result.append((entry.ident, entry.BillingCode, entry.Balance, entry.PageCounter, entry.Description))
            return result 
        
    def extractGroups(self, extractonly={}) :
        """Extracts all group records."""
        gname = extractonly.get("groupname")
        entries = [g for g in [self.getGroup(name) for name in self.getAllGroupsNames(gname)] if g.Exists]
        if entries :
            result = [ ("dn", "groupname", "limitby", "balance", "lifetimepaid") ]
            for entry in entries :
                result.append((entry.ident, entry.Name, entry.LimitBy, entry.AccountBalance, entry.LifeTimePaid))
            return result 
        
    def extractPayments(self, extractonly={}) :
        """Extracts all payment records."""
        uname = extractonly.get("username")
        entries = [u for u in [self.getUser(name) for name in self.getAllUsersNames(uname)] if u.Exists]
        if entries :
            result = [ ("username", "amount", "date", "description") ]
            for entry in entries :
                for (date, amount, description) in entry.Payments :
                    result.append((entry.Name, amount, date, description))
            return result        
        
    def extractUpquotas(self, extractonly={}) :
        """Extracts all userpquota records."""
        pname = extractonly.get("printername")
        entries = [p for p in [self.getPrinter(name) for name in self.getAllPrintersNames(pname)] if p.Exists]
        if entries :
            result = [ ("username", "printername", "dn", "userdn", "printerdn", "lifepagecounter", "pagecounter", "softlimit", "hardlimit", "datelimit") ]
            uname = extractonly.get("username")
            for entry in entries :
                for (user, userpquota) in self.getPrinterUsersAndQuotas(entry, names=[uname or "*"]) :
                    result.append((user.Name, entry.Name, userpquota.ident, user.ident, entry.ident, userpquota.LifePageCounter, userpquota.PageCounter, userpquota.SoftLimit, userpquota.HardLimit, userpquota.DateLimit))
            return result
        
    def extractGpquotas(self, extractonly={}) :
        """Extracts all grouppquota records."""
        pname = extractonly.get("printername")
        entries = [p for p in [self.getPrinter(name) for name in self.getAllPrintersNames(pname)] if p.Exists]
        if entries :
            result = [ ("groupname", "printername", "dn", "groupdn", "printerdn", "lifepagecounter", "pagecounter", "softlimit", "hardlimit", "datelimit") ]
            gname = extractonly.get("groupname")
            for entry in entries :
                for (group, grouppquota) in self.getPrinterGroupsAndQuotas(entry, names=[gname or "*"]) :
                    result.append((group.Name, entry.Name, grouppquota.ident, group.ident, entry.ident, grouppquota.LifePageCounter, grouppquota.PageCounter, grouppquota.SoftLimit, grouppquota.HardLimit, grouppquota.DateLimit))
            return result
        
    def extractUmembers(self, extractonly={}) :
        """Extracts all user groups members."""
        gname = extractonly.get("groupname")
        entries = [g for g in [self.getGroup(name) for name in self.getAllGroupsNames(gname)] if g.Exists]
        if entries :
            result = [ ("groupname", "username", "groupdn", "userdn") ]
            uname = extractonly.get("username")
            for entry in entries :
                for member in entry.Members :
                    if (uname is None) or (member.Name == uname) :
                        result.append((entry.Name, member.Name, entry.ident, member.ident))
            return result        
                
    def extractPmembers(self, extractonly={}) :
        """Extracts all printer groups members."""
        pname = extractonly.get("printername")
        entries = [p for p in [self.getPrinter(name) for name in self.getAllPrintersNames(pname)] if p.Exists]
        if entries :
            result = [ ("pgroupname", "printername", "pgroupdn", "printerdn") ]
            pgname = extractonly.get("pgroupname")
            for entry in entries :
                for parent in self.getParentPrinters(entry) :
                    if (pgname is None) or (parent.Name == pgname) :
                        result.append((parent.Name, entry.Name, parent.ident, entry.ident))
            return result        
        
    def extractHistory(self, extractonly={}) :
        """Extracts all jobhistory records."""
        uname = extractonly.get("username")
        if uname :
            user = self.getUser(uname)
        else :    
            user = None
        pname = extractonly.get("printername")
        if pname :
            printer = self.getPrinter(pname)
        else :    
            printer = None
        startdate = extractonly.get("start")
        enddate = extractonly.get("end")
        (startdate, enddate) = self.cleanDates(startdate, enddate)
        entries = self.retrieveHistory(user, printer, hostname=extractonly.get("hostname"), billingcode=extractonly.get("billingcode"), limit=None, start=startdate, end=enddate)
        if entries :
            result = [ ("username", "printername", "dn", "jobid", "pagecounter", "jobsize", "action", "jobdate", "filename", "title", "copies", "options", "jobprice", "hostname", "jobsizebytes", "md5sum", "pages", "billingcode", "precomputedjobsize", "precomputedjobprice") ] 
            for entry in entries :
                result.append((entry.UserName, entry.PrinterName, entry.ident, entry.JobId, entry.PrinterPageCounter, entry.JobSize, entry.JobAction, entry.JobDate, entry.JobFileName, entry.JobTitle, entry.JobCopies, entry.JobOptions, entry.JobPrice, entry.JobHostName, entry.JobSizeBytes, entry.JobMD5Sum, entry.JobPages, entry.JobBillingCode, entry.PrecomputedJobSize, entry.PrecomputedJobPrice)) 
            return result
            
    def getBillingCodeFromBackend(self, label) :
        """Extracts billing code information given its label : returns first matching billing code."""
        code = StorageBillingCode(self, label)
        ulabel = self.userCharsetToDatabase(label)
        result = self.doSearch("(&(objectClass=pykotaBilling)(pykotaBillingCode=%s))" % \
                                  ulabel, \
                                  ["pykotaBillingCode", "pykotaBalance", "pykotaPageCounter", "description"], \
                                  base=self.info["billingcodebase"])
        if result :
            fields = result[0][1]       # take only first matching code, ignore the rest
            code.ident = result[0][0]
            code.BillingCode = self.databaseToUserCharset(fields.get("pykotaBillingCode", [ulabel])[0])
            code.PageCounter = int(fields.get("pykotaPageCounter", [0])[0])
            code.Balance = float(fields.get("pykotaBalance", [0.0])[0])
            code.Description = self.databaseToUserCharset(fields.get("description", [""])[0]) 
            code.Exists = 1
        return code    
        
    def addBillingCode(self, label) :
        """Adds a billing code to the quota storage, returns it."""
        uuid = self.genUUID()
        dn = "cn=%s,%s" % (uuid, self.info["billingcodebase"])
        fields = { "objectClass" : ["pykotaObject", "pykotaBilling"],
                   "cn" : uuid,
                   "pykotaBillingCode" : self.userCharsetToDatabase(label),
                   "pykotaPageCounter" : "0",
                   "pykotaBalance" : "0.0",
                 } 
        self.doAdd(dn, fields)
        return self.getBillingCode(label)
        
    def writeBillingCodeDescription(self, code) :
        """Sets the new description for a billing code."""
        fields = {
                   "description" : self.userCharsetToDatabase(code.Description or ""), 
                 }
        if fields["description"] :
            self.doModify(code.ident, fields)
            
    def getMatchingBillingCodes(self, billingcodepattern) :
        """Returns the list of all billing codes which match a certain pattern."""
        codes = []
        result = self.doSearch("objectClass=pykotaBilling", \
                                ["pykotaBillingCode", "description", "pykotaPageCounter", "pykotaBalance"], \
                                base=self.info["billingcodebase"])
        if result :
            patterns = billingcodepattern.split(",")
            for (codeid, fields) in result :
                bcode = self.databaseToUserCharset(fields.get("pykotaBillingCode", [""])[0])
                if self.tool.matchString(bcode, patterns) :
                    code = StorageBillingCode(self, codename)
                    code.ident = codeid
                    code.BillingCode = codename
                    code.PageCounter = int(fields.get("pykotaPageCounter", [0])[0])
                    code.Balance = float(fields.get("pykotaBalance", [0.0])[0])
                    code.Description = self.databaseToUserCharset(fields.get("description", [""])[0]) 
                    code.Exists = 1
                    codes.append(code)
                    self.cacheEntry("BILLINGCODES", code.BillingCode, code)
        return codes        
        
    def setBillingCodeValues(self, code, newpagecounter, newbalance) :
        """Sets the new page counter and balance for a billing code."""
        fields = {
                   "pykotaPageCounter" : str(newpagecounter),
                   "pykotaBalance" : str(newbalance),
                 }  
        return self.doModify(code.ident, fields)         
       
    def consumeBillingCode(self, code, pagecounter, balance) :
        """Consumes from a billing code."""
        fields = {
                   "pykotaBalance" : { "operator" : "-", "value" : balance, "convert" : float },
                   "pykotaPageCounter" : { "operator" : "+", "value" : pagecounter, "convert" : int },
                 }
        return self.doModify(code.ident, fields)         

