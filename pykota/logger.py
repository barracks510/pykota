# -*- coding: utf-8 -*-
#
# PyKota : Print Quotas for CUPS
#
# (c) 2003-2009 Jerome Alet <alet@librelogiciel.com>
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

"""This module defines base classes used by all logging backends."""

import os
import imp

from pykota.errors import PyKotaLoggingError

def openLogger(backend) :
    """Returns the appropriate logger subsystem object."""
    try :
        loggingbackend = imp.load_source("loggingbackend",
                                         os.path.join(os.path.dirname(__file__),
                                                      "loggers",
                                                      "%s.py" % backend.lower()))
    except ImportError :
        raise PyKotaLoggingError, _("Unsupported logging subsystem %s") % backend
    else :
        return loggingbackend.Logger()
