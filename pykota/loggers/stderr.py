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

import sys

class Logger :
    """A logger class which logs to stderr."""
    def log_message(self, message, level="info") :
        """Sends the message to the appropriate logging subsystem."""
        sys.stderr.write("%s: PyKota : %s\n" % (level.upper(), message.strip()))
        sys.stderr.flush()
