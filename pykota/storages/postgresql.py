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
# Revision 1.10  2003/04/30 13:36:40  jalet
# Stupid accounting method was added.
#
# Revision 1.9  2003/04/27 08:04:15  jalet
# LDAP storage backend's skeleton added. DOESN'T WORK.
#
# Revision 1.8  2003/04/23 22:13:57  jalet
# Preliminary support for LPRng added BUT STILL UNTESTED.
#
# Revision 1.7  2003/04/15 11:30:57  jalet
# More work done on money print charging.
# Minor bugs corrected.
# All tools now access to the storage as priviledged users, repykota excepted.
#
# Revision 1.6  2003/03/29 13:45:27  jalet
# GPL paragraphs were incorrectly (from memory) copied into the sources.
# Two README files were added.
# Upgrade script for PostgreSQL pre 1.01 schema was added.
#
# Revision 1.5  2003/03/22 13:11:33  jalet
# The port on which the Quota Storage Sever is listening can now
# be set in the configuration file (see sample).
# Better error handling if PygreSQL is not installed.
# Improved documentation.
# Version number changed to 1.02alpha
#
# Revision 1.4  2003/02/17 22:05:50  jalet
# Storage backend now supports admin and user passwords (untested)
#
# Revision 1.3  2003/02/06 14:49:04  jalet
# edpykota should be ok now
#
# Revision 1.2  2003/02/05 22:28:38  jalet
# More robust storage
#
# Revision 1.1  2003/02/05 21:28:17  jalet
# Initial import into CVS
#
#
#


from pykota.storage import PyKotaStorageError
from pykota.storages import sql

try :
    import pg
except ImportError :    
    import sys
    # TODO : to translate or not to translate ?
    raise PyKotaStorageError, "This python version (%s) doesn't seem to have the PygreSQL module installed correctly." % sys.version.split()[0]

class Storage(sql.SQLStorage) :
    def __init__(self, host, dbname, user, passwd) :
        """Opens the PostgreSQL database connection."""
        self.closed = 1
        try :
            (host, port) = host.split(":")
            port = int(port)
        except ValueError :    
            port = -1         # Use PostgreSQL's default tcp/ip port (5432).
        
        try :
            self.database = pg.connect(host=host, port=port, dbname=dbname, user=user, passwd=passwd)
            self.closed = 0
        except pg.error, msg :
            raise PyKotaStorageError, msg
            
    def __del__(self) :        
        """Closes the database connection."""
        if not self.closed :
            self.database.close()
            self.closed = 1
        
    def doQuery(self, query) :
        """Does a query."""
        if type(query) in (type([]), type(())) :
            query = ";".join(query)
        query = query.strip()    
        if not query.endswith(';') :    
            query += ';'
        self.database.query("BEGIN;")
        try :
            result = self.database.query(query)
        except pg.error, msg :    
            self.database.query("ROLLBACK;")
            raise PyKotaStorageError, msg
        else :    
            self.database.query("COMMIT;")
            return result
        
    def doQuote(self, field) :
        """Quotes a field for use as a string in SQL queries."""
        if type(field) in (type(0), type(0.0)) : # TODO : do something safer
            typ = "decimal"
        else :    
            typ = "text"
        return pg._quote(field, typ)
        
    def doParseResult(self, result) :
        """Returns the result as a list of Python mappings."""
        if (result is not None) and (result.ntuples() > 0) :
            return result.dictresult()
        
