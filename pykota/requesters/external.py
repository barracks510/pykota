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
    def __init__(self, config, printername, arguments) :
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
        
