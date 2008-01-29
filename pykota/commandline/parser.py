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

"""This modules defines a command line options parser for PyKota's command line tools."""

import optparse
from gettext import gettext as _

from pykota import version

class PyKotaOptionParser(optparse.OptionParser) :
    """
    This class to define additional methods, and different help
    formatting, from the traditional OptionParser.
    """   
    def __init__(self, *args, **kwargs) :
        """
        Initializes our option parser with additional attributes.
        """
        self.examples = []
        optparse.OptionParser.__init__(self, *args, **kwargs)
        self.disable_interspersed_args()
        self.add_option("-", "--version",
                             action="store_true",
                             dest="version",
                             help=_("show %prog's version number and exit."))
        
    def format_help(self, formatter=None) :
        """
        Reformats help our way : adding examples and copyright
        message at the end.
        """
        if formatter is None :
            formatter = self.formatter
        result = []
        result.append(optparse.OptionParser.format_help(self, formatter) + "\n")
        result.append(self.format_examples() + "\n")
        result.append(self.format_copyright() + "\n")
        return "".join(result)
        
    def format_examples(self, formatter=None) :
        """Formats examples our way."""
        if formatter is None :
            formatter = self.formatter
        result = []
        if self.examples :
            result.append(formatter.format_heading(_("examples")))
            formatter.indent()
            for (cmd, explanation) in self.examples :
                result.append(formatter.format_description(self.expand_prog_name(cmd)))
                result.append(formatter.format_description(self.expand_prog_name(explanation)) + "\n")
            formatter.dedent()
        return "".join(result)    
        
    def format_copyright(self, formatter=None) :
        """Formats copyright message our way."""
        if formatter is None :
            formatter = self.formatter
        result = []    
        result.append(formatter.format_heading(_("licensing terms")))
        formatter.indent()
        result.append(formatter.format_description("(c) %s %s\n" \
                                                      % (version.__years__, \
                                                         version.__author__)))
        for part in version.__gplblurb__.split("\n\n") :
            result.append(formatter.format_description(part) + "\n")
        formatter.dedent()    
        return "".join(result)
        
    def add_example(self, command, doc) :    
        """Adds an usage example."""
        self.examples.append(("%prog " + command, doc))
