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

"""This modules defines a command line options parser for PyKota's command line tools."""

import sys
import os
import optparse
from gettext import gettext as _

from pykota import version
from pykota.utils import loginvalidparam, getdefaultcharset

def checkandset_pagesize(option, opt, value, optionparser) :
    """Checks and sets the page size."""
    from pykota.pdfutils import getPageSize
    if getPageSize(value) is None :
        loginvalidparam(opt, value, option.default)
        setattr(optionparser.values, option.dest, option.default)
    else :
        setattr(optionparser.values, option.dest, value)

def checkandset_savetoner(option, opt, value, optionparser) :
    """Checks and sets the save toner value."""
    if (value < 0.0) or (value > 99.0) :
        loginvalidparam(opt, value, option.default, \
                        _("Allowed range is (0..99)"))
        setattr(optionparser.values, option.dest, option.default)
    else :
        setattr(optionparser.values, option.dest, value)

def checkandset_positiveint(option, opt, value, optionparser) :
    """Checks if an option argument is a positive integer and validates the option if it is the case."""
    if not (value >= 0) :
        loginvalidparam(opt, value, option.default, \
                        _("Value must be positive"))
        setattr(optionparser.values, option.dest, option.default)
    else :
        setattr(optionparser.values, option.dest, value)

def checkandset_positivefloat(option, opt, value, optionparser) :
    """Checks if an option argument is a positive float and validates the option if it is the case."""
    if not (value >= 0.0) :
        loginvalidparam(opt, value, option.default, \
                        _("Value must be positive"))
        setattr(optionparser.values, option.dest, option.default)
    else :
        setattr(optionparser.values, option.dest, value)

def checkandset_percent(option, opt, value, optionparser) :
    """Checks if an option argument is comprised between 0.0 included and 100.0 not included, and validates the option if it is the case."""
    if not (0.0 <= value < 100.0) :
        loginvalidparam(opt, value, option.default, \
                        _("Value must be comprised between 0.0 included and 100.0 not included"))
        setattr(optionparser.values, option.dest, option.default)
    else :
        setattr(optionparser.values, option.dest, value)

def load_arguments_file(option, opt, value, optionparser) :
    """Loads arguments from a file, one per line."""
    setattr(optionparser.values, option.dest, value)
    try :
        argsfile = open(value.encode(getdefaultcharset(), "replace"), "r")
    except IOError :
        loginvalidparam(opt, value, additionalinfo=_("this option will be ignored"))
    else :
        arguments = [ l.strip().decode(getdefaultcharset(), "replace") for l in argsfile.readlines() ]
        argsfile.close()
        for i in range(len(arguments)) :
            argi = arguments[i]
            if argi.startswith('"') and argi.endswith('"') :
                arguments[i] = argi[1:-1]
        arguments.reverse()
        for arg in arguments :
            optionparser.rargs.insert(0, arg)

class PyKotaOptionParser(optparse.OptionParser) :
    """
    This class to define additional methods, and different help
    formatting, from the traditional OptionParser.
    """
    def __init__(self, *args, **kwargs) :
        """
        Initializes our option parser with additional attributes.
        """
        self.filterexpressions = []
        self.examples = []
        kwargs["version"] = "%s (PyKota) %s" % (os.path.basename(sys.argv[0]),
                                                version.__version__)
        optparse.OptionParser.__init__(self, *args, **kwargs)
        self.disable_interspersed_args()
        self.remove_version_and_help()
        self.add_generic_options()

    def format_help(self, formatter=None) :
        """
        Reformats help our way : adding examples and copyright
        message at the end.
        """
        if formatter is None :
            formatter = self.formatter
        result = []
        result.append(optparse.OptionParser.format_help(self, formatter) + "\n")
        result.append(self.format_filterexpressions())
        result.append(self.format_examples())
        result.append(self.format_copyright())
        return "".join(result)

    #
    # Below are PyKota specific additions
    #
    def format_filterexpressions(self, formatter=None) :
        """Formats filter expressions our way."""
        if formatter is None :
            formatter = self.formatter
        result = []
        if self.filterexpressions :
            result.append(formatter.format_heading(_("filtering expressions")))
            formatter.indent()
            result.append(formatter.format_description(_("Use the filtering expressions to extract only parts of the datas. Allowed filters are of the form 'key=value'. Wildcards are not expanded as part of these filtering expressions, so you can't use them here.")))
            result.append("\n")
            result.append(formatter.format_heading(_("allowed keys for now")))
            formatter.indent()
            for (expression, explanation) in self.filterexpressions :
                result.append(formatter.format_description("%s : %s" % (expression, explanation)))
            formatter.dedent()
            result.append("\n")
            result.append(formatter.format_heading(_("formatting of dates with the 'start' and 'end' filtering keys")))
            formatter.indent()
            result.append(formatter.format_description(_("YYYY : year boundaries")))
            result.append(formatter.format_description(_("YYYYMM : month boundaries")))
            result.append(formatter.format_description(_("YYYYMMDD : day boundaries")))
            result.append(formatter.format_description(_("YYYYMMDDhh : hour boundaries")))
            result.append(formatter.format_description(_("YYYYMMDDhhmm : minute boundaries")))
            result.append(formatter.format_description(_("YYYYMMDDhhmmss : second boundaries")))
            result.append(formatter.format_description(_("yesterday[+-N] : yesterday more or less N days (e.g. : yesterday-15)")))
            result.append(formatter.format_description(_("today[+-N] : today more or less N days (e.g. : today-15)")))
            result.append(formatter.format_description(_("tomorrow[+-N] : tomorrow more or less N days (e.g. : tomorrow-15)")))
            result.append(formatter.format_description(_("now[+-N] : now more or less N days (e.g. now-15)")))
            formatter.dedent()
            result.append("\n")
            result.append(formatter.format_description(_("'now' and 'today' are not exactly the same since 'today' represents the first or last second of the day depending on if it's used in a 'start=' or 'end=' date expression.")))
            result.append("\n")
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

    def add_filterexpression(self, expression, doc) :
        """Adds a filtering expression."""
        self.filterexpressions.append((expression, doc))

    def add_example(self, command, doc) :
        """Adds an usage example."""
        self.examples.append(("%prog " + command, doc))

    def remove_version_and_help(self) :
        """Removes the default definitions for options version and help."""
        for o in ("-h", "-help", "--help", "-v", "-version", "--version") :
            try :
                self.remove_option(o)
            except ValueError :
                pass

    def add_generic_options(self) :
        """Adds options which are common to all PyKota command line tools."""
        self.add_option("-h", "--help",
                              action="help",
                              help=_("show this help message and exit."))
        self.add_option("-v", "--version",
                              action="version",
                              help=_("show the version number and exit."))
        self.add_option("-A", "--arguments",
                              action="callback",
                              type="string",
                              dest="argumentsfile",
                              callback=load_arguments_file,
                              help=_("loads additional options and arguments from a file, one per line."))
