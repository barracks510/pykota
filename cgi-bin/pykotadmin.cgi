#! /usr/bin/env python

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
# Revision 1.1  2003/05/03 17:33:08  jalet
# First shot at the complete web-based administrative interface.
#
#
#

import sys
import os
import cgi
from pykota.tool import PyKotaTool, PyKotaToolError

header = """Content-type: text/html

<?xml version="1.0" encoding="iso-8859-1"?>
<html>
  <head>
    <title>PyKota Administration</title>
  </head>
  <body>
    <form action="pykotadmin.cgi" method="POST">
      <table>
        <tr>
          <td>
            <p>
              <a href="http://www.librelogiciel.com/software/"><img src="http://www.librelogiciel.com/software/PyKota/calllogo" alt="PyKota's Logo" /></a>
              <br />
              <a href="http://www.librelogiciel.com/software/">PyKota</a>
            </p>
          </td>
          <td colspan="2">
            <h2>PyKota Administration</h2>
          </td>
        </tr>
        <tr>
          <td>
            <input type="submit" name="action" value="Report" />
          </td>
          <td>
            <input type="submit" name="action" value="Modify" />
          </td>
          <td>
            <input type="submit" name="action" value="Warn" />
          </td>
        </tr>
      </table>"""
    
footer = """
    </form>
  </body>
</html>"""  


class PyKotaAdminGUI(PyKotaTool) :
    """PyKota Administrative GUI"""
    def guiDisplay(self) :
        """Displays the administrative interface."""
        global header, footer
        print header
        print self.body
        print footer
        
    def error(self, message) :
        """Adds an error message to the GUI's body."""
        if message :
            self.body = '<p><font color="red">%s</font></p>\n%s' % (message, self.body)
        
    def htmlListPrinters(self) :    
        """Displays the printers multiple selection list."""
        printers = self.storage.getMatchingPrinters("*")
        message = 'Printer : <select name="printers" multiple="multiple">'
        for (printerid, printername) in printers :
            message += '<option value="%s">%s</option>' % (printerid, printername)
        message += '</select>'
        return message
        
    def guiAction(self) :
        """Main function"""
        self.body = "<p>Please click on the menu above</p>\n"
        form = cgi.FieldStorage()
        if form.has_key("action") :
            action = form["action"].value
            if action == "Modify" :
                self.error("Not implemented yet ! Sorry.")
            elif action == "Warn" :
                self.error("Not implemented yet ! Sorry.")
            elif action == "Report" :
                self.error("Not implemented yet ! Sorry.")
            else :
                self.error(body, "Invalid action [%s]" % action)
        self.body = self.body + self.htmlListPrinters()            
    
if __name__ == "__main__" :
    admin = PyKotaAdminGUI()
    admin.guiAction()
    admin.guiDisplay()
