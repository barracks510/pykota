# PyKota
#
# PyKota - Print Quotas for CUPS and LPRng
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
# Revision 1.8  2003/04/23 22:13:57  jalet
# Preliminary support for LPRng added BUT STILL UNTESTED.
#
# Revision 1.7  2003/03/29 13:45:27  jalet
# GPL paragraphs were incorrectly (from memory) copied into the sources.
# Two README files were added.
# Upgrade script for PostgreSQL pre 1.01 schema was added.
#
# Revision 1.6  2003/02/10 11:47:39  jalet
# Moved some code down into the requesters
#
# Revision 1.5  2003/02/10 00:42:17  jalet
# External requester should be ok (untested)
# New syntax for configuration file wrt requesters
#
# Revision 1.4  2003/02/09 13:05:43  jalet
# Internationalization continues...
#
# Revision 1.3  2003/02/07 13:12:41  jalet
# Bad old comment
#
# Revision 1.2  2003/02/05 23:00:12  jalet
# Forgotten import
# Bad datetime conversion
#
# Revision 1.1  2003/02/05 21:28:17  jalet
# Initial import into CVS
#
#
#

import os
from pykota.requester import PyKotaRequesterError

class Requester :
    """A class to send queries to printers via SNMP."""
    def __init__(self, config, printername, arguments) :
        """Sets instance vars depending on the current printer."""
        self.printername = printername
        args = [x.strip() for x in arguments.split(',')]
        self.community = args[0]
        self.oid = args[1]
        
    def getPrinterPageCounter(self, hostname) :
        """Returns the page counter from the hostname printer via SNMP.
        
           Currently uses the snmpget external command. TODO : do it internally 
        """
        if hostname is None :
            raise PyKotaRequesterError, _("Unknown printer address in SNMP(%s, %s) for printer %s") % (self.community, self.oid, self.printername)
        answer = os.popen("snmpget -c %s -Ov %s %s" % (self.community, hostname, self.oid))
        try :
            pagecounter = int(answer.readline().split()[-1].strip())
        except IndexError :    
            raise PyKotaRequesterError, _("Unable to query printer %s via SNMP(%s, %s)") % (hostname, self.community, self.oid) 
        answer.close()
        return pagecounter
    
