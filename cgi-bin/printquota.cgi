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
# Revision 1.9  2003/06/30 13:47:26  jalet
# Allows multiple user / group names masks in the input field
#
# Revision 1.8  2003/06/30 13:32:01  jalet
# Much more powerful CGI script for quota reports
#
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
from pykota.reporter import PyKotaReporterError, openReporter

header = """Content-type: text/html

<?xml version="1.0" encoding="iso-8859-1"?>
<html>
  <head>
    <title>PyKota Reports</title>
  </head>
  <body>
    <form action="printquota.cgi" method="POST">
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
            <h2>PyKota Reports</h2>
          </td>
        </tr>
        <tr>
          <td colspan="3" align="center">
            <input type="submit" name="action" value="Report" />
          </td>
        </tr>
      </table>"""
    
footer = """
    </form>
  </body>
</html>"""  


class PyKotaReportGUI(PyKotaTool) :
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
        
    def htmlListPrinters(self, selected=[], mask="*") :    
        """Displays the printers multiple selection list."""
        printers = self.storage.getMatchingPrinters(mask)
        selectednames = [p.Name for p in selected]
        message = 'Printer : <select name="printers" multiple="multiple">'
        for printer in printers :
            if printer.Name in selectednames :
                message += '<option value="%s" selected="selected">%s</option>' % (printer.Name, printer.Name)
            else :
                message += '<option value="%s">%s</option>' % (printer.Name, printer.Name)
        message += '</select>'
        return message
        
    def htmlUGNamesInput(self, value="*") :    
        """Input field for user/group names wildcard."""
        return 'User / Group names mask : <input type="text" name="ugmask" size="20" value="%s" /> <em>e.g. <strong>jo*</strong></em>' % (value or "*")
        
    def htmlGroupsCheckbox(self, isgroup=0) :
        """Groups checkbox."""
        if isgroup :
            return 'Groups report : <input type="checkbox" checked="checked" name="isgroup" />'
        else :    
            return 'Groups report : <input type="checkbox" name="isgroup" />'
            
    def guiAction(self) :
        """Main function"""
        printers = ugmask = isgroup = None
        self.body = "<p>Please click on the menu above</p>\n"
        if self.form.has_key("action") :
            action = self.form["action"].value
            if action == "Report" :
                if self.form.has_key("printers") :
                    printersfield = self.form["printers"]
                    if type(printersfield) != type([]) :
                        printersfield = [ printersfield ]
                    printers = [self.storage.getPrinter(p.value) for p in printersfield]
                else :    
                    printers = self.storage.getMatchingPrinters("*")
                if self.form.has_key("ugmask") :     
                    ugmask = self.form["ugmask"].value
                else :     
                    ugmask = "*"
                if self.form.has_key("isgroup") :    
                    isgroup = 1
                else :    
                    isgroup = 0
            else :
                self.error(body, "Invalid action [%s]" % action)
        self.body += self.htmlListPrinters(printers or [])            
        self.body += "<br />"
        self.body += self.htmlUGNamesInput(ugmask)
        self.body += "<br />"
        self.body += self.htmlGroupsCheckbox(isgroup)
        if printers and ugmask :
            self.reportingtool = openReporter(admin, "text", printers, ugmask.split(), isgroup)
            self.body += "<pre>%s</pre>" % self.reportingtool.generateReport()
    
if __name__ == "__main__" :
    admin = PyKotaReportGUI()
    admin.form = cgi.FieldStorage()
    admin.guiAction()
    admin.guiDisplay()
