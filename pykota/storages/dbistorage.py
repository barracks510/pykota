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
# Revision 1.2  2004/09/24 21:19:48  jalet
# Did a pass of PyChecker
#
# Revision 1.1  2004/02/02 22:44:15  jalet
# Preliminary work on Relationnal Database Independance via DB-API 2.0
#
#
#

########################################################################
##                                                                    ##
## THIS FILE IS HIGHLY EXPERIMENTAL.                                  ##
##                                                                    ##
## IT WILL PROVIDE DATABASE INDEPENDANCE IN THE FUTURE.               ##
##                                                                    ##
## FOR NOW IT ONLY RECOGNIZES THE POSTGRESQL DBI MODULE.              ##
##                                                                    ##
## DON'T USE THIS UNTIL YOU ARE TOLD TO DO SO.                        ##
##                                                                    ##
##                                      THANKS !                      ##
##                                                                    ##
########################################################################

from pykota.storage import PyKotaStorageError,BaseStorage,StorageObject,StorageUser,StorageGroup,StoragePrinter,StorageJob,StorageLastJob,StorageUserPQuota,StorageGroupPQuota
from pykota.storages.sql import SQLStorage

try :
    import _pg
    import pgdb
except ImportError :    
    import sys
    # TODO : to translate or not to translate ?
    raise PyKotaStorageError, "This python version (%s) doesn't seem to have the PygreSQL module installed correctly." % sys.version.split()[0]

class Storage(BaseStorage, SQLStorage) :
    def __init__(self, pykotatool, host, dbname, user, passwd) :
        """Opens the Database Independant connection."""
        BaseStorage.__init__(self, pykotatool)
        try :
            (host, port) = host.split(":")
            port = int(port)
        except ValueError :    
            port = -1         # Use PostgreSQL's default tcp/ip port (5432).
        
        try :
            self.database = pgdb.connect(host=host, database=dbname, user=user, password=passwd)
            self.cursor = self.database.cursor()
        except _pg.error, msg :
            raise PyKotaStorageError, msg
        else :    
            self.closed = 0
            self.tool.logdebug("Database opened (host=%s, port=%s, dbname=%s, user=%s)" % (host, port, dbname, user))
            
    def close(self) :    
        """Closes the database connection."""
        if not self.closed :
            self.cursor.close()
            self.database.close()
            self.closed = 1
            self.tool.logdebug("Database closed.")
        
    def beginTransaction(self) :    
        """Starts a transaction."""
        # No need for this since transactions begin automatically
        # self.database.query("BEGIN;")
        self.tool.logdebug("Transaction begins...")
        
    def commitTransaction(self) :    
        """Commits a transaction."""
        self.database.commit()
        self.tool.logdebug("Transaction committed.")
        
    def rollbackTransaction(self) :     
        """Rollbacks a transaction."""
        self.database.rollback()
        self.tool.logdebug("Transaction aborted.")
        
    def doSearch(self, query) :
        """Does a search query."""
        query = query.strip()    
        if not query.endswith(';') :    
            query += ';'
        try :
            self.tool.logdebug("QUERY : %s" % query)
            self.cursor.execute(query)
            result = self.cursor.fetchall()
        except pgdb.DatabaseError, msg :    
            raise PyKotaStorageError, msg
        else :    
            newresult = []
            fieldsnames = [desc[0] for desc in self.cursor.description]
            for record in result :
                dico = {}
                for fnumber in range(len(record)) :
                    dico.update({fieldsnames[fnumber] : record[fnumber]})
                newresult.append(dico)    
            return newresult
            
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
        return pgdb._quote(field)
