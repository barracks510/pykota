#!/bin/sh
#
# PyKota : Print Quotas for CUPS
#
# (c) 2003, 2004, 2005, 2006, 2007 Jerome Alet <alet@librelogiciel.com>
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
#
# $Id$
#
#
#
# This script was freely adapted and modified from the printquota project 
# http://printquota.sourceforge.net for inclusion into PyKota.
#
# printquota (c) 2002-2003 Ahmet Ozturk & Cagatay Koksoy
# printquota is distributed under the GNU General Public License
#
# Usage : pagecount.sh <file.ps
#
(
(sed -n -e '/%!PS-Adobe-/,/\%\%EOF/p' | grep -E -v "/Duplex|PageSize")
echo currentdevice /PageCount gsgetdeviceprop == flush
) | gs -q -sDEVICE=bit -sOutputFile=/dev/null -r5 - | tail -1

