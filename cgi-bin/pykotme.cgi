#! /usr/bin/python
# -*- coding: ISO-8859-15 -*-

# PyKota Print Quotes generator
#
# PyKota - Print Quotas for CUPS and LPRng
#
# (c) 2003, 2004, 2005 Jerome Alet <alet@librelogiciel.com>
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
#

import sys
import os
import cgi
import urllib
import cStringIO

from pykota import version
from pykota.tool import PyKotaTool, PyKotaToolError
from pykota.pdlanalyzer import PDLAnalyzer, PDLAnalyzerError
from pykota.cgifuncs import getLanguagePreference, getCharsetPreference

header = """Content-type: text/html

<?xml version="1.0" encoding="%s"?>
<html>
  <head>
    <title>%s</title>
    <link rel="stylesheet" type="text/css" href="/pykota.css" />
  </head>
  <body>
    <form action="pykotme.cgi" method="POST" enctype="multipart/form-data">
      <table>
        <tr>
          <td>
            <p>
              <a href="http://www.librelogiciel.com/software/"><img src="%s?version=%s" alt="PyKota's Logo" /></a>
              <br />
              <a href="http://www.librelogiciel.com/software/">PyKota v%s</a>
            </p>
          </td>
          <td colspan="2">
            <h1>%s</h1>
          </td>
        </tr>
        <tr>
          <td colspan="3" align="center">
            <input type="submit" name="report" value="%s" />
          </td>
        </tr>
      </table>"""
    
footer = """
      <table>
        <tr>
          <td colspan="3" align="center">
            <input type="submit" name="report" value="%s" />
          </td>
        </tr>
      </table>  
    </form>
  </body>
</html>"""  

class PyKotMeGUI(PyKotaTool) :
    """PyKota Quote's Generator GUI"""
    def guiDisplay(self) :
        """Displays the administrative interface."""
        global header, footer
        print header % (self.getCharset(), _("PyKota Reports"), self.config.getLogoURL(), version.__version__, version.__version__, _("PyKota Quotes"), _("Quote"))
        print self.body
        print footer % _("Quote")
        
    def error(self, message) :
        """Adds an error message to the GUI's body."""
        if message :
            self.body = '<p><font color="red">%s</font></p>\n%s' % (message, self.body)
        
    def htmlListPrinters(self, selected=[], mask="*") :    
        """Displays the printers multiple selection list."""
        printers = self.storage.getMatchingPrinters(mask)
        selectednames = [p.Name for p in selected]
        message = '<table><tr><td valign="top">%s :</td><td valign="top"><select name="printers" multiple="multiple">' % _("Printer")
        for printer in printers :
            if printer.Name in selectednames :
                message += '<option value="%s" selected="selected">%s (%s)</option>' % (printer.Name, printer.Name, printer.Description)
            else :
                message += '<option value="%s">%s (%s)</option>' % (printer.Name, printer.Name, printer.Description)
        message += '</select></td></tr></table>'
        return message
        
    def guiAction(self) :
        """Main function"""
        printers = inputfile = None
        self.body = "<p>%s</p>\n" % _("Please click on the above button")
        if self.form.has_key("report") :
            if self.form.has_key("printers") :
                printersfield = self.form["printers"]
                if type(printersfield) != type([]) :
                    printersfield = [ printersfield ]
                printers = [self.storage.getPrinter(p.value) for p in printersfield]
            else :    
                printers = self.storage.getMatchingPrinters("*")
            if self.form.has_key("inputfile") :    
                inputfile = self.form["inputfile"].value
                
        self.body += self.htmlListPrinters(printers or [])            
        self.body += "<br />"
        self.body += _("Filename") + " : "
        self.body += '<input type="file" size="64" name="inputfile" />'
        self.body += "<br />"
        if inputfile :
            try :
                parser = PDLAnalyzer(cStringIO.StringIO(inputfile))
                jobsize = parser.getJobSize()
            except PDLAnalyzerError, msg :    
                self.body += '<p><font color="red">%s</font></p>' % msg
            else :    
                self.body += "<p>%s</p>" % (_("Job size : %i pages") % jobsize)
                
            remuser = os.environ.get("REMOTE_USER", "root")    
            # special hack to accomodate mod_auth_ldap Apache module
            try :
                remuser = remuser.split("=")[1].split(",")[0]
            except IndexError :    
                pass
            if remuser == "root" :    
                self.body += "<p>%s</p>" % _("The exact cost of a print job can only be determined for a particular user. Please retry while logged-in.")
            else :    
                try :    
                    user = self.storage.getUser(remuser)
                    if user.Exists :
                        for printer in printers :
                            upquota = self.storage.getUserPQuota(user, printer)
                            if upquota.Exists :
                                cost = upquota.computeJobPrice(jobsize)
                                self.body += "<p>%s</p>" % (_("Cost on printer %s : %.2f") % (printer.Name, cost))
                except :
                    self.body += '<p><font color="red">%s</font></p>' % self.crashed("CGI Error").replace("\n", "<br />")
            
if __name__ == "__main__" :
    os.environ["LC_ALL"] = getLanguagePreference()
    admin = PyKotMeGUI(lang=os.environ["LC_ALL"], charset=getCharsetPreference())
    admin.deferredInit()
    admin.form = cgi.FieldStorage()
    admin.guiAction()
    admin.guiDisplay()
    try :
        admin.storage.close()
    except (TypeError, NameError, AttributeError) :    
        pass
        
    sys.exit(0)
