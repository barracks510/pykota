#! /usr/bin/env python

# PyKota - Print Quotas for CUPS
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
# Revision 1.2  2003/02/09 13:05:43  jalet
# Internationalization continues...
#
# Revision 1.1  2003/02/07 13:15:01  jalet
# External requester skeleton added.
#
#
#

import os
from pykota.requester import PyKotaRequesterError

class Requester :
    """A class to send queries to printers via external commands."""
    def __init__(self, config, printername) :
        """Sets instance vars depending on the current printer."""
        self.printername = printername
        raise PyKotaRequesterError, _("Requester not implemented yet.")
        
    def getPrinterPageCounter(self, hostname) :
        """Returns the page counter from the hostname printer via SNMP.
        
           Currently uses the snmpget external command. TODO : do it internally 
        """
        raise PyKotaRequesterError, _("Requester not implemented yet.")
        
