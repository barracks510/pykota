# -*- coding: utf-8 -*-*-
#
# PyKota : Print Quotas for CUPS
#
# (c) 2003, 2004, 2005, 2006, 2007, 2008 Jerome Alet <alet@librelogiciel.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# $Id$
#
#

"""This module defines a class for PyKota logging through stderr."""

import sys
import os

__revision__ = "$Id$"

class Logger :
    """A logger class which logs to stderr."""
    def log_message(self, message, level="info") :
        """Sends the message to the appropriate logging subsystem."""
        try :
            sys.stderr.write("%s: PyKota (PID %s) : %s\n" \
                                              % (level.upper(), \
                                                 os.getpid(), \
                                                 message.strip()))
        except IOError :
            pass # What else could we do ?
        else :
            try :
                sys.stderr.flush()
            except IOError :
                pass # What else could we do ?
