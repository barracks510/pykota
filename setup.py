#! /usr/bin/env python
# -*- coding: ISO-8859-15 -*-
#
# PyKota
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
# Revision 1.61  2005/01/08 19:13:11  jalet
# dumpykota.cgi was added to allow the use of dumpykota through the web.
# This makes real time interfacing with the third party software phpPrintAnalyzer
# a breeze !
#
# Revision 1.60  2004/11/21 21:50:02  jalet
# Introduced the new pkmail command as a simple email gateway
#
# Revision 1.59  2004/11/15 19:59:34  jalet
# PyKota banners now basically work !
#
# Revision 1.58  2004/11/12 23:46:43  jalet
# Heavy work on pkbanner. Not finished yet though, but mostly works.
#
# Revision 1.57  2004/11/10 22:40:45  jalet
# Logos are installed now
#
# Revision 1.56  2004/11/10 22:17:12  jalet
# Installation script is now non-interactive again, and doesn't install
# the sample configuration files into /etc/pykota anymore.
# Dependencies check is now done by running checkdeps.py
# The database creation scripts will now be included in RPM packages.
#
# Revision 1.55  2004/10/16 10:20:32  jalet
# Now installs translated manual pages
#
# Revision 1.54  2004/10/13 07:45:01  jalet
# Modified installation script to please both me and the Debian packagers
#
# Revision 1.53  2004/10/04 21:25:29  jalet
# dumpykota can now output datas in the XML format
#
# Revision 1.52  2004/09/30 09:52:45  jalet
# Initial release of autopykota. Reading help or manpage is greatly
# encouraged !
#
# Revision 1.51  2004/09/21 21:31:35  jalet
# Installation script now checks for availability of Python-SNMP (http://pysnmp.sf.net)
#
# Revision 1.50  2004/09/14 22:29:12  jalet
# First version of dumpykota. Works fine but only with PostgreSQL backend
# for now.
#
# Revision 1.49  2004/07/28 13:00:02  jalet
# Now takes care of .sxi and .sxc files if any
#
# Revision 1.48  2004/07/27 07:14:24  jalet
# Now warns the user if pyosd is not present
#
# Revision 1.47  2004/07/16 12:22:45  jalet
# LPRng support early version
#
# Revision 1.46  2004/07/07 13:21:26  jalet
# Introduction of the pykosd command
#
# Revision 1.45  2004/07/06 09:37:01  jalet
# Integrated most of the Debian packaging work made by Sergio González González
#
# Revision 1.44  2004/06/05 22:03:49  jalet
# Payments history is now stored in database
#
# Revision 1.43  2004/05/25 09:49:41  jalet
# The old pykota filter has been removed. LPRng support disabled for now.
#
# Revision 1.42  2004/05/18 14:48:46  jalet
# Big code changes to completely remove the need for "requester" directives,
# jsut use "hardware(... your previous requester directive's content ...)"
#
# Revision 1.41  2004/05/13 14:17:32  jalet
# Warning about changed accounter and requester directives
#
# Revision 1.40  2004/05/13 13:59:27  jalet
# Code simplifications
#
# Revision 1.39  2004/04/08 17:07:41  jalet
# pkpgcounter added
#
# Revision 1.38  2004/03/18 09:18:09  jalet
# Installation now checks for old scripts
#
# Revision 1.37  2004/03/03 19:35:36  jalet
# Spelling problem. Thanks to Jurandy Martins
#
# Revision 1.36  2004/02/25 15:10:38  jalet
# Preliminary snmpprinterstatus command added.
#
# Revision 1.35  2004/02/12 22:43:58  jalet
# Better integration in Debian and more LSB compliance, thanks to
# Peter Hawkins.
#
# Revision 1.34  2004/02/07 13:45:51  jalet
# Preliminary work on the pkhint command
#
# Revision 1.33  2004/02/04 11:16:59  jalet
# pkprinters command line tool added.
#
# Revision 1.32  2004/01/18 20:52:50  jalet
# Portuguese portuguese translation replaces brasilian portuguese one, which
# moves in its own directory.
# Installation script modified to reorganise installed documentation and include
# the documentation on OpenOffice.org + ODBC
#
# Revision 1.31  2004/01/15 12:50:41  jalet
# Installation scripts now tells where the documentation was installed.
#
# Revision 1.30  2004/01/12 15:45:03  jalet
# Now installs documentation in /usr/share/doc/pykota too.
#
# Revision 1.29  2004/01/08 14:10:32  jalet
# Copyright year changed.
#
# Revision 1.28  2003/12/27 16:49:25  uid67467
# Should be ok now.
#
# Revision 1.28  2003/12/06 09:03:43  jalet
# Added Perl script to retrieve printer's internal page counter via PJL,
# contributed by René Lund Jensen.
#
# Revision 1.27  2003/11/28 08:31:28  jalet
# Shell script to wait for AppleTalk enabled printers being idle was added.
#
# Revision 1.26  2003/11/08 16:05:31  jalet
# CUPS backend added for people to experiment.
#
# Revision 1.25  2003/10/08 07:01:19  jalet
# Job history can be disabled.
# Some typos in README.
# More messages in setup script.
#
# Revision 1.24  2003/10/07 09:07:27  jalet
# Character encoding added to please latest version of Python
#
# Revision 1.23  2003/07/29 20:55:17  jalet
# 1.14 is out !
#
# Revision 1.22  2003/07/29 09:54:03  jalet
# Added configurable LDAP mail attribute support
#
# Revision 1.21  2003/07/28 09:11:12  jalet
# PyKota now tries to add its attributes intelligently in existing LDAP
# directories.
#
# Revision 1.20  2003/07/23 16:51:32  jalet
# waitprinter.sh is now included to prevent PyKota from asking the
# printer's internal page counter while a job is still being printer.
#
# Revision 1.19  2003/07/16 21:53:07  jalet
# Really big modifications wrt new configuration file's location and content.
#
# Revision 1.18  2003/07/03 09:44:00  jalet
# Now includes the pykotme utility
#
# Revision 1.17  2003/06/30 12:46:15  jalet
# Extracted reporting code.
#
# Revision 1.16  2003/06/06 20:49:15  jalet
# Very latest schema. UNTESTED.
#
# Revision 1.15  2003/05/17 16:32:30  jalet
# Also outputs the original import error message.
#
# Revision 1.14  2003/05/17 16:31:38  jalet
# Dies gracefully if DistUtils is not present.
#
# Revision 1.13  2003/04/29 18:37:54  jalet
# Pluggable accounting methods (actually doesn't support external scripts)
#
# Revision 1.12  2003/04/23 22:13:56  jalet
# Preliminary support for LPRng added BUT STILL UNTESTED.
#
# Revision 1.11  2003/04/17 13:49:29  jalet
# Typo
#
# Revision 1.10  2003/04/17 13:48:39  jalet
# Better help
#
# Revision 1.9  2003/04/17 13:47:28  jalet
# Help added during installation.
#
# Revision 1.8  2003/04/15 17:49:29  jalet
# Installation script now checks the presence of Netatalk
#
# Revision 1.7  2003/04/03 20:03:37  jalet
# Installation script now allows to install the sample configuration file.
#
# Revision 1.6  2003/03/29 13:45:26  jalet
# GPL paragraphs were incorrectly (from memory) copied into the sources.
# Two README files were added.
# Upgrade script for PostgreSQL pre 1.01 schema was added.
#
# Revision 1.5  2003/03/29 13:08:28  jalet
# Configuration is now expected to be found in /etc/pykota.conf instead of
# in /etc/cups/pykota.conf
# Installation script can move old config files to the new location if needed.
# Better error handling if configuration file is absent.
#
# Revision 1.4  2003/03/29 09:47:00  jalet
# More powerful installation script.
#
# Revision 1.3  2003/03/26 17:48:36  jalet
# First shot at trying to detect the availability of the needed software
# during the installation.
#
# Revision 1.2  2003/03/09 16:49:04  jalet
# The installation script installs the man pages too now.
#
# Revision 1.1  2003/02/05 21:28:17  jalet
# Initial import into CVS
#
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

