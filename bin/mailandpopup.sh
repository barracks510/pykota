#! /bin/sh
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
#
PATH=$PATH:/bin:/usr/bin:/usr/local/bin:/opt/bin
#
# user's name
UNAME=$1
# printer's name
PNAME=$2
# message's recipient
RECIPIENT=$3
# message's body
MESSAGE=$4
#
# Convert message body to UTF8 for WinPopup
UTF8MESSAGE=`echo "$MESSAGE" | iconv --to-code utf-8 --from-code iso-8859-15`
#
# Send original message to user
mail -s "Print Quota problem" $RECIPIENT <<EOF1
$MESSAGE
EOF1
#
# Send some information to root as well
mail -s "Print Quota problem on printer $PNAME" root <<EOF2
Print Quota problem for user $UNAME
EOF2
#
# Launch WinPopup on user's host (may need a real Samba or NT domain)
# In some cases the username does not suffice for smbclient to send a message;
# we must also supply the IP address. This will use smbstatus to get all IPs
# where the user is logged in and send the message there:
IPS=`smbstatus -b -u "$UNAME" | grep "$UNAME" | cut -d '(' -f 2,2 | cut -d ')' -f 1,1`
for i in $IPS ; do
    echo "$UTF8MESSAGE" | smbclient -M "$UNAME" -I $i 2>&1 ;
done
