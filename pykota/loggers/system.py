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
# Revision 1.3  2003/02/27 22:55:20  jalet
# WARN log priority doesn't exist.
#
# Revision 1.2  2003/02/05 23:47:54  jalet
# Forgotten default argument
#
# Revision 1.1  2003/02/05 23:09:20  jalet
# Name conflict
#
#
#

import sys
import syslog

class Logger :
    """A logger class which logs to syslog."""
    def __init__(self) :
        """Opens the logging subsystem."""
        syslog.openlog("PyKota", 0, syslog.LOG_LPR)
        
    def __del__(self) :    
        """Ensures the logging subsystem is closed."""
        syslog.closelog()
        
    def log_message(self, message, level="info") :
        """Sends the message to syslog."""
        priority = getattr(syslog, "LOG_%s" % level.upper(), syslog.LOG_DEBUG)
        syslog.syslog(priority, message)
