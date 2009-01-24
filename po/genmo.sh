#! /bin/sh
#
# PyKota - Print Quotas for CUPS
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
for dir in * ; do
    if [ -d $dir ] ; then
        if [ -e $dir/pykota.po ] ; then
            echo -n $dir ;
            cd $dir ;
            chmod 644 *.?o ;
            msgmerge --no-wrap --no-location --no-fuzzy-matching --output-file=pykota.po.new pykota.po ../pykota.pot ;
            mv pykota.po.new pykota.po ;
            /bin/rm -f pykota.mo ;
            msgfmt -o pykota.mo pykota.po ;
            cd .. ;
        fi ;
    fi ;
done
