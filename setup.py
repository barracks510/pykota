#! /usr/bin/env python
#
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
from distutils.core import setup

sys.path.insert(0, "pykota")
from pykota.version import __version__, __doc__

ACTION_CONTINUE = 0
ACTION_ABORT = 1

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
    
def checkWithPrompt(prompt, module=None, command=None, help=None) :
    """Tells the user what will be checked, and asks him what to do if something is absent."""
    sys.stdout.write("Checking for %s availability : " % prompt)
    sys.stdout.flush()
    if command is not None :
        result = checkCommand(command)
    elif module is not None :    
        result = checkModule(module)
    if result :    
        sys.stdout.write("OK\n")
        return ACTION_CONTINUE
    else :    
        sys.stdout.write("NO.\n")
        sys.stderr.write("ERROR : %s not available !\n" % prompt)
        if help is not None :
            sys.stdout.write("%s\n" % help)
            sys.stdout.write("You may continue safely if you don't need this functionnality.\n")
        answer = raw_input("%s is missing. Do you want to continue anyway (y/N) ? " % prompt)
        if answer[0:1].upper() == 'Y' :
            return ACTION_CONTINUE
        else :
            return ACTION_ABORT
    
if "install" in sys.argv :
    # checks if Python version is correct, we need >= 2.1
    if not (sys.version > "2.1") :
        sys.stderr.write("PyKota needs at least Python v2.1 !\nYour version seems to be older than that, please update.\nAborted !\n")
        sys.exit(-1)
        
    # checks if a configuration file is present in the old location
    if os.path.isfile("/etc/cups/pykota.conf") :
        if not os.path.isfile("/etc/pykota.conf") :
            sys.stdout.write("From version 1.02 on, PyKota expects to find its configuration\nfile in /etc instead of /etc/cups.\n")
            sys.stdout.write("It seems that you've got a configuration file in the old location,\nso it will not be used anymore,\nand there's no configuration file in the new location.\n")
            answer = raw_input("Do you want to move /etc/cups/pykota.conf to /etc/pykota.conf (y/N) ? ")
            if answer[0:1].upper() == 'Y' :
                try :
                    os.rename("/etc/cups/pykota.conf", "/etc/pykota.conf")
                except OSError :    
                    sys.stderr.write("ERROR : An error occured while moving /etc/cups/pykota.conf to /etc/pykota.conf\nAborted !\n")
                    sys.exit(-1)
            else :
                sys.stderr.write("WARNING : Configuration file /etc/cups/pykota.conf won't be used ! Move it to /etc instead.\n")
                sys.stderr.write("PyKota installation will continue anyway, but the software won't run until you put a proper configuration file in /etc\n")
        else :        
            sys.stderr.write("WARNING : Configuration file /etc/cups/pykota.conf will not be used !\nThe file /etc/pykota.conf will be used instead.\n")
    elif not os.path.isfile("/etc/pykota.conf") :        
        # no configuration file, first installation it seems.
        if os.path.isfile("conf/pykota.conf.sample") :
            answer = raw_input("Do you want to install conf/pykota.conf.sample as /etc/pykota.conf (y/N) ? ")
            if answer[0:1].upper() == 'Y' :
                try :
                    shutil.copy("conf/pykota.conf.sample", "/etc/pykota.conf")        
                except IOError :    
                    sys.stderr.write("WARNING : Problem while installing /etc/pykota.conf, please do it manually.\n")
                else :    
                    sys.stdout.write("Configuration file /etc/pykota.conf installed.\nDon't forget to adapt /etc/pykota.conf to your needs.\n")
            else :        
                sys.stderr.write("WARNING : PyKota won't run without a configuration file !\n")
    
    # checks if some needed Python modules are there or not.
    modulestocheck = [("PygreSQL", "pg"), ("mxDateTime", "mx.DateTime")]
    commandstocheck = [("SNMP Tools", "snmpget", "SNMP Tools are needed if you want to use SNMP enabled printers."), ("Netatalk", "pap", "Netatalk is needed if you want to use AppleTalk enabled printers.")]
    for (name, module) in modulestocheck :
        action = checkWithPrompt(name, module=module)
        if action == ACTION_ABORT :
            sys.stderr.write("Aborted !\n")
            sys.exit(-1)
            
    # checks if some software are there or not.
    for (name, command, help) in commandstocheck :
        action = checkWithPrompt(name, command=command, help=help)
        if action == ACTION_ABORT :
            sys.stderr.write("Aborted !\n")
            sys.exit(-1)
            
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

