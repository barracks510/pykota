#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# PyKota
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

import sys
import os

def checkModule(module) :
    """Checks if a Python module is available or not."""
    try :
        exec "import %s" % module
    except ImportError :
        return 0
    else :
        return 1

def checkCommand(command) :
    """Checks if a command is available or not."""
    input = os.popen("type %s 2>/dev/null" % command)
    result = input.read().strip()
    input.close()
    return result

def checkWithPrompt(prompt, module=None, command=None, helper=None) :
    """Tells the user what will be checked, and asks him what to do if something is absent."""
    sys.stdout.write("Checking for %s availability : " % prompt)
    sys.stdout.flush()
    if command is not None :
        result = checkCommand(command)
    elif module is not None :
        result = checkModule(module)
    if result :
        sys.stdout.write("OK\n")
    else :
        sys.stdout.write("NO.\n")
        sys.stderr.write("ERROR : %s not available !\n" % prompt)
        sys.stdout.write("%s\n" % helper)

if __name__ == "__main__" :
    sys.stdout.write("Checking PyKota dependencies...\n")

    # checks if Python version is correct, we need >= 2.4
    if not (sys.version > "2.4") :
        sys.stderr.write("PyKota needs at least Python v2.4 !\nYour version seems to be older than that, please update.\nAborted !\n")
        sys.exit(-1)

    # checks if some needed Python modules are there or not.
    modulestocheck = [ ("Python-PygreSQL", "pg", "PygreSQL is mandatory if you want to use PostgreSQL as the quota database backend.\nSee http://www.pygresql.org or use 'apt-get install python-pygresql'"),
                       ("Python-SQLite", "pysqlite2", "Python-SQLite is mandatory if you want to use SQLite as the quota database backend.\nSee http://www.pysqlite.org or use 'apt-get install python-pysqlite2'"),
                       ("MySQL-Python", "MySQLdb", "MySQL-Python is mandatory if you want to use MySQL as the quota database backend.\nSee http://sourceforge.net/projects/mysql-python or use 'apt-get install python-mysqldb'"),
                       ("Python-egenix-mxDateTime", "mx.DateTime", "eGenix' mxDateTime is mandatory for PyKota to work.\nSee http://www.egenix.com or use 'apt-get install python-egenix-mxdatetime'"),
                       ("Python-LDAP", "ldap", "Python-LDAP is mandatory if you plan to use an LDAP\ndirectory as the quota database backend.\nSee http://python-ldap.sf.net or use 'apt-get install python-ldap'"),
                       ("Python-OSD", "pyosd", "Python-OSD is recommended if you plan to use the X Window On Screen Display\nprint quota reminder named pykosd. See http://repose.cx/pyosd/ or use 'apt-get install python-osd'"),
                       ("Python-SNMP", "pysnmp", "Python-SNMP is recommended if you plan to use hardware\naccounting with printers which support SNMP.\nSee http://pysnmp.sf.net or use 'apt-get install python-pysnmp4'"),
                       ("Python-JAXML", "jaxml", "Python-JAXML is recommended if you plan to dump datas in the XML format.\nSee http://www.librelogiciel.com/software/ or use 'apt-get install python-jaxml'"),
                       ("Python-ReportLab", "reportlab.pdfgen.canvas", "Python-ReportLab is required if you plan to have PyKota generate banners, invoices or receipts.\nSee http://www.reportlab.org/ or use 'apt-get install python-reportlab'"),
                       ("Python-Imaging", "PIL.Image", "Python-Imaging is required if you plan to have PyKota generate banners, invoices or receipts.\nSee http://www.pythonware.com/downloads/ or use 'apt-get install python-imaging'"),
                       ("Python-pkpgcounter", "pkpgpdls", "Python-pkpgcounter is mandatory.\nGrab it from http://www.pykota.com/software/pkpgcounter/ or use 'apt-get install pkpgcounter'"),
                       ("Python-PAM", "PAM", "Python-PAM is recommended if you plan to use pknotify+PyKotIcon.\nGrab it from http://www.pangalactic.org/PyPAM/ or use 'apt-get install python-pam'"),
                       ("Python-pkipplib", "pkipplib", "Python-pkipplib is now mandatory.\nGrab it from http://www.pykota.com/software/pkipplib/"),
                     ]
    commandstocheck = [ ("GhostScript", "gs", "GhostScript may be needed in different parts of PyKota. Install it from your favorite distribution, or use 'apt-get install ghostscript'."),
                        ("Netatalk", "pap", "Netatalk is needed if you want to use hardware accounting with AppleTalk enabled printers. Install it from your favorite distribution or use 'apt-get install netatalk'")
                      ]
    for (name, module, helper) in modulestocheck :
        checkWithPrompt(name, module=module, helper=helper)

    # checks if some software are there or not.
    for (name, command, helper) in commandstocheck :
        checkWithPrompt(name, command=command, helper=helper)

