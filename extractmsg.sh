#! /bin/sh
#
# PyKota - Print Quotas for CUPS and LPRng
#
# (c) 2003, 2004, 2005, 2006 Jerome Alet <alet@librelogiciel.com>
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
#
# First ensures there's no existing file
rm -f /tmp/pykota.po
#
# Then extract messages
xgettext --keyword=N_ --language=python --default-domain=pykota --output-dir=/tmp --no-location --msgid-bugs-address="alet@librelogiciel.com" $*

