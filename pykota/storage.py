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
# Revision 1.1  2003/02/05 21:28:17  jalet
# Initial import into CVS
#
#
#

class PyKotaStorageError(Exception):
    """An exception for Quota Storage related stuff."""
    def __init__(self, message = ""):
        self.message = message
        Exception.__init__(self, message)
    def __repr__(self):
        return self.message
    __str__ = __repr__
    
def openConnection(config, asadmin=0) :
    """Returns a connection handle to the appropriate Quota Storage Database."""
    (backend, host, database, admin, user) = config.getStorageBackend()
    try :
        module = __import__("pykota.storages." + backend.lower())
    except ImportError :
        raise PyKotaStorageError, "Unsupported quota storage backend %s" % backend
    else :    
        return getattr(module, "Storage")(host, database, (asadmin and admin) or user)
