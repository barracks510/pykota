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
    backend = config.getRequesterBackend(printername)
    try :
        if not backend.isalpha() :
            # don't trust user input
            raise ImportError
        exec "from pykota.requesters import %s as requesterbackend" % backend.lower()    
    except ImportError :
        raise PyKotaRequesterError, _("Unsupported requester backend %s") % backend
    else :    
        return getattr(requesterbackend, "Requester")(config, printername)
