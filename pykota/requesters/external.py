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
# Revision 1.8  2003/07/07 11:49:24  jalet
# Lots of small fixes with the help of PyChecker
#
# Revision 1.7  2003/04/23 22:13:57  jalet
# Preliminary support for LPRng added BUT STILL UNTESTED.
#
# Revision 1.6  2003/03/29 13:45:27  jalet
# GPL paragraphs were incorrectly (from memory) copied into the sources.
# Two README files were added.
# Upgrade script for PostgreSQL pre 1.01 schema was added.
#
# Revision 1.5  2003/02/10 11:47:39  jalet
# Moved some code down into the requesters
#
# Revision 1.4  2003/02/10 10:36:33  jalet
# Small problem wrt external requester
#
# Revision 1.3  2003/02/10 00:42:17  jalet
# External requester should be ok (untested)
# New syntax for configuration file wrt requesters
#
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
    def __init__(self, printername, arguments) :
        """Sets instance vars depending on the current printer."""
        self.printername = printername
        self.commandline = arguments.strip()
        
    def getPrinterPageCounter(self, printer) :
        """Returns the page counter from the printer via an external command.
        
           The external command must report the life time page number of the printer on stdout.
        """
        commandline = self.commandline % locals()
        if printer is None :
            raise PyKotaRequesterError, _("Unknown printer address in EXTERNAL(%s) for printer %s") % (commandline, self.printername)
        answer = os.popen(commandline)
        try :
            pagecounter = int(answer.readline().strip())
        except ValueError :    
            raise PyKotaRequesterError, _("Unable to query printer %s via EXTERNAL(%s)") % (printer, commandline) 
        answer.close()
        return pagecounter
        
