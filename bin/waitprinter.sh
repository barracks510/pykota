#! /bin/sh
#
# PyKota - Print Quotas for CUPS and LPRng
#
# (c) 2003-2004 Jerome Alet <alet@librelogiciel.com>
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
# Fix by Matt Hyclak & Jerome Alet

# If ending phase, after the job has been fully transmitted to the printer
# we have to wait for the printer being in printing mode before checking
# if it is idle, otherwise we could have problems with slow printers.
# When using the pykota filter, PYKOTAPHASE is not defined at the
# first requesting stage (which is the ending phase of the previous
# job), because waiting for the printer being printing wouldn't be OK :
# the printer would effectively never print again if the previous job
# was already fully printed.
PATH=$PATH:/bin:/usr/bin:/usr/local/bin:/opt/bin
if [ x$PYKOTAACTION != "xDENY" ] && [ x$PYKOTAPHASE == "xAFTER" ] ; then
  until snmpget -v1 -c public -Ov $1 HOST-RESOURCES-MIB::hrPrinterStatus.1 | grep -i printing >/dev/null; do
   sleep 1 ;
  done
fi

# In any case, wait until the printer is idle again.
until snmpget -v1 -c public -Ov $1 HOST-RESOURCES-MIB::hrPrinterStatus.1 | grep -i idle >/dev/null ; do 
  sleep 1 ;
done

