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

"""This module defines classes to display progress reports."""

import sys
import time

class Percent :
    """A class to display progress."""
    def __init__(self, app, size=None) :
        """Initializes the engine."""
        self.isatty = sys.stdout.isatty()
        self.app = app
        self.size = None
        if size :
            self.setSize(size)
        self.previous = None
        self.before = time.time()

    def setSize(self, size) :
        """Sets the total size."""
        self.number = 0
        self.size = size
        if size :
            self.factor = 100.0 / float(size)

    def display(self, msg) :
        """Displays the value."""
        if self.isatty :
            self.app.display(msg)
            sys.stdout.flush()

    def oneMore(self) :
        """Increments internal counter."""
        if self.size :
            self.number += 1
            percent = "%.02f" % (float(self.number) * self.factor)
            if percent != self.previous : # optimize for large number of items
                self.display("\r%s%%" % percent)
                self.previous = percent

    def done(self) :
        """Displays the 'done' message."""
        after = time.time()
        if self.size :
            try :
                speed = self.size / ((after - self.before) + 0.00000000001) # adds an epsilon to avoid an user's problem I can't reproduce...
            except ZeroDivisionError :
                speed = 1 # Fake value in case of division by zero, shouldn't happen anyway with the epsilon above...
            self.display("\r100.00%%\r        \r%s. %s : %.2f %s.\n" \
                     % (_("Done"), _("Average speed"), speed, _("entries per second")))
        else :
            self.display("\r100.00%%\r        \r%s.\n" % _("Done"))

