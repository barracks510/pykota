#! /usr/bin/python

# PyKota Print Quota Reports generator
#
# PyKota - Print Quotas for CUPS
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
# $Log$
# Revision 1.1  2003/02/10 13:41:38  jalet
# repykota cgi script added.
# cleaner doc.
#

import sys
import os
import cgi

import jaxml

x = jaxml.CGI_document()
x.html()
x._push()
x.head()
x.title("Print Quota Report")
x._pop()

x.h2("Print Quota Report")

x.pre()

out = os.popen("repykota")
x._text(out.read())
out.close()

x._output()
