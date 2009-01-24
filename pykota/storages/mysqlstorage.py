# -*- coding: utf-8 -*-
#
# PyKota : Print Quotas for CUPS
#
# (c) 2003-2009 Jerome Alet <alet@librelogiciel.com>
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

"""This module defines a class to access to a MySQL database backend."""

from pykota.errors import PyKotaStorageError
from pykota.storage import BaseStorage
from pykota.storages.sql import SQLStorage

try :
    import MySQLdb
except ImportError :
    import sys
    # TODO : to translate or not to translate ?
    raise PyKotaStorageError, "This python version (%s) doesn't seem to have the MySQL module installed correctly." % sys.version.split()[0]

class Storage(BaseStorage, SQLStorage) :
    def __init__(self, pykotatool, host, dbname, user, passwd) :
        """Opens the MySQL database connection."""
        BaseStorage.__init__(self, pykotatool)
        try :
            (host, port) = host.split(":")
            port = int(port)
        except ValueError :
            port = 3306           # Use the default MySQL port

        self.tool.logdebug("Trying to open database (host=%s, port=%s, dbname=%s, user=%s)..." \
                               % (repr(host),
                                  repr(port),
                                  repr(dbname),
                                  repr(user)))
        try :
            self.database = MySQLdb.connect(host=host,
                                            port=port,
                                            db=dbname,
                                            user=user,
                                            passwd=passwd,
                                            charset="utf8")
        except TypeError :
            self.tool.logdebug("'charset' argument not allowed with this version of python-mysqldb, retrying without...")
            self.database = MySQLdb.connect(host=host,
                                            port=port,
                                            db=dbname,
                                            user=user,
                                            passwd=passwd)

        try :
            self.database.autocommit(1)
        except AttributeError :
            raise PyKotaStorageError, _("Your version of python-mysqldb is too old. Please install a newer release.")
        self.cursor = self.database.cursor()
        self.cursor.execute("SET NAMES 'utf8';")
        self.cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED;") # Same as PostgreSQL and Oracle's default
        self.closed = False
        self.tool.logdebug("Database opened (host=%s, port=%s, dbname=%s, user=%s)" \
                               % (repr(host),
                                  repr(port),
                                  repr(dbname),
                                  repr(user)))
        try :
            # Here we try to select a string (an &eacute;) which is
            # already encoded in UTF-8. If python-mysqldb suffers from
            # the double encoding problem, we will catch the exception
            # and activate a workaround.
            self.cursor.execute("SELECT '%s';" % (chr(0xc3) + chr(0xa9))) # &eacute; in UTF-8
            self.cursor.fetchall()
        except UnicodeDecodeError :
            self.needsworkaround = True
            self.tool.logdebug("Database needs encoding workaround.")
        else :
            self.needsworkaround = False
            self.tool.logdebug("Database doesn't need encoding workaround.")

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
        self.database.commit()
        self.tool.logdebug("Transaction committed.")

    def rollbackTransaction(self) :
        """Rollbacks a transaction."""
        self.database.rollback()
        self.tool.logdebug("Transaction aborted.")

    def doRawSearch(self, query) :
        """Does a raw search query."""
        query = query.strip()
        if not query.endswith(';') :
            query += ';'
        self.querydebug("QUERY : %s" % query)
        if self.needsworkaround :
            query = query.decode("UTF-8")
        try :
            self.cursor.execute(query)
        except self.database.Error, msg :
            raise PyKotaStorageError, repr(msg)
        else :
            # This returns a list of lists. Integers are returned as longs.
            return self.cursor.fetchall()

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
                    rowdict[fields[field]] = row[field]
                rows.append(rowdict)
            # returns a list of dicts
            return rows

    def doModify(self, query) :
        """Does a (possibly multiple) modify query."""
        query = query.strip()
        if not query.endswith(';') :
            query += ';'
        self.querydebug("QUERY : %s" % query)
        if self.needsworkaround :
            query = query.decode("UTF-8")
        try :
            self.cursor.execute(query)
        except self.database.Error, msg :
            self.tool.logdebug("Query failed : %s" % repr(msg))
            raise PyKotaStorageError, repr(msg)

    def doQuote(self, field) :
        """Quotes a field for use as a string in SQL queries."""
        if type(field) == type(0.0) :
            return field
        elif type(field) == type(0) :
            return field
        elif type(field) == type(0L) :
            return field
        elif field is not None :
            return self.database.string_literal(field)
        else :
            return "NULL"

    def prepareRawResult(self, result) :
        """Prepares a raw result by including the headers."""
        if result :
            return [tuple([f[0] for f in self.cursor.description])] \
                 + list(result)
