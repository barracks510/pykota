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

"""This module defines some utility functions which make no sense as methods."""

import sys
import locale
import gettext

def initlocale(lang="", cset=None) :
    """Initializes the locale stuff."""
    try :
        locale.setlocale(locale.LC_ALL, (lang, cset))
    except (locale.Error, IOError) :
        locale.setlocale(locale.LC_ALL, None)
    (language, charset) = locale.getlocale()
    language = language or "C"
    try :
        charset = charset or locale.getpreferredencoding()
    except locale.Error :    
        charset = sys.stdout.encoding or sys.getfilesystemencoding()

    # Dirty hack : if the charset is ASCII, we can safely use UTF-8 instead
    # This has the advantage of allowing transparent support for recent
    # versions of CUPS which (en-)force charset to UTF-8 when printing.
    # This should be needed only when printing, but is probably (?) safe
    # to do when using interactive commands.
    if charset.upper() in ('ASCII', 'ANSI_X3.4-1968') :
        charset = "UTF-8"
    return (language, charset)

def initgettext(lang, cset) :
    """Initializes gettext translations for PyKota."""
    try :
        try :
            trans = gettext.translation("pykota", \
                                        languages=["%s.%s" % (lang, 
                                                              cset)], 
                                        codeset=cset)
        except TypeError : # Python <2.4
            trans = gettext.translation("pykota", 
                                        languages=["%s.%s" % (lang, 
                                                              cset)])
        trans.install(unicode=True)
    except :
        gettext.NullTranslations().install(unicode=True)

def databaseToUnicode(text) :
    """Converts from database format (UTF-8) to unicode."""
    if text is not None :
        return text.decode("UTF-8", "replace")
    else : 
        return None
    
def unicodeToDatabase(text) :
    """Converts from unicode to database format (UTF-8)."""
    if text is not None : 
        return text.encode("UTF-8", "replace")
    else :    
        return None
            
def logerr(text) :
    """Logs an unicode text to stderr."""
    sys.stderr.write(text.encode(sys.stdout.encoding, "replace"))
            