data_files.append((os.path.join(docdir, "postgresql"), ["initscripts/postgresql/README.postgresql"]))
data_files.append((os.path.join(docdir, "ldap"), ["initscripts/ldap/README.ldap"]))

directory = os.sep.join(["share", "man", "man1"])
manpages = glob.glob(os.sep.join(["man", "*.1"]))    
data_files.append((directory, manpages))

modirs = [ os.path.split(os.path.split(mof)[0])[1] for mof in mofiles ]
for dir in modirs :
    directory = os.sep.join(["share", "man", dir, "man1"])
    manpages = glob.glob(os.sep.join(["man", dir, "*.1"]))    
    data_files.append((directory, manpages))

directory = os.sep.join(["share", "pykota"])
data_files.append((directory, ["checkdeps.py", "bin/cupspykota", "bin/lprngpykota", "bin/waitprinter.sh", "bin/papwaitprinter.sh", "bin/mailandpopup.sh", "contributed/pagecount.pl", "untested/pjl/pagecount.pjl", "untested/pjl/status.pjl", "untested/netatalk/netatalk.sh", "untested/netatalk/pagecount.ps"]))

data_files.append((os.sep.join([directory, "conf"]), ["conf/README", "conf/pykota.conf.sample", "conf/pykotadmin.conf.sample"]))

data_files.append((os.sep.join([directory, "cgi-bin"]), ["cgi-bin/README", "cgi-bin/printquota.cgi", "cgi-bin/dumpykota.cgi"]))

data_files.append((os.sep.join([directory, "logos"]), glob.glob(os.sep.join(["logos", "*.jpeg"])) + glob.glob(os.sep.join(["logos", "*.png"])) + glob.glob(os.sep.join(["logos", "*.xcf"]))))

pgdirectory = os.sep.join([directory, "postgresql"])
data_files.append((pgdirectory, ["initscripts/postgresql/README.postgresql", "initscripts/postgresql/pykota-postgresql.sql"]))

ldapdirectory = os.sep.join([directory, "ldap"])
data_files.append((ldapdirectory, ["initscripts/ldap/README.ldap", "initscripts/ldap/pykota.schema", "initscripts/ldap/pykota-sample.ldif"]))

setup(name = "pykota", version = __version__,
      license = "GNU GPL",
      description = __doc__,
      author = "Jerome Alet",
      author_email = "alet@librelogiciel.com",
      url = "http://www.librelogiciel.com/software/",
      packages = [ "pykota", "pykota.storages", "pykota.loggers", "pykota.accounters", "pykota.reporters" ],
      scripts = [ "bin/pkmail", "bin/pkbanner", "bin/autopykota", "bin/dumpykota", "bin/pkpgcounter", "bin/snmpprinterstatus", "bin/pykosd", "bin/edpykota", "bin/repykota", "bin/warnpykota", "bin/pykotme", "bin/pkprinters", "bin/pkhint" ],
      data_files = data_files)
