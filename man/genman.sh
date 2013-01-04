#! /bin/sh
#
# PyKota - Print Quotas for CUPS
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
#
for prog in pksetup \
    pkrefund \
    pknotify \
    pkusers \
    pkinvoice \
    pkturnkey \
    pkbcodes \
    pkbanner \
    autopykota \
    dumpykota \
    edpykota \
    pykotme \
    repykota \
    warnpykota \
    pkprinters \
    pykosd ; do
    echo "$prog" ;
    help2man --no-info \
             --section=1 \
             --manual="User Commands" \
             --source="C@LL - Conseil Internet & Logiciels Libres" \
             --output="temp$prog.1" \
             "$prog" ;
    /bin/sed -e "s/--/\\\-\\\-/g" <"temp$prog.1" >"$prog.1" ;
    /bin/rm -f "temp$prog.1"
    cd ../po ;
    for dir in * ; do
        if [ -d $dir ] ; then
            if [ -e $dir/pykota.po ] ; then
                echo "  $dir" ;
                cd ../man/$dir ;
                help2man --no-info \
                         --locale=$dir \
                         --section=1 \
                         --manual="User Commands" \
                         --source="C@LL - Conseil Internet & Logiciels Libres" \
                         --output="temp$prog.1" \
                         "$prog" ;
                /bin/sed -e "s/--/\\\-\\\-/g" <"temp$prog.1" >"$prog.1" ;
                /bin/rm -f "temp$prog.1"
                cd ../../po ;
            fi ;
        fi ;
    done
    cd ../man ;
    echo ;
done
