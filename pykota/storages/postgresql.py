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

try :
    import pg
except ImportError :    
    import sys
    sys.stderr.write("This python version (%s) doesn't seem to have the PygreSQL module installed correctly.\n" % sys.version.split()[0])
    raise

from pykota.storage import PyKotaStorageError
from pykota.storages import sql

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
        
