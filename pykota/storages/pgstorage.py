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
# Revision 1.35  2004/02/02 22:44:16  jalet
# Preliminary work on Relationnal Database Independance via DB-API 2.0
#
# Revision 1.34  2004/01/12 15:12:50  jalet
# Small fix for history
#
# Revision 1.33  2004/01/12 14:44:47  jalet
# Missing space in SQL query
#
# Revision 1.32  2004/01/12 14:35:02  jalet
# Printing history added to CGI script.
#
# Revision 1.31  2004/01/10 09:44:02  jalet
# Fixed potential accuracy problem if a user printed on several printers at
# the very same time.
#
# Revision 1.30  2004/01/08 16:33:27  jalet
# Additionnal check to not create a circular printers group.
#
# Revision 1.29  2004/01/08 16:24:49  jalet
# edpykota now supports adding printers to printer groups.
#
# Revision 1.28  2004/01/08 14:10:33  jalet
# Copyright year changed.
#
# Revision 1.27  2004/01/06 14:24:59  jalet
# Printer groups should be cached now, if caching is enabled.
#
# Revision 1.26  2003/12/29 14:12:48  uid67467
# Tries to workaround possible integrity violations when retrieving printer groups
#
# Revision 1.25  2003/12/27 16:49:25  uid67467
# Should be ok now.
#
# Revision 1.24  2003/11/29 22:02:14  jalet
# Don't try to retrieve the user print quota information if current printer
# doesn't exist.
#
# Revision 1.23  2003/11/23 19:01:37  jalet
# Job price added to history
#
# Revision 1.22  2003/11/21 14:28:46  jalet
# More complete job history.
#
# Revision 1.21  2003/11/12 13:06:38  jalet
# Bug fix wrt no user/group name command line argument to edpykota
#
# Revision 1.20  2003/10/09 21:25:26  jalet
# Multiple printer names or wildcards can be passed on the command line
# separated with commas.
# Beta phase.
#
# Revision 1.19  2003/10/08 07:01:20  jalet
# Job history can be disabled.
# Some typos in README.
# More messages in setup script.
#
# Revision 1.18  2003/10/07 09:07:30  jalet
# Character encoding added to please latest version of Python
#
# Revision 1.17  2003/10/06 13:12:28  jalet
# More work on caching
#
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

from pykota.storage import PyKotaStorageError,BaseStorage,StorageObject,StorageUser,StorageGroup,StoragePrinter,StorageJob,StorageLastJob,StorageUserPQuota,StorageGroupPQuota
from pykota.storages.sql import SQLStorage

try :
    import pg
except ImportError :    
    import sys
    # TODO : to translate or not to translate ?
    raise PyKotaStorageError, "This python version (%s) doesn't seem to have the PygreSQL module installed correctly." % sys.version.split()[0]

class Storage(BaseStorage, SQLStorage) :
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
