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
