#! /usr/bin/python
# -*- coding: ISO-8859-15 -*-

# PyKota Print Quota Reports generator
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

from pykota import version
from pykota.tool import PyKotaToolError
from pykota.dumper import DumPyKota
from pykota.cgifuncs import getLanguagePreference, getCharsetPreference

header = """Content-type: text/html

<?xml version="1.0" encoding="%s"?>
<html>
  <head>
    <title>%s</title>
    <link rel="stylesheet" type="text/css" href="/pykota.css" />
  </head>
  <body>
    <form action="dumpykota.cgi" method="GET">
      <table>
        <tr>
          <td>
            <p>
              <a href="http://www.librelogiciel.com/software/"><img src="http://www.librelogiciel.com/software/PyKota/pykota.png?version=%s" alt="PyKota's Logo" /></a>
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
      </table>
      <p>
        %s
      </p>"""
    
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

class PyKotaDumperGUI(DumPyKota) :
    """PyKota Dumper GUI"""
    def guiDisplay(self) :
        """Displays the dumper interface."""
        global header, footer
        print header % (self.getCharset(), _("PyKota Data Dumper"), version.__version__, version.__version__, _("PyKota Data Dumper"), _("Dump"), _("Please click on the above button"))
        print self.htmlListDataTypes(self.options.get("data", "")) 
        print "<br />"
        print self.htmlListFormats(self.options.get("format", ""))
        print "<br />"
        print self.htmlFilterInput(" ".join(self.arguments))
        print footer % _("Dump")
        
    def htmlListDataTypes(self, selected="") :    
        """Displays the datatype selection list."""
        message = '<table><tr><td valign="top">%s :</td><td valign="top"><select name="datatype">' % _("Data Type")
        for dt in self.validdatatypes.items() :
            if dt[0] == selected :
                message += '<option value="%s" selected="selected">%s (%s)</option>' % (dt[0], dt[0], dt[1])
            else :
                message += '<option value="%s">%s (%s)</option>' % (dt[0], dt[0], dt[1])
        message += '</select></td></tr></table>'
        return message
        
    def htmlListFormats(self, selected="") :    
        """Displays the formats selection list."""
        message = '<table><tr><td valign="top">%s :</td><td valign="top"><select name="format">' % _("Output Format")
        for fmt in self.validformats.items() :
            if fmt[0] == selected :
                message += '<option value="%s" selected="selected">%s (%s)</option>' % (fmt[0], fmt[0], fmt[1])
            else :
                message += '<option value="%s">%s (%s)</option>' % (fmt[0], fmt[0], fmt[1])
        message += '</select></td></tr></table>'
        return message
        
    def htmlFilterInput(self, value="") :    
        """Input the optional dump filter."""
        return _("Filter") + (' : <input type="text" name="filter" size="40" value="%s" /> <em>e.g. <strong>username=jerome printername=HP2100</strong></em>' % (value or ""))
        
    def guiAction(self) :
        """Main function"""
        try :
            wantreport = self.form.has_key("report")
        except TypeError :    
            pass # WebDAV request probably, seen when trying to open a csv file in OOo
        else :    
            if wantreport :
                if self.form.has_key("datatype") :
                    self.options["data"] = self.form["datatype"].value
                if self.form.has_key("format") :
                    self.options["format"] = self.form["format"].value
                if self.form.has_key("filter") :    
                    self.arguments = self.form["filter"].value.split()
                    
                # when no authentication is done, or when the remote username    
                # is 'root' (even if not run as root of course), then unrestricted
                # dump is allowed.
                remuser = os.environ.get("REMOTE_USER", "root")    
                # special hack to accomodate mod_auth_ldap Apache module
                try :
                    remuser = remuser.split("=")[1].split(",")[0]
                except IndexError :    
                    pass
                if remuser != "root" :
                    # non-'root' users when the script is password protected
                    # can not dump any data as they like, we restrict them
                    # to their own datas.
                    if self.options["data"] not in ["printers", "pmembers", "groups", "gpquotas"] :
                        self.arguments.append("username=%s" % remuser)
                    
                if self.options["format"] in ("csv", "ssv") :
                    #ctype = "application/vnd.sun.xml.calc"     # OpenOffice.org
                    ctype = "text/comma-separated-values"
                    fname = "dump.csv"
                elif self.options["format"] == "tsv" :
                    #ctype = "application/vnd.sun.xml.calc"     # OpenOffice.org
                    ctype = "text/tab-separated-values"
                    fname = "dump.tsv"
                elif self.options["format"] == "xml" :
                    ctype = "text/xml"
                    fname = "dump.xml"
                elif self.options["format"] == "cups" :
                    ctype = "text/plain"
                    fname = "page_log"
                print "Content-type: %s" % ctype    
                print "Content-disposition: attachment; filename=%s" % fname 
                print
                try :
                    self.main(self.arguments, self.options, restricted=0)
                except PyKotaToolError, msg :    
                    print msg
            else :        
                self.guiDisplay()
            
if __name__ == "__main__" :
    os.environ["LC_ALL"] = getLanguagePreference()
    admin = PyKotaDumperGUI(lang=os.environ["LC_ALL"], charset=getCharsetPreference())
    admin.form = cgi.FieldStorage()
    admin.options = { "output" : "-",
                "data" : "history",
                "format" : "cups",
              }
    admin.arguments = []
    admin.guiAction()
    try :
        admin.storage.close()
    except (TypeError, NameError, AttributeError) :    
        pass
        
    sys.exit(0)
