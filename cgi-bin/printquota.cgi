#! /usr/bin/python

# PyKota Print Quota Reports generator
#
# PyKota - Print Quotas for CUPS and LPRng
#
# (c) 2003 Jerome Alet <alet@librelogiciel.com>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# $Id$
#
# $Log$
# Revision 1.7  2003/06/30 12:46:15  jalet
# Extracted reporting code.
#
# Revision 1.6  2003/04/23 22:13:56  jalet
# Preliminary support for LPRng added BUT STILL UNTESTED.
#
# Revision 1.5  2003/04/17 21:30:09  jalet
# Now includes the logo
#
# Revision 1.4  2003/04/08 21:20:25  jalet
# CGI Script now displays a link to PyKota's website.
#
# Revision 1.3  2003/03/29 13:45:27  jalet
# GPL paragraphs were incorrectly (from memory) copied into the sources.
# Two README files were added.
# Upgrade script for PostgreSQL pre 1.01 schema was added.
#
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

from pykota import version
from pykota.tool import PyKotaTool, PyKotaToolError
from pykota.config import PyKotaConfigError
from pykota.storage import PyKotaStorageError

header = """Content-type: text/html

<?xml version="1.0" encoding="iso-8859-1"?>
<html>
  <head>
    <title>Print Quota Report</title>
  </head>
  <body>
    <h2>Print Quota Report</h2>
    <p>
      <pre>"""

footer = """
      </pre>
    </p>  
    <p>
      <a href="http://www.librelogiciel.com/software/"><img src="http://www.librelogiciel.com/software/PyKota/calllogo" /></a>
      <br />
      Report generated with <a href="http://www.librelogiciel.com/software/">PyKota</a>
    </p>
  </body>
</html>"""  

print header

out = os.popen("repykota")
print out.read().strip()
out.close()

print footer
