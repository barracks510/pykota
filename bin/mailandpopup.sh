#! /bin/sh
#
# PyKota - Print Quotas for CUPS and LPRng
#
# (c) 2003 Jerome Alet <alet@librelogiciel.com>
# You're welcome to redistribute this software under the
# terms of the GNU General Public Licence version 2.0
# or, at your option, any higher version.
#
# You can read the complete GNU GPL in the file COPYING
# which should come along with this software, or visit
# the Free Software Foundation's WEB site http://www.fsf.org
#
# $Id$
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
UTF8MESSAGE=`echo "$MESSAGE" | /usr/bin/iconv --to-code utf-8 --from-code iso-8859-15`
#
# Send original message to user
/usr/bin/mail -s "Print Quota problem" $RECIPIENT <<EOF1
$MESSAGE
EOF1
# 
# Send some information to root as well
/usr/bin/mail -s "Print Quota problem on printer $PNAME" root <<EOF2
Print Quota problem for user $UNAME
EOF2
#
# Launch WinPopup on user's host (may need a real Samba or NT domain) 
echo "$UTF8MESSAGE" | /usr/bin/smbclient -M "$UNAME" 2>&1 >/dev/null
