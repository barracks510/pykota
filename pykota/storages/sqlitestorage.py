# -*- coding: utf-8 -*-
#
# PyKota : Print Quotas for CUPS
#
# (c) 2003-2013 Jerome Alet <alet@librelogiciel.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# $Id$
#
#

"""This module defines a class to access to a SQLite database backend."""

from pykota.errors import PyKotaStorageError
from pykota.storage import BaseStorage
from pykota.storages.sql import SQLStorage

try :
    from pysqlite2 import dbapi2 as sqlite
except ImportError :
    import sys
    # TODO : to translate or not to translate ?
    raise PyKotaStorageError, "This python version (%s) doesn't seem to have the PySQLite module installed correctly." % sys.version.split()[0]

class Storage(BaseStorage, SQLStorage) :
    def __init__(self, pykotatool, host, dbname, user, passwd) :
        """Opens the SQLite database connection."""
        BaseStorage.__init__(self, pykotatool)
        self.doModify = self.doQuery
        self.tool.logdebug("Trying to open database (dbname=%s)..." % repr(dbname))
        self.database = sqlite.connect(dbname, isolation_level=None)
        self.cursor = self.database.cursor()
        self.closed = False
        try :
            self.doQuery("PRAGMA foreign_keys = True;")
        except PyKotaStorageError :
            pass
        self.tool.logdebug("Database opened (dbname=%s)" % repr(dbname))

    def close(self) :
        """Closes the database connection."""
        if not self.closed :
            self.cursor.close()
            self.database.close()
            self.closed = True
            self.tool.logdebug("Database closed.")

    def beginTransaction(self) :
        """Starts a transaction."""
        self.cursor.execute("BEGIN;")
        self.tool.logdebug("Transaction begins...")

    def commitTransaction(self) :
        """Commits a transaction."""
        self.cursor.execute("COMMIT;")
        self.tool.logdebug("Transaction committed.")

    def rollbackTransaction(self) :
        """Rollbacks a transaction."""
        self.cursor.execute("ROLLBACK;")
        self.tool.logdebug("Transaction aborted.")

    def doQuery(self, query) :
        """Executes an SQL query."""
        query = query.strip()
        if not query.endswith(';') :
            query += ';'
        self.querydebug("QUERY : %s" % query)
        try :
            self.cursor.execute(query)
        except self.database.Error, msg :
            self.tool.logdebug("Query failed : %s" % repr(msg))
            raise PyKotaStorageError, repr(msg)

    def doRawSearch(self, query) :
        """Executes a raw search query."""
        self.doQuery(query)
        result = self.cursor.fetchall()
        return result

    def doSearch(self, query) :
        """Does a search query."""
        result = self.doRawSearch(query)
        if result :
            rows = []
            fields = {}
            for i in range(len(self.cursor.description)) :
                fields[i] = self.cursor.description[i][0]
            for row in result :
                rowdict = {}
                for field in fields.keys() :
                    value = row[field]
                    try :
                        value = value.encode("UTF-8")
                    except :
                        pass
                    rowdict[fields[field]] = value
                rows.append(rowdict)
            return rows

    def doQuote(self, field) :
        """Quotes a field for use as a string in SQL queries."""
        if type(field) == type(0.0) :
            return field
        elif type(field) == type(0) :
            return field
        elif type(field) == type(0L) :
            return field
        elif field is not None :
            return ("'%s'" % field.replace("'", "''"))
        else :
            return "NULL"

    def prepareRawResult(self, result) :
        """Prepares a raw result by including the headers."""
        if result :
            entries = [tuple([f[0] for f in self.cursor.description])]
            entries.extend(result)
            return entries

