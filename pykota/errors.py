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

"""This module defines ALL PyKota specific exceptions."""

class PyKotaError(Exception) :
    """Mother class of all PyKota exceptions."""
    def __init__(self, value) :
        """Saves the value passed as a parameter."""
        self.value = value

    def __str__(self) :
        """Returns an unicode string representation."""
        try :
            return unicode(self.value, errors="replace")
        except TypeError :
            return unicode(self.value) # None and strings which are already unicode

class PyKotaToolError(PyKotaError) :
    """PyKota Exception for all executables."""
    pass

class PyKotaToolError(PyKotaError) :
    """PyKota Exception for all executables."""
    pass

class PyKotaCommandLineError(PyKotaToolError) :
    """PyKota Exception for errors on executables' command line."""
    pass

class PyKotaStorageError(PyKotaError) :
    """PyKota Exception for database backend related errors."""
    pass

class PyKotaConfigError(PyKotaError) :
    """PyKota Exception for errors in PyKota's configuration."""
    pass

class PyKotaAccounterError(PyKotaError) :
    """PyKota Exception for errors in PyKota accounters."""
    pass

class PyKotaReporterError(PyKotaError) :
    """PyKota Exception for errors in PyKota report generators."""
    pass

class PyKotaLoggingError(PyKotaError) :
    """PyKota Exception for errors in PyKota logging."""
    pass

class PyKotaTimeoutError(PyKotaError) :
    """An exception for timeouts."""
    pass
