#! /usr/bin/python

# PyKota Print Quota Reports generator
#
# PyKota - Print Quotas for CUPS and LPRng
#
# (c) 2003-2004 Jerome Alet <alet@librelogiciel.com>
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
# Revision 1.24  2004/01/12 14:52:03  jalet
# Cuts the date string
#
# Revision 1.23  2004/01/12 14:35:01  jalet
# Printing history added to CGI script.
#
# Revision 1.22  2004/01/09 07:58:53  jalet
# Changed URL to PyKota's logo
#
# Revision 1.21  2004/01/08 14:10:32  jalet
# Copyright year changed.
#
# Revision 1.20  2004/01/07 16:07:17  jalet
# The stylesheet is again expected to be local, it was a bad idea to use
# the one on my server.
#
# Revision 1.19  2004/01/06 16:05:45  jalet
# Will now search the stylesheet on my own website.
#
# Revision 1.18  2003/12/27 16:49:25  uid67467
# Should be ok now.
#
# Revision 1.16  2003/12/02 14:40:20  jalet
# Some code refactoring.
# New HTML reporter added, which is now used in the CGI script for web based
# print quota reports. It will need some de-uglyfication though...
#
# Revision 1.15  2003/10/24 22:06:42  jalet
# Initial support for browser's language preference added.
#
# Revision 1.14  2003/10/10 19:48:07  jalet
# Now displays version number
#
# Revision 1.13  2003/08/25 11:23:05  jalet
# More powerful CGI script for quota reports
#
# Revision 1.12  2003/07/29 20:55:17  jalet
# 1.14 is out !
#
# Revision 1.11  2003/07/01 12:37:31  jalet
# Nicer UI
#
# Revision 1.10  2003/07/01 07:30:32  jalet
# Message changed.
#
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
import urllib

from pykota import version
from pykota.tool import PyKotaTool, PyKotaToolError
from pykota.reporter import PyKotaReporterError, openReporter

header = """Content-type: text/html

<?xml version="1.0" encoding="iso-8859-1"?>
<html>
  <head>
    <title>PyKota Reports</title>
    <link rel="stylesheet" type="text/css" href="/pykota.css" />
  </head>
  <body>
    <form action="printquota.cgi" method="POST">
      <table>
        <tr>
          <td>
            <p>
              <a href="http://www.librelogiciel.com/software/"><img src="http://www.librelogiciel.com/software/PyKota/pykota.png" alt="PyKota's Logo" /></a>
              <br />
              <a href="http://www.librelogiciel.com/software/">PyKota version %s</a>
            </p>
          </td>
          <td colspan="2">
            <h1>PyKota Reports</h1>
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

def getLanguagePreference() :
    """Returns the preferred language."""
    languages = os.environ.get("HTTP_ACCEPT_LANGUAGE", "")
    langs = [l.strip().split(';')[0] for l in languages.split(",")]
    return "%s_%s" % (langs[0], langs[0].upper())

class PyKotaReportGUI(PyKotaTool) :
    """PyKota Administrative GUI"""
        
    def guiDisplay(self) :
        """Displays the administrative interface."""
        global header, footer
        print header % version.__version__
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
        message = '<table><tr><td valign="top">Printer :</td><td valign="top"><select name="printers" multiple="multiple">'
        for printer in printers :
            if printer.Name in selectednames :
                message += '<option value="%s" selected="selected">%s</option>' % (printer.Name, printer.Name)
            else :
                message += '<option value="%s">%s</option>' % (printer.Name, printer.Name)
        message += '</select></td></tr></table>'
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
        self.body = "<p>Please click on the button above</p>\n"
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
                remuser = os.environ.get("REMOTE_USER", "root")    
                if remuser == "root" :
                    if self.form.has_key("ugmask") :     
                        ugmask = self.form["ugmask"].value
                    else :     
                        ugmask = "*"
                else :        
                    if self.form.has_key("isgroup") :    
                        user = self.storage.getUser(remuser)
                        if user.Exists :
                            ugmask = " ".join([ g.Name for g in self.storage.getUserGroups(user) ])
                        else :    
                            ugmask = remuser # result will probably be empty, we don't care
                    else :    
                        ugmask = remuser
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
        if not self.form.has_key("history") :
            if printers and ugmask :
                self.reportingtool = openReporter(admin, "html", printers, ugmask.split(), isgroup)
                self.body += "%s" % self.reportingtool.generateReport()
        else :        
            remuser = os.environ.get("REMOTE_USER", "root")    
            if remuser != "root" :
                username = remuser
            elif self.form.has_key("username") :    
                username = self.form["username"].value
            else :    
                username = None
            if username is not None :    
                user = self.storage.getUser(username)
            else :    
                user =None
            if self.form.has_key("printername") :
                printer = self.storage.getPrinter(self.form["printername"].value)
            else :    
                printer = None
            if self.form.has_key("datelimit") :    
                datelimit = self.form["datelimit"].value
            else :    
                datelimit = None
            self.report = ["<h2>History</h2>"]    
            history = self.storage.retrieveHistory(user, printer, datelimit)
            if not history :
                self.report.append("<h3>Empty</h3>")
            else :
                self.report.append('<table class="pykotatable" border="1">')
                headers = ["Date", "User", "Printer", "PageCounter", "JobId", "JobSize", "JobPrice", "Copies", "Title", "Filename", "Options", "Action"]
                self.report.append('<tr class="pykotacolsheader">%s</tr>' % "".join(["<th>%s</th>" % h for h in headers]))
                oddeven = 0
                for job in history :
                    oddeven += 1
                    if oddeven % 2 :
                        oddevenclass = "odd"
                    else :    
                        oddevenclass = "even"
                    if job.JobAction == "DENY" :
                        oddevenclass = "deny"
                    elif job.JobAction == "WARN" :    
                        oddevenclass = "warn"
                    self.report.append('<tr class="%s">%s</tr>' % (oddevenclass, "".join(["<td>%s</td>" % h for h in (job.JobDate[:19], job.User.Name, job.Printer.Name, job.PrinterPageCounter, job.JobId, job.JobSize, job.JobPrice, job.JobCopies, job.JobTitle, job.JobFileName, job.JobOptions, job.JobAction)])))
                self.report.append('</table>')
                dico = { "history" : 1,
                         "datelimit" : job.JobDate,
                       }
                if user and user.Exists :
                    dico.update({ "username" : user.Name })
                if printer and printer.Exists :
                    dico.update({ "printername" : printer.Name })
                prevurl = "%s?%s" % (os.environ.get("SCRIPT_NAME", ""), urllib.urlencode(dico))
                self.report.append('<a href="%s">Previous page</a>' % prevurl)
            self.body = "\n".join(self.report)    
            
if __name__ == "__main__" :
    os.environ["LC_ALL"] = getLanguagePreference()
    admin = PyKotaReportGUI(lang=os.environ["LC_ALL"])
    admin.form = cgi.FieldStorage()
    admin.guiAction()
    admin.guiDisplay()
    try :
        admin.storage.close()
    except (TypeError, NameError, AttributeError) :    
        pass
        
    sys.exit(0)
