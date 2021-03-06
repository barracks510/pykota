#! /bin/sh
#
# PyKota
#
# PyKota : Print Quotas for CUPS
#
# (c) 2003-2013 Jerome Alet <alet@librelogiciel.com>
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

# Use this to clean the tree from temporary files

rm -f MANIFEST ChangeLog
find . -name "*.bak" -exec rm -f {} \;
find . -name "\#*\#" -exec rm -f {} \;
find . -name "*~" -exec rm -f {} \;
find . -name "*.pyc" -exec rm -f {} \;
find . -name "*.pyo" -exec rm -f {} \;
find . -name "*.jem" -exec rm -f {} \;
find docs -name "*.html" -exec rm -f {} \;
find docs -name "*.pdf" -exec rm -f {} \;
find docs -name "*.tex" -exec rm -f {} \;
find docs -name "*.dvi" -exec rm -f {} \;
rm -fr build dist
rm -fr debian/tmp/
rm -fr docs/pykota/ docs/pykota.junk/
