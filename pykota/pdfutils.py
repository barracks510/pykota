# -*- coding: UTF-8 -*-
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

"""This module contains helper methods for PDF related work."""

def getPageSize(pgsize) :
    """Returns the correct page size or None if not found."""
    try :
        import reportlab.lib.pagesizes as sizes
    except ImportError :    
        pass
    else :    
        try :
            return getattr(sizes, pgsize.upper(), getattr(sizes, 
                                                          pgsize.lower(), 
                                                          None))
        except UnicodeError :            
            pass
    return None        
