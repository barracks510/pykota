# PyKota
#
# PyKota : Print Quotas for CUPS
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
# Revision 1.6  2003/03/29 13:45:27  jalet
# GPL paragraphs were incorrectly (from memory) copied into the sources.
# Two README files were added.
# Upgrade script for PostgreSQL pre 1.01 schema was added.
#
# Revision 1.5  2003/02/10 00:42:17  jalet
# External requester should be ok (untested)
# New syntax for configuration file wrt requesters
#
# Revision 1.4  2003/02/09 13:05:43  jalet
# Internationalization continues...
#
# Revision 1.3  2003/02/05 22:10:29  jalet
# Typos
#
# Revision 1.2  2003/02/05 22:02:22  jalet
# __import__ statement didn't work as expected
#
# Revision 1.1  2003/02/05 21:28:17  jalet
# Initial import into CVS
#
#
#

class PyKotaRequesterError(Exception):
    """An exception for Requester related stuff."""
    def __init__(self, message = ""):
        self.message = message
        Exception.__init__(self, message)
    def __repr__(self):
        return self.message
    __str__ = __repr__
    
def openRequester(config, printername) :
    """Returns a connection handle to the appropriate requester."""
    (backend, args) = config.getRequesterBackend(printername)
    try :
        if not backend.isalpha() :
            # don't trust user input
            raise ImportError
        exec "from pykota.requesters import %s as requesterbackend" % backend.lower()    
    except ImportError :
        raise PyKotaRequesterError, _("Unsupported requester backend %s") % backend
    else :    
        return getattr(requesterbackend, "Requester")(config, printername, args)
