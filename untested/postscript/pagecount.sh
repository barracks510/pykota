#!/bin/sh
#
# Adapted and modified from the printquota project 
# http://printquota.sourceforge.net
#
# printquota (c) 2002-2003 Ahmet Ozturk & Cagatay Koksoy
# printquota is distributed under the GNU General Public License
#
# Usage : pagecount.sh file.ps
#
(
(cat $* | sed -n -e '/%!PS-Adobe-/,/\%\%EOF/p' | grep -E -v "/Duplex|PageSize")
echo currentdevice /PageCount gsgetdeviceprop == flush
) | gs -q -sDEVICE=bit -sOutputFile=/dev/null -r5 - | tail -1

