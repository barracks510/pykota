# PyKota
#
# PyKota : Print Quotas for CUPS
#
# (c) 2003 Jerome Alet <alet@librelogiciel.com>
# You're welcome to redistribute this software under the
# terms of the GNU General Public Licence version 2.0
# or, at your option, any higher version.
#
# You can read the complete GNU GPL in the file COPYING
# which should come along with this software, or visit
# the Free Software Foundation's WEB site http://www.fsf.org
#
# $Id$
#
# $Log$
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

import pg

from pykota.storage import PyKotaStorageError
from pykota.storages import sql

class Storage(sql.SQLStorage) :
    def __init__(self, host, dbname, user) :
        """Opens the PostgreSQL database connection."""
        self.closed = 1
        try :
            self.database = pg.connect(host=host, dbname=dbname, user=user)
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
        try :
            return self.database.query(query)
        except pg.error, msg :    
            raise PyKotaStorageError, msg
        
    def doQuote(self, field) :
        """Quotes a field for use as a string in SQL queries."""
        if type(field) == type(0) : # TODO : do something safer
            typ = "decimal"
        else :    
            typ = "text"
        return pg._quote(field, typ)
        
    def doParseResult(self, result) :
        """Returns the result as a list of Python mappings."""
        if (result is not None) and (result.ntuples() > 0) :
            return result.dictresult()
        
