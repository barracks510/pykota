# PyKota
# -*- coding: ISO-8859-15 -*-
#
# PyKota : Print Quotas for CUPS and LPRng
#
# (c) 2003-2004 Jerome Alet <alet@librelogiciel.com>
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
# Revision 1.7  2004/05/24 11:59:49  jalet
# More robust (?) code
#
# Revision 1.6  2004/05/07 14:43:44  jalet
# Now logs the PID too
#
# Revision 1.5  2004/01/08 14:10:33  jalet
# Copyright year changed.
#
# Revision 1.4  2003/10/07 09:07:29  jalet
# Character encoding added to please latest version of Python
#
# Revision 1.3  2003/04/23 22:13:57  jalet
# Preliminary support for LPRng added BUT STILL UNTESTED.
#
# Revision 1.2  2003/03/29 13:45:27  jalet
# GPL paragraphs were incorrectly (from memory) copied into the sources.
# Two README files were added.
# Upgrade script for PostgreSQL pre 1.01 schema was added.
#
# Revision 1.1  2003/02/05 21:28:17  jalet
# Initial import into CVS
#
#
#

import sys
import os

class Logger :
    """A logger class which logs to stderr."""
    def log_message(self, message, level="info") :
        """Sends the message to the appropriate logging subsystem."""
        try :
            sys.stderr.write("%s: PyKota (PID %s) : %s\n" % (level.upper(), os.getpid(), message.strip()))
        except IOError :    
            pass # What else could we do ?
        else :    
            try :
                sys.stderr.flush()
            except IOError :    
                pass # What else could we do ?
