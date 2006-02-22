#! /usr/bin/env python
# -*- coding: ISO-8859-15 -*-
#
# PyKota
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

import sys
import glob
import os
import shutil
try :
    from distutils.core import setup
except ImportError, msg :    
    sys.stderr.write("%s\n" % msg)
    sys.stderr.write("You need the DistUtils Python module.\nunder Debian, you may have to install the python-dev package.\nOf course, YMMV.\n")
    sys.exit(-1)

sys.path.insert(0, "pykota")
from pykota.version import __version__, __doc__

data_files = []
mofiles = glob.glob(os.sep.join(["po", "*", "*.mo"]))
for mofile in mofiles :
    lang = mofile.split(os.sep)[1]
    directory = os.sep.join(["share", "locale", lang, "LC_MESSAGES"])
    data_files.append((directory, [ mofile ]))
    
docdir = "share/doc/pykota"    
docfiles = ["README", "FAQ", "SECURITY", "COPYING", "LICENSE", "CREDITS", "TODO", "NEWS"]
data_files.append((docdir, docfiles))

docfiles = glob.glob(os.sep.join(["docs", "*.pdf"]))
docfiles += glob.glob(os.sep.join(["docs", "*.sx?"]))
data_files.append((docdir, docfiles))

docfiles = glob.glob(os.sep.join(["docs", "spanish", "*.pdf"]))
docfiles += glob.glob(os.sep.join(["docs", "spanish", "*.sxw"]))
data_files.append((os.path.join(docdir, "spanish"), docfiles))

docfiles = glob.glob(os.sep.join(["docs", "pykota", "*.html"]))
data_files.append((os.path.join(docdir, "html"), docfiles))

docfiles = glob.glob(os.sep.join(["openoffice", "*.sx?"]))
docfiles += glob.glob(os.sep.join(["openoffice", "*.png"]))
docfiles += glob.glob(os.sep.join(["openoffice", "README"]))
data_files.append((os.path.join(docdir, "openoffice"), docfiles))

directory = os.sep.join(["share", "man", "man1"])
manpages = glob.glob(os.sep.join(["man", "*.1"]))    
data_files.append((directory, manpages))

modirs = [ os.path.split(os.path.split(mof)[0])[1] for mof in mofiles ]
for dir in modirs :
    directory = os.sep.join(["share", "man", dir, "man1"])
    manpages = glob.glob(os.sep.join(["man", dir, "*.1"]))    
    data_files.append((directory, manpages))

directory = os.sep.join(["share", "pykota"])
data_files.append((directory, ["checkdeps.py", "bin/cupspykota", \
                               "bin/waitprinter.sh", \
                               "bin/papwaitprinter.sh", \
                               "bin/mailandpopup.sh", \
                               "contributed/pagecount.pl", \
                               "contributed/dump_bfd.php", \
                               "untested/pjl/pagecount.pjl", \
                               "untested/pjl/status.pjl", \
                               "untested/netatalk/netatalk.sh", \
                               "untested/netatalk/pagecount.ps"]))

data_files.append((os.sep.join([directory, "conf"]), ["conf/README", "conf/pykota.conf.sample", "conf/pykotadmin.conf.sample"]))

data_files.append((os.sep.join([directory, "cgi-bin"]), ["cgi-bin/README", "cgi-bin/printquota.cgi", "cgi-bin/dumpykota.cgi", "cgi-bin/pykotme.cgi"]))

data_files.append((os.sep.join([directory, "logos"]), glob.glob(os.sep.join(["logos", "*.jpeg"])) + glob.glob(os.sep.join(["logos", "*.png"])) + glob.glob(os.sep.join(["logos", "*.xcf"]))))

data_files.append((os.sep.join([directory, "stylesheets"]), glob.glob(os.sep.join(["stylesheets", "*.css"])) + [ "stylesheets/README" ]))

pgdirectory = os.sep.join([directory, "postgresql"])
data_files.append((pgdirectory, ["initscripts/postgresql/README.postgresql", "initscripts/postgresql/pykota-postgresql.sql"]))

ldapdirectory = os.sep.join([directory, "ldap"])
data_files.append((ldapdirectory, ["initscripts/ldap/README.ldap", "initscripts/ldap/pykota.schema", "initscripts/ldap/pykota-sample.ldif"]))

mysqldirectory = os.sep.join([directory, "mysql"])
data_files.append((mysqldirectory, ["initscripts/mysql/README.mysql", "initscripts/mysql/pykota-mysql.sql"]))

sqlitedirectory = os.sep.join([directory, "sqlite"])
data_files.append((sqlitedirectory, ["initscripts/sqlite/README.sqlite", "initscripts/sqlite/pykota-sqlite.sql"]))

os.umask(022)
setup(name = "pykota", version = __version__,
      license = "GNU GPL",
      description = __doc__,
      author = "Jerome Alet",
      author_email = "alet@librelogiciel.com",
      url = "http://www.librelogiciel.com/software/",
      packages = [ "pykota", "pykota.storages", "pykota.loggers", "pykota.accounters", "pykota.reporters" ],
      scripts = [ "bin/pkusers", "bin/pkinvoice", "bin/pykoef", \
                  "bin/pkturnkey", "bin/pkbcodes", "bin/pkmail", \
                  "bin/pkbanner", "bin/autopykota", "bin/dumpykota", \
                  "bin/pykosd", "bin/edpykota", "bin/repykota", \
                  "bin/warnpykota", "bin/pykotme", "bin/pkprinters" ],
      data_files = data_files)
