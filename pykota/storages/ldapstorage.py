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
# Revision 1.85  2004/10/24 12:55:09  jalet
# Missing spaces
#
# Revision 1.84  2004/10/12 08:58:53  jalet
# Now warnpykota only warns users who have already printed, to not confuse
# users who have just opened their account.
#
# Revision 1.83  2004/10/07 21:14:28  jalet
# Hopefully final fix for data encoding to and from the database
#
# Revision 1.82  2004/10/05 09:59:20  jalet
# Restore compatibility with Python 2.1
#
# Revision 1.81  2004/10/04 11:27:57  jalet
# Finished LDAP support for dumpykota.
#
# Revision 1.80  2004/10/03 19:57:57  jalet
# Dump of payments should work with LDAP backend now.
#
# Revision 1.79  2004/10/03 19:52:59  jalet
# More work done on LDAP and dumpykota
#
# Revision 1.78  2004/10/02 05:48:56  jalet
# Should now correctly deal with charsets both when storing into databases and when
# retrieving datas. Works with both PostgreSQL and LDAP.
#
# Revision 1.77  2004/09/28 14:29:00  jalet
# dumpykota for LDAP backend is almost there.
#
# Revision 1.76  2004/09/28 09:11:56  jalet
# Fix for accented chars in print job's title, filename, and options
#
# Revision 1.75  2004/09/24 20:21:50  jalet
# Fixed pykotaAccountBalance object location during creation
#
# Revision 1.74  2004/09/02 10:09:30  jalet
# Fixed bug in LDAP user deletion code which didn't correctly delete the user's
# pykotaLastJob entries.
#
# Revision 1.73  2004/07/17 20:37:27  jalet
# Missing file... Am I really stupid ?
#
# Revision 1.72  2004/07/01 19:56:43  jalet
# Better dispatching of error messages
#
# Revision 1.71  2004/07/01 17:45:49  jalet
# Added code to handle the description field for printers
#
# Revision 1.70  2004/06/10 20:50:25  jalet
# Better log message
#
# Revision 1.69  2004/06/05 22:18:04  jalet
# Now catches some exceptions earlier.
# storage.py and ldapstorage.py : removed old comments
#
# Revision 1.68  2004/06/05 22:03:50  jalet
# Payments history is now stored in database
#
# Revision 1.67  2004/06/03 23:14:10  jalet
# Now stores the job's size in bytes in the database.
# Preliminary work on payments storage : database schemas are OK now,
# but no code to store payments yet.
# Removed schema picture, not relevant anymore.
#
# Revision 1.66  2004/05/28 20:56:45  jalet
# Extended syntax for LDAP specific newuser and newgroup directives. Untested.
#
# Revision 1.65  2004/05/27 12:52:12  jalet
# More useful error message in case of misconfiguration of an LDAP  search base
# in pykota.conf
#
# Revision 1.64  2004/05/26 14:50:01  jalet
# First try at saving the job-originating-hostname in the database
#
# Revision 1.63  2004/05/06 12:37:46  jalet
# pkpgcounter : comments
# pkprinters : when --add is used, existing printers are now skipped.
#
# Revision 1.62  2004/03/05 14:31:58  jalet
# Improvement on strange history entries
#
# Revision 1.61  2004/03/05 13:19:53  jalet
# Code safer wrt entries created in other tools
#
# Revision 1.60  2004/03/02 14:39:02  jalet
# Final fix for printers searching
#
# Revision 1.59  2004/03/02 14:35:46  jalet
# Missing test when searching printer objects when these objects were manually
# created and don't contain the pykotaPrinterName attribute
#
# Revision 1.58  2004/02/27 09:30:33  jalet
# datelimit wasn't reset when modifying soft and hard limits with the LDAP backend
#
# Revision 1.57  2004/02/26 14:18:07  jalet
# Should fix the remaining bugs wrt printers groups and users groups.
#
# Revision 1.56  2004/02/25 16:52:39  jalet
# Small fix wrt empty user groups
#
# Revision 1.55  2004/02/23 22:53:21  jalet
# Don't retrieve data when it's not needed, to avoid database queries
#
# Revision 1.54  2004/02/20 16:38:39  jalet
# ldapcache directive marked as experimental
#
# Revision 1.53  2004/02/20 14:42:21  jalet
# Experimental ldapcache directive added
#
# Revision 1.52  2004/02/17 23:41:48  jalet
# Preliminary work on low-level LDAP specific cache.
#
# Revision 1.51  2004/02/04 13:24:41  jalet
# pkprinters can now remove printers from printers groups.
#
# Revision 1.50  2004/02/04 11:17:00  jalet
# pkprinters command line tool added.
#
# Revision 1.49  2004/01/29 22:35:45  jalet
# Small fix from Matt.
#
# Revision 1.48  2004/01/12 14:35:02  jalet
# Printing history added to CGI script.
#
# Revision 1.47  2004/01/10 09:44:02  jalet
# Fixed potential accuracy problem if a user printed on several printers at
# the very same time.
#
# Revision 1.46  2004/01/08 16:33:27  jalet
# Additionnal check to not create a circular printers group.
#
# Revision 1.45  2004/01/08 16:24:49  jalet
# edpykota now supports adding printers to printer groups.
#
# Revision 1.44  2004/01/08 14:10:33  jalet
# Copyright year changed.
#
# Revision 1.43  2004/01/06 14:24:59  jalet
# Printer groups should be cached now, if caching is enabled.
#
# Revision 1.42  2003/12/29 14:12:48  uid67467
# Tries to workaround possible integrity violations when retrieving printer groups
#
# Revision 1.41  2003/12/27 16:49:25  uid67467
# Should be ok now.
#
# Revision 1.40  2003/11/29 22:02:14  jalet
# Don't try to retrieve the user print quota information if current printer
# doesn't exist.
#
# Revision 1.39  2003/11/26 23:35:32  jalet
# Added a bit of code to support the setting of the user's email address
# which was ignored during writes for now.
#
# Revision 1.38  2003/11/24 09:54:06  jalet
# Small fix for LDAP when pykotaOptions attribute wasn't present.
#
# Revision 1.37  2003/11/23 19:01:37  jalet
# Job price added to history
#
# Revision 1.36  2003/11/21 14:28:46  jalet
# More complete job history.
#
# Revision 1.35  2003/11/12 13:06:37  jalet
# Bug fix wrt no user/group name command line argument to edpykota
#
# Revision 1.34  2003/10/24 08:37:55  jalet
# More complete messages in case of LDAP failure.
# LDAP database connection is now unbound on exit too.
#
# Revision 1.33  2003/10/08 07:01:20  jalet
# Job history can be disabled.
# Some typos in README.
# More messages in setup script.
#
# Revision 1.32  2003/10/07 14:23:25  jalet
# More work on cache
#
# Revision 1.31  2003/10/07 09:07:30  jalet
# Character encoding added to please latest version of Python
#
# Revision 1.30  2003/10/06 14:42:36  jalet
# LDAP group access will be slower when cache is disabled, but at least code
# is consistent with the rest of the caching mechanis, but at least code
# is consistent with the rest of the caching mechanism
#
# Revision 1.29  2003/10/06 13:12:28  jalet
# More work on caching
#
# Revision 1.28  2003/10/03 12:27:02  jalet
# Several optimizations, especially with LDAP backend
#
# Revision 1.27  2003/10/03 08:57:55  jalet
# Caching mechanism now caches all that's cacheable.
#
# Revision 1.26  2003/10/02 20:23:18  jalet
# Storage caching mechanism added.
#
# Revision 1.25  2003/08/20 15:56:24  jalet
# Better user and group deletion
#
# Revision 1.24  2003/07/29 20:55:17  jalet
# 1.14 is out !
#
# Revision 1.23  2003/07/29 19:52:32  jalet
# Forgot to read the email field from LDAP
#
# Revision 1.22  2003/07/29 09:54:03  jalet
# Added configurable LDAP mail attribute support
#
# Revision 1.21  2003/07/28 09:11:12  jalet
# PyKota now tries to add its attributes intelligently in existing LDAP
# directories.
#
# Revision 1.20  2003/07/25 10:41:30  jalet
# Better documentation.
# pykotme now displays the current user's account balance.
# Some test changed in ldap module.
#
# Revision 1.19  2003/07/14 14:18:16  jalet
# Wrong documentation strings
#
# Revision 1.18  2003/07/11 14:23:13  jalet
# When adding an user only adds one object containing both the user and
# its account balance instead of two objects.
#
# Revision 1.17  2003/07/07 12:51:07  jalet
# Small fix
#
# Revision 1.16  2003/07/07 12:11:13  jalet
# Small fix
#
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

