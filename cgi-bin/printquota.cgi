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
# Revision 1.2  2003/02/12 11:31:51  jalet
# doesn't use the jaxml module anymore
#
# Revision 1.1  2003/02/10 13:41:38  jalet
# repykota cgi script added.
# cleaner doc.
#

import sys
import os
import cgi

header = """Content-type: text/html

<?xml version="1.0" encoding="iso-8859-1"?>
<html>
  <head>
    <title>Print Quota Report</title>
  </head>
  <body>
    <h2>Print Quota Report</h2>
    <pre>"""

footer = """
    </pre>
  </body>
</html>"""  

print header

out = os.popen("repykota")
print out.read().strip()
out.close()

print footer
