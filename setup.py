#! /usr/bin/env python
#
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
from distutils.core import setup

sys.path.insert(0, "pykota")
from pykota.version import __version__, __doc__

if "install" in sys.argv :
    sys.stderr.write("PygreSQL availability : ")
    try :
        import pg
    except ImportError :    
        sys.stderr.write("No ! Installation aborted.\n")
        sys.exit(-1)
    else :    
        del pg
        sys.stderr.write("OK.\n")
        sys.stderr.write("snmpget availability : ")
        result = os.popen("type snmpget")
        snmpget = result.read().strip()
        result.close()
        if not snmpget :
            sys.stderr.write("No ! Installation aborted.\n")
            sys.exit(-1)
        else :    
            sys.stderr.write("OK.\n")
            
data_files = []
mofiles = glob.glob(os.sep.join(["po", "*", "*.mo"]))
for mofile in mofiles :
    lang = mofile.split(os.sep)[1]
    directory = os.sep.join(["share", "locale", lang, "LC_MESSAGES"])
    data_files.append((directory, [ mofile ]))
    
directory = os.sep.join(["share", "man", "man1"])
manpages = glob.glob(os.sep.join(["man", "*.1"]))    
data_files.append((directory, manpages))

setup(name = "pykota", version = __version__,
      license = "GNU GPL",
      description = __doc__,
      author = "Jerome Alet",
      author_email = "alet@librelogiciel.com",
      url = "http://www.librelogiciel.com/software/",
      packages = [ "pykota", "pykota.storages", "pykota.requesters", "pykota.loggers" ],
      scripts = [ "bin/pykota", "bin/edpykota", "bin/repykota", "bin/warnpykota" ],
      data_files = data_files)

