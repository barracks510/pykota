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
# Revision 1.3  2003/04/30 19:53:58  jalet
# 1.05
#
# Revision 1.2  2003/04/30 13:36:40  jalet
# Stupid accounting method was added.
#
# Revision 1.1  2003/04/29 18:37:54  jalet
# Pluggable accounting methods (actually doesn't support external scripts)
#
#
#

import sys

class PyKotaAccounterError(Exception):
    """An exception for Accounter related stuff."""
    def __init__(self, message = ""):
        self.message = message
        Exception.__init__(self, message)
    def __repr__(self):
        return self.message
    __str__ = __repr__
    
class AccounterBase :    
    """A class to account print usage by querying printers."""
    def __init__(self, kotafilter, arguments) :
        """Sets instance vars depending on the current printer."""
        self.filter = kotafilter
        self.arguments = arguments
        
    def filterInput(self, inputfile) :
        """Transparent filter."""
        mustclose = 0    
        if inputfile is not None :    
            if hasattr(inputfile, "read") :
                infile = inputfile
            else :    
                infile = open(inputfile, "rb")
            mustclose = 1
        else :    
            infile = sys.stdin
        data = infile.read(256*1024)    
        while data :
            sys.stdout.write(data)
            data = infile.read(256*1024)
        if mustclose :    
            infile.close()
            
    def doAccounting(self, printerid, userid) :    
        """Does the real accounting."""
        raise PyKotaAccounterError, "Accounter not implemented !"
        
def openAccounter(kotafilter) :
    """Returns a connection handle to the appropriate accounter."""
    (backend, args) = kotafilter.config.getAccounterBackend(kotafilter.printername)
    try :
        if not backend.isalpha() :
            # don't trust user input
            raise ImportError
        exec "from pykota.accounters import %s as accounterbackend" % backend.lower()    
    except ImportError :
        raise PyKotaAccounterError, _("Unsupported accounter backend %s") % backend
    else :    
        return getattr(accounterbackend, "Accounter")(kotafilter, args)