import os
import types
import time
import md5
from mx import DateTime

from pykota.storage import PyKotaStorageError, BaseStorage, StorageObject, StorageUser, StorageGroup, StoragePrinter, StorageJob, StorageLastJob, StorageUserPQuota, StorageGroupPQuota

try :
    import ldap
    import ldap.modlist
except ImportError :    
    import sys
    # TODO : to translate or not to translate ?
    raise PyKotaStorageError, "This python version (%s) doesn't seem to have the python-ldap module installed correctly." % sys.version.split()[0]
    
class Storage(BaseStorage) :
    def __init__(self, pykotatool, host, dbname, user, passwd) :
        """Opens the LDAP connection."""
        BaseStorage.__init__(self, pykotatool)
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
            self.useldapcache = pykotatool.config.getLDAPCache()
            if self.useldapcache :
                self.tool.logdebug("Low-Level LDAP Caching enabled.")
                self.ldapcache = {} # low-level cache specific to LDAP backend
            self.closed = 0
            self.tool.logdebug("Database opened (host=%s, dbname=%s, user=%s)" % (host, dbname, user))
            
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
            raise PyKotaStorageError, (_("Search for %s(%s) from %s(scope=%s) returned no answer.") % (key, fields, base, scope)) + " : %s" % str(msg)
        else :     
            self.tool.logdebug("QUERY : Result : %s" % result)
            if self.useldapcache :
                for (dn, attributes) in result :
                    self.tool.logdebug("LDAP cache store %s => %s" % (dn, attributes))
                    self.ldapcache[dn] = attributes
            return result
            
    def doAdd(self, dn, fields) :
        """Adds an entry in the LDAP directory."""
        # TODO : store into LDAP specific cache
        fields = self.normalizeFields(fields)
        try :
            self.tool.logdebug("QUERY : ADD(%s, %s)" % (dn, str(fields)))
            entry = ldap.modlist.addModlist(fields)
            self.tool.logdebug("%s" % entry)
            self.database.add_s(dn, entry)
        except ldap.LDAPError, msg :
            raise PyKotaStorageError, (_("Problem adding LDAP entry (%s, %s)") % (dn, str(fields))) + " : %s" % str(msg)
        else :
            if self.useldapcache :
                self.tool.logdebug("LDAP cache add %s => %s" % (dn, fields))
                self.ldapcache[dn] = fields
            return dn
            
    def doDelete(self, dn) :
        """Deletes an entry from the LDAP directory."""
        # TODO : delete from LDAP specific cache
        try :
            self.tool.logdebug("QUERY : Delete(%s)" % dn)
            self.database.delete_s(dn)
        except ldap.LDAPError, msg :
            raise PyKotaStorageError, (_("Problem deleting LDAP entry (%s)") % dn) + " : %s" % str(msg)
        else :    
            if self.useldapcache :
                try :
                    self.tool.logdebug("LDAP cache del %s" % dn)
                    del self.ldapcache[dn]
                except KeyError :    
                    pass
            
    def doModify(self, dn, fields, ignoreold=1, flushcache=0) :
        """Modifies an entry in the LDAP directory."""
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
                if mtyp != "createTimestamp" :
                    modentry.append((mop, mtyp, mval))
            self.tool.logdebug("MODIFY : %s ==> %s ==> %s" % (fields, entry, modentry))
            if modentry :
                self.database.modify_s(dn, modentry)
        except ldap.LDAPError, msg :
            raise PyKotaStorageError, (_("Problem modifying LDAP entry (%s, %s)") % (dn, fields)) + " : %s" % str(msg)
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
            
    def getAllPrintersNames(self) :    
        """Extracts all printer names."""
        printernames = []
        result = self.doSearch("objectClass=pykotaPrinter", ["pykotaPrinterName"], base=self.info["printerbase"])
        if result :
            printernames = [record[1]["pykotaPrinterName"][0] for record in result]
        return printernames
        
    def getAllUsersNames(self) :    
        """Extracts all user names."""
        usernames = []
        result = self.doSearch("objectClass=pykotaAccount", ["pykotaUserName"], base=self.info["userbase"])
        if result :
            usernames = [record[1]["pykotaUserName"][0] for record in result]
        return usernames
        
    def getAllGroupsNames(self) :    
        """Extracts all group names."""
        groupnames = []
        result = self.doSearch("objectClass=pykotaGroup", ["pykotaGroupName"], base=self.info["groupbase"])
        if result :
            groupnames = [record[1]["pykotaGroupName"][0] for record in result]
        return groupnames
        
    def getUserNbJobsFromHistory(self, user) :
        """Returns the number of jobs the user has in history."""
        result = self.doSearch("(&(pykotaUserName=%s)(objectClass=pykotaJob))" % user.Name, None, base=self.info["jobbase"])
        return len(result)
        
    def getUserFromBackend(self, username) :    
        """Extracts user information given its name."""
        user = StorageUser(self, username)
        result = self.doSearch("(&(objectClass=pykotaAccount)(|(pykotaUserName=%s)(%s=%s)))" % (username, self.info["userrdn"], username), ["pykotaUserName", "pykotaLimitBy", self.info["usermail"]], base=self.info["userbase"])
        if result :
            fields = result[0][1]
            user.ident = result[0][0]
            user.Name = fields.get("pykotaUserName", [username])[0] 
            user.Email = fields.get(self.info["usermail"])
            if user.Email is not None :
                user.Email = user.Email[0]
            user.LimitBy = fields.get("pykotaLimitBy")
            if user.LimitBy is not None :
                user.LimitBy = user.LimitBy[0]
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
                    (date, amount) = payment.split(" # ")
                    user.Payments.append((date, amount))
            user.Exists = 1
        return user
       
    def getGroupFromBackend(self, groupname) :    
        """Extracts group information given its name."""
        group = StorageGroup(self, groupname)
        result = self.doSearch("(&(objectClass=pykotaGroup)(|(pykotaGroupName=%s)(%s=%s)))" % (groupname, self.info["grouprdn"], groupname), ["pykotaGroupName", "pykotaLimitBy"], base=self.info["groupbase"])
        if result :
            fields = result[0][1]
            group.ident = result[0][0]
            group.Name = fields.get("pykotaGroupName", [groupname])[0] 
            group.LimitBy = fields.get("pykotaLimitBy")
            if group.LimitBy is not None :
                group.LimitBy = group.LimitBy[0]
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
        result = self.doSearch("(&(objectClass=pykotaPrinter)(|(pykotaPrinterName=%s)(%s=%s)))" % (printername, self.info["printerrdn"], printername), ["pykotaPrinterName", "pykotaPricePerPage", "pykotaPricePerJob", "uniqueMember", "description"], base=self.info["printerbase"])
        if result :
            fields = result[0][1]       # take only first matching printer, ignore the rest
            printer.ident = result[0][0]
            printer.Name = fields.get("pykotaPrinterName", [printername])[0] 
            printer.PricePerJob = float(fields.get("pykotaPricePerJob", [0.0])[0] or 0.0)
            printer.PricePerPage = float(fields.get("pykotaPricePerPage", [0.0])[0] or 0.0)
            printer.uniqueMember = fields.get("uniqueMember", [])
            printer.Description = self.databaseToUserCharset(fields.get("description", [""])[0]) 
            printer.Exists = 1
        return printer    
        
    def getUserPQuotaFromBackend(self, user, printer) :        
        """Extracts a user print quota."""
        userpquota = StorageUserPQuota(self, user, printer)
        if printer.Exists and user.Exists :
            result = self.doSearch("(&(objectClass=pykotaUserPQuota)(pykotaUserName=%s)(pykotaPrinterName=%s))" % (user.Name, printer.Name), ["pykotaPageCounter", "pykotaLifePageCounter", "pykotaSoftLimit", "pykotaHardLimit", "pykotaDateLimit"], base=self.info["userquotabase"])
            if result :
                fields = result[0][1]
                userpquota.ident = result[0][0]
                userpquota.PageCounter = int(fields.get("pykotaPageCounter", [0])[0] or 0)
                userpquota.LifePageCounter = int(fields.get("pykotaLifePageCounter", [0])[0] or 0)
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
                usernamesfilter = "".join(["(pykotaUserName=%s)" % member.Name for member in self.getGroupMembers(group)])
                if usernamesfilter :
                    usernamesfilter = "(|%s)" % usernamesfilter
                result = self.doSearch("(&(objectClass=pykotaUserPQuota)(pykotaPrinterName=%s)%s)" % (printer.Name, usernamesfilter), ["pykotaPageCounter", "pykotaLifePageCounter"], base=self.info["userquotabase"])
                if result :
                    for userpquota in result :    
                        grouppquota.PageCounter += int(userpquota[1].get("pykotaPageCounter", [0])[0] or 0)
                        grouppquota.LifePageCounter += int(userpquota[1].get("pykotaLifePageCounter", [0])[0] or 0)
                grouppquota.Exists = 1
        return grouppquota
        
    def getPrinterLastJobFromBackend(self, printer) :        
        """Extracts a printer's last job information."""
        lastjob = StorageLastJob(self, printer)
        result = self.doSearch("(&(objectClass=pykotaLastjob)(|(pykotaPrinterName=%s)(%s=%s)))" % (printer.Name, self.info["printerrdn"], printer.Name), ["pykotaLastJobIdent"], base=self.info["lastjobbase"])
        if result :
            lastjob.lastjobident = result[0][0]
            lastjobident = result[0][1]["pykotaLastJobIdent"][0]
            result = None
            try :
                result = self.doSearch("objectClass=pykotaJob", ["pykotaJobSizeBytes", "pykotaHostName", "pykotaUserName", "pykotaJobId", "pykotaPrinterPageCounter", "pykotaJobSize", "pykotaAction", "pykotaJobPrice", "pykotaFileName", "pykotaTitle", "pykotaCopies", "pykotaOptions", "createTimestamp"], base="cn=%s,%s" % (lastjobident, self.info["jobbase"]), scope=ldap.SCOPE_BASE)
            except PyKotaStorageError :    
                pass # Last job entry exists, but job probably doesn't exist anymore. 
            if result :
                fields = result[0][1]
                lastjob.ident = result[0][0]
                lastjob.JobId = fields.get("pykotaJobId")[0]
                lastjob.UserName = fields.get("pykotaUserName")[0]
                lastjob.PrinterPageCounter = int(fields.get("pykotaPrinterPageCounter", [0])[0] or 0)
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
                date = fields.get("createTimestamp", ["19700101000000"])[0]
                year = int(date[:4])
                month = int(date[4:6])
                day = int(date[6:8])
                hour = int(date[8:10])
                minute = int(date[10:12])
                second = int(date[12:14])
                lastjob.JobDate = "%04i-%02i-%02i %02i:%02i:%02i" % (year, month, day, hour, minute, second)
                lastjob.Exists = 1
        return lastjob
        
    def getGroupMembersFromBackend(self, group) :        
        """Returns the group's members list."""
        groupmembers = []
        result = self.doSearch("(&(objectClass=pykotaGroup)(|(pykotaGroupName=%s)(%s=%s)))" % (group.Name, self.info["grouprdn"], group.Name), [self.info["groupmembers"]], base=self.info["groupbase"])
        if result :
            for username in result[0][1].get(self.info["groupmembers"], []) :
                groupmembers.append(self.getUser(username))
        return groupmembers        
        
    def getUserGroupsFromBackend(self, user) :        
        """Returns the user's groups list."""
        groups = []
        result = self.doSearch("(&(objectClass=pykotaGroup)(%s=%s))" % (self.info["groupmembers"], user.Name), [self.info["grouprdn"], "pykotaGroupName", "pykotaLimitBy"], base=self.info["groupbase"])
        if result :
            for (groupid, fields) in result :
                groupname = (fields.get("pykotaGroupName", [None]) or fields.get(self.info["grouprdn"], [None]))[0]
                group = self.getFromCache("GROUPS", groupname)
                if group is None :
                    group = StorageGroup(self, groupname)
                    group.ident = groupid
                    group.LimitBy = fields.get("pykotaLimitBy")
                    if group.LimitBy is not None :
                        group.LimitBy = group.LimitBy[0]
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
        result = self.doSearch("(&(objectClass=pykotaPrinter)(uniqueMember=%s))" % printer.ident, ["pykotaPrinterName"], base=self.info["printerbase"])
        if result :
            for (printerid, fields) in result :
                if printerid != printer.ident : # In case of integrity violation.
                    parentprinter = self.getPrinter(fields.get("pykotaPrinterName")[0])
                    if parentprinter.Exists :
                        pgroups.append(parentprinter)
        return pgroups
        
    def getMatchingPrinters(self, printerpattern) :
        """Returns the list of all printers for which name matches a certain pattern."""
        printers = []
        # see comment at the same place in pgstorage.py
        result = self.doSearch("(&(objectClass=pykotaPrinter)(|%s))" % "".join(["(pykotaPrinterName=%s)(%s=%s)" % (pname, self.info["printerrdn"], pname) for pname in printerpattern.split(",")]), ["pykotaPrinterName", "pykotaPricePerPage", "pykotaPricePerJob", "uniqueMember", "description"], base=self.info["printerbase"])
        if result :
            for (printerid, fields) in result :
                printername = fields.get("pykotaPrinterName", [""])[0] or fields.get(self.info["printerrdn"], [""])[0]
                printer = StoragePrinter(self, printername)
                printer.ident = printerid
                printer.PricePerJob = float(fields.get("pykotaPricePerJob", [0.0])[0] or 0.0)
                printer.PricePerPage = float(fields.get("pykotaPricePerPage", [0.0])[0] or 0.0)
                printer.uniqueMember = fields.get("uniqueMember", [])
                printer.Description = self.databaseToUserCharset(fields.get("description", [""])[0]) 
                printer.Exists = 1
                printers.append(printer)
                self.cacheEntry("PRINTERS", printer.Name, printer)
        return printers        
        
    def getPrinterUsersAndQuotas(self, printer, names=["*"]) :        
        """Returns the list of users who uses a given printer, along with their quotas."""
        usersandquotas = []
        result = self.doSearch("(&(objectClass=pykotaUserPQuota)(pykotaPrinterName=%s)(|%s))" % (printer.Name, "".join(["(pykotaUserName=%s)" % uname for uname in names])), ["pykotaUserName", "pykotaPageCounter", "pykotaLifePageCounter", "pykotaSoftLimit", "pykotaHardLimit", "pykotaDateLimit"], base=self.info["userquotabase"])
        if result :
            for (userquotaid, fields) in result :
                user = self.getUser(fields.get("pykotaUserName")[0])
                userpquota = StorageUserPQuota(self, user, printer)
                userpquota.ident = userquotaid
                userpquota.PageCounter = int(fields.get("pykotaPageCounter", [0])[0] or 0)
                userpquota.LifePageCounter = int(fields.get("pykotaLifePageCounter", [0])[0] or 0)
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
        result = self.doSearch("(&(objectClass=pykotaGroupPQuota)(pykotaPrinterName=%s)(|%s))" % (printer.Name, "".join(["(pykotaGroupName=%s)" % gname for gname in names])), ["pykotaGroupName"], base=self.info["groupquotabase"])
        if result :
            for (groupquotaid, fields) in result :
                group = self.getGroup(fields.get("pykotaGroupName")[0])
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
        newfields = {
                       "pykotaUserName" : user.Name,
                       "pykotaLimitBy" : (user.LimitBy or "quota"),
                    }   
                       
        if user.Email :
            newfields.update({self.info["usermail"]: user.Email})
        mustadd = 1
        if self.info["newuser"].lower() != 'below' :
            try :
                (where, action) = [s.strip() for s in self.info["newuser"].split(",")]
            except ValueError :
                (where, action) = (self.info["newuser"].strip(), "fail")
            result = self.doSearch("(&(objectClass=%s)(%s=%s))" % (where, self.info["userrdn"], user.Name), None, base=self.info["userbase"])
            if result :
                (dn, fields) = result[0]
                fields["objectClass"].extend(["pykotaAccount", "pykotaAccountBalance"])
                fields.update(newfields)
                fields.update({ "pykotaBalance" : str(user.AccountBalance or 0.0),
                                "pykotaLifeTimePaid" : str(user.LifeTimePaid or 0.0), })   
                self.doModify(dn, fields)
                mustadd = 0
            else :
                message = _("Unable to find an existing objectClass %s entry with %s=%s to attach pykotaAccount objectClass") % (where, self.info["userrdn"], user.Name)
                if action.lower() == "warn" :    
                    self.tool.printInfo("%s. A new entry will be created instead." % message, "warn")
                else : # 'fail' or incorrect setting
                    raise PyKotaStorageError, "%s. Action aborted. Please check your configuration." % message
                
        if mustadd :
            if self.info["userbase"] == self.info["balancebase"] :            
                fields = { self.info["userrdn"] : user.Name,
                           "objectClass" : ["pykotaObject", "pykotaAccount", "pykotaAccountBalance"],
                           "cn" : user.Name,
                           "pykotaBalance" : str(user.AccountBalance or 0.0),
                           "pykotaLifeTimePaid" : str(user.LifeTimePaid or 0.0), 
                         } 
            else :             
                fields = { self.info["userrdn"] : user.Name,
                           "objectClass" : ["pykotaObject", "pykotaAccount"],
                           "cn" : user.Name,
                         } 
            fields.update(newfields)         
            dn = "%s=%s,%s" % (self.info["userrdn"], user.Name, self.info["userbase"])
            self.doAdd(dn, fields)
            if self.info["userbase"] != self.info["balancebase"] :            
                fields = { self.info["balancerdn"] : user.Name,
                           "objectClass" : ["pykotaObject", "pykotaAccountBalance"],
                           "cn" : user.Name,
                           "pykotaBalance" : str(user.AccountBalance or 0.0),
                           "pykotaLifeTimePaid" : str(user.LifeTimePaid or 0.0),  
                         } 
                dn = "%s=%s,%s" % (self.info["balancerdn"], user.Name, self.info["balancebase"])
                self.doAdd(dn, fields)
            
        return self.getUser(user.Name)
        
    def addGroup(self, group) :        
        """Adds a group to the quota storage, returns it."""
        newfields = { 
                      "pykotaGroupName" : group.Name,
                      "pykotaLimitBY" : (group.LimitBy or "quota"),
                    } 
        mustadd = 1
        if self.info["newgroup"].lower() != 'below' :
            try :
                (where, action) = [s.strip() for s in self.info["newgroup"].split(",")]
            except ValueError :
                (where, action) = (self.info["newgroup"].strip(), "fail")
            result = self.doSearch("(&(objectClass=%s)(%s=%s))" % (where, self.info["grouprdn"], group.Name), None, base=self.info["groupbase"])
            if result :
                (dn, fields) = result[0]
                fields["objectClass"].extend(["pykotaGroup"])
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
            fields = { self.info["grouprdn"] : group.Name,
                       "objectClass" : ["pykotaObject", "pykotaGroup"],
                       "cn" : group.Name,
                     } 
            fields.update(newfields)         
            dn = "%s=%s,%s" % (self.info["grouprdn"], group.Name, self.info["groupbase"])
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
        
    def writePrinterDescription(self, printer) :    
        """Write the printer's description back into the storage."""
        fields = {
                   "description" : self.userCharsetToDatabase(str(printer.Description)), 
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
            
    def writeNewPayment(self, user, amount) :        
        """Adds a new payment to the payments history."""
        payments = []
        for payment in user.Payments :
            payments.append("%s # %s" % (payment[0], str(payment[1])))
        payments.append("%s # %s" % (str(DateTime.now()), str(amount)))
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
        
    def writeJobNew(self, printer, user, jobid, pagecounter, action, jobsize=None, jobprice=None, filename=None, title=None, copies=None, options=None, clienthost=None, jobsizebytes=None) :
        """Adds a job in a printer's history."""
        if (not self.disablehistory) or (not printer.LastJob.Exists) :
            uuid = self.genUUID()
            dn = "cn=%s,%s" % (uuid, self.info["jobbase"])
        else :    
            uuid = printer.LastJob.ident[3:].split(",")[0]
            dn = printer.LastJob.ident
        fields = {
                   "objectClass" : ["pykotaObject", "pykotaJob"],
                   "cn" : uuid,
                   "pykotaUserName" : user.Name,
                   "pykotaPrinterName" : printer.Name,
                   "pykotaJobId" : jobid,
                   "pykotaPrinterPageCounter" : str(pagecounter),
                   "pykotaAction" : action,
                   "pykotaFileName" : ((filename is None) and "None") or self.userCharsetToDatabase(filename), 
                   "pykotaTitle" : ((title is None) and "None") or self.userCharsetToDatabase(title), 
                   "pykotaCopies" : str(copies), 
                   "pykotaOptions" : ((options is None) and "None") or self.userCharsetToDatabase(options), 
                   "pykotaHostName" : str(clienthost), 
                   "pykotaJobSizeBytes" : str(jobsizebytes),
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
                       "pykotaPrinterName" : printer.Name,
                       "pykotaLastJobIdent" : uuid,
                     }  
            self.doAdd(lastjdn, fields)          
            
    def writeUserPQuotaLimits(self, userpquota, softlimit, hardlimit) :
        """Sets soft and hard limits for a user quota."""
        fields = { 
                   "pykotaSoftLimit" : str(softlimit),
                   "pykotaHardLimit" : str(hardlimit),
                   "pykotaDateLimit" : "None",
                 }
        self.doModify(userpquota.ident, fields)
        
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
            
    def retrieveHistory(self, user=None, printer=None, datelimit=None, hostname=None, limit=100) :    
        """Retrieves all print jobs for user on printer (or all) before date, limited to first 100 results."""
        precond = "(objectClass=pykotaJob)"
        where = []
        if (user is not None) and user.Exists :
            where.append("(pykotaUserName=%s)" % user.Name)
        if (printer is not None) and printer.Exists :
            where.append("(pykotaPrinterName=%s)" % printer.Name)
        if hostname is not None :
            where.append("(pykotaHostName=%s)" % hostname)
        if where :    
            where = "(&%s)" % "".join([precond] + where)
        else :    
            where = precond
        jobs = []    
        result = self.doSearch(where, fields=["pykotaJobSizeBytes", "pykotaHostName", "pykotaUserName", "pykotaPrinterName", "pykotaJobId", "pykotaPrinterPageCounter", "pykotaAction", "pykotaJobSize", "pykotaJobPrice", "pykotaFileName", "pykotaTitle", "pykotaCopies", "pykotaOptions", "createTimestamp"], base=self.info["jobbase"])
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
                date = fields.get("createTimestamp", ["19700101000000"])[0]
                year = int(date[:4])
                month = int(date[4:6])
                day = int(date[6:8])
                hour = int(date[8:10])
                minute = int(date[10:12])
                second = int(date[12:14])
                job.JobDate = "%04i-%02i-%02i %02i:%02i:%02i" % (year, month, day, hour, minute, second)
                if (datelimit is None) or (job.JobDate <= datelimit) :
                    job.UserName = fields.get("pykotaUserName")[0]
                    job.PrinterName = fields.get("pykotaPrinterName")[0]
                    job.Exists = 1
                    jobs.append(job)
            jobs.sort(lambda x, y : cmp(y.JobDate, x.JobDate))        
            if limit :    
                jobs = jobs[:int(limit)]
        return jobs
        
    def deleteUser(self, user) :    
        """Completely deletes an user from the Quota Storage."""
        todelete = []    
        result = self.doSearch("(&(objectClass=pykotaJob)(pykotaUserName=%s))" % user.Name, base=self.info["jobbase"])
        for (ident, fields) in result :
            todelete.append(ident)
            
        result = self.doSearch("(&(objectClass=pykotaUserPQuota)(pykotaUserName=%s))" % user.Name, ["pykotaPrinterName", "pykotaUserName"], base=self.info["userquotabase"])
        for (ident, fields) in result :
            # ensure the user print quota entry will be deleted
            todelete.append(ident)
            
            # if last job of current printer was printed by the user
            # to delete, we also need to delete the printer's last job entry.
            printername = fields["pykotaPrinterName"][0]
            printer = self.getPrinter(printername)
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
            if fields.get("objectClass") or fields.get("objectclass") :
                self.doModify(group.ident, fields, ignoreold=0)        
            else :    
                self.doDelete(group.ident)
                
    def deletePrinter(self, printer) :    
        """Completely deletes an user from the Quota Storage."""
        result = self.doSearch("(&(objectClass=pykotaLastJob)(pykotaPrinterName=%s))" % printer.Name, base=self.info["lastjobbase"])
        for (ident, fields) in result :
            self.doDelete(ident)
        result = self.doSearch("(&(objectClass=pykotaJob)(pykotaPrinterName=%s))" % printer.Name, base=self.info["jobbase"])
        for (ident, fields) in result :
            self.doDelete(ident)
        result = self.doSearch("(&(objectClass=pykotaGroupPQuota)(pykotaPrinterName=%s))" % printer.Name, base=self.info["groupquotabase"])
        for (ident, fields) in result :
            self.doDelete(ident)
        result = self.doSearch("(&(objectClass=pykotaUserPQuota)(pykotaPrinterName=%s))" % printer.Name, base=self.info["userquotabase"])
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
        
    def extractPrinters(self) :
        """Extracts all printer records."""
        entries = [p for p in [self.getPrinter(name) for name in self.getAllPrintersNames()] if p.Exists]
        if entries :
            result = [ ("dn", "pykotaPrinterName", "pykotaPricePerPage", "pykotaPricePerPage", "description") ]
            for entry in entries :
                result.append((entry.ident, entry.Name, entry.PricePerPage, entry.PricePerJob, entry.Description))
            return result 
        
    def extractUsers(self) :
        """Extracts all user records."""
        entries = [u for u in [self.getUser(name) for name in self.getAllUsersNames()] if u.Exists]
        if entries :
            result = [ ("dn", "pykotaUserName", self.info["usermail"], "pykotaBalance", "pykotaLifeTimePaid", "pykotaLimitBy") ]
            for entry in entries :
                result.append((entry.ident, entry.Name, entry.Email, entry.AccountBalance, entry.LifeTimePaid, entry.LimitBy))
            return result 
        
    def extractGroups(self) :
        """Extracts all group records."""
        entries = [g for g in [self.getGroup(name) for name in self.getAllGroupsNames()] if g.Exists]
        if entries :
            result = [ ("dn", "pykotaGroupName", "pykotaBalance", "pykotaLifeTimePaid", "pykotaLimitBy") ]
            for entry in entries :
                result.append((entry.ident, entry.Name, entry.AccountBalance, entry.LifeTimePaid, entry.LimitBy))
            return result 
        
    def extractPayments(self) :
        """Extracts all payment records."""
        entries = [u for u in [self.getUser(name) for name in self.getAllUsersNames()] if u.Exists]
        if entries :
            result = [ ("pykotaUserName", "date", "amount") ]
            for entry in entries :
                for (date, amount) in entry.Payments :
                    result.append((entry.Name, date, amount))
            return result        
        
    def extractUpquotas(self) :
        """Extracts all userpquota records."""
        entries = [p for p in [self.getPrinter(name) for name in self.getAllPrintersNames()] if p.Exists]
        if entries :
            result = [ ("pykotaUserName", "pykotaPrinterName", "dn", "userdn", "printerdn", "pykotaLifePageCounter", "pykotaPageCounter", "pykotaSoftLimit", "pykotaHardLimit", "pykotaDateLimit") ]
            for entry in entries :
                for (user, userpquota) in self.getPrinterUsersAndQuotas(entry) :
                    result.append((user.Name, entry.Name, userpquota.ident, user.ident, entry.ident, userpquota.LifePageCounter, userpquota.PageCounter, userpquota.SoftLimit, userpquota.HardLimit, userpquota.DateLimit))
            return result
        
    def extractGpquotas(self) :
        """Extracts all grouppquota records."""
        entries = [p for p in [self.getPrinter(name) for name in self.getAllPrintersNames()] if p.Exists]
        if entries :
            result = [ ("pykotaGroupName", "pykotaPrinterName", "dn", "groupdn", "printerdn", "pykotaLifePageCounter", "pykotaPageCounter", "pykotaSoftLimit", "pykotaHardLimit", "pykotaDateLimit") ]
            for entry in entries :
                for (group, grouppquota) in self.getPrinterGroupsAndQuotas(entry) :
                    result.append((group.Name, entry.Name, grouppquota.ident, group.ident, entry.ident, grouppquota.LifePageCounter, grouppquota.PageCounter, grouppquota.SoftLimit, grouppquota.HardLimit, grouppquota.DateLimit))
            return result
        
    def extractUmembers(self) :
        """Extracts all user groups members."""
        entries = [g for g in [self.getGroup(name) for name in self.getAllGroupsNames()] if g.Exists]
        if entries :
            result = [ ("pykotaGroupName", "pykotaUserName", "groupdn", "userdn") ]
            for entry in entries :
                for member in entry.Members :
                    result.append((entry.Name, member.Name, entry.ident, member.ident))
            return result        
                
    def extractPmembers(self) :
        """Extracts all printer groups members."""
        entries = [p for p in [self.getPrinter(name) for name in self.getAllPrintersNames()] if p.Exists]
        if entries :
            result = [ ("pykotaPGroupName", "pykotaPrinterName", "pgroupdn", "printerdn") ]
            for entry in entries :
                for parent in self.getParentPrinters(entry) :
                    result.append((parent.Name, entry.Name, parent.ident, entry.ident))
            return result        
        
    def extractHistory(self) :
        """Extracts all jobhistory records."""
        entries = self.retrieveHistory(limit=None)
        if entries :
            result = [ ("pykotaUserName", "pykotaPrinterName", "dn", "pykotaJobId", "pykotaPrinterPageCounter", "pykotaJobSize", "pykotaAction", "createTimeStamp", "pykotaFileName", "pykotaTitle", "pykotaCopies", "pykotaOptions", "pykotaJobPrice", "pykotaHostName", "pykotaJobSizeBytes") ] 
            for entry in entries :
                result.append((entry.UserName, entry.PrinterName, entry.ident, entry.JobId, entry.PrinterPageCounter, entry.JobSize, entry.JobAction, entry.JobDate, entry.JobFileName, entry.JobTitle, entry.JobCopies, entry.JobOptions, entry.JobPrice, entry.JobHostName, entry.JobSizeBytes)) 
            return result    
