#! /usr/bin/env python

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
# Revision 1.1  2003/02/05 21:28:17  jalet
# Initial import into CVS
#
#
#

import sys
import os
import smtplib

from pykota import config
from pykota import storage
from pykota import logger

class PyKotaToolError(Exception):
    """An exception for PyKota config related stuff."""
    def __init__(self, message = ""):
        self.message = message
        Exception.__init__(self, message)
    def __repr__(self):
        return self.message
    __str__ = __repr__
    
class PyKotaTool :    
    """Base class for all PyKota command line tools."""
    def __init__(self, isfilter=0) :
        """Initializes the command line tool."""
        self.config = config.PyKotaConfig(os.environ.get("CUPS_SERVERROOT", "/etc/cups"))
        self.logger = logger.Logger(self.config)
        self.storage = storage.openConnection(self.config, asadmin=(not isfilter))
        self.printername = os.environ.get("PRINTER", None)
        self.printerhostname = self.getPrinterHostname()
        self.smtpserver = self.config.getSMTPServer()
        self.admin = self.config.getAdmin()
        self.adminmail = self.config.getAdminMail()
        
    def sendMessage(self, touser, fullmessage) :
        """Sends an email message containing headers to some user."""
        fullmessage += "\n\nPlease contact your system administrator %s - <%s>\n" % (self.admin, self.adminmail)
        if "@" not in touser :
            touser = "%s@%s" % (touser, self.smtpserver)
        server = smtplib.SMTP(self.smtpserver)
        server.sendmail(self.adminmail, [touser], fullmessage)
        server.quit()
        
    def sendMessageToUser(self, username, subject, message) :
        """Sends an email message to a user."""
        self.sendMessage(username, "Subject: %s\n\n%s" % (subject, message))
        
    def sendMessageToAdmin(self, subject, message) :
        """Sends an email message to the Print Quota administrator."""
        self.sendMessage(self.adminmail, "Subject: %s\n\n%s" % (subject, message))
        
    def getPrinterHostname(self) :
        """Returns the printer hostname."""
        device_uri = os.environ.get("DEVICE_URI", "")
        # TODO : check this for more complex urls than ipp://myprinter.dot.com:631/printers/lp
        try :
            (backend, destination) = device_uri.split(":", 1) 
        except ValueError :    
            raise PyKotaToolError, "Invalid DEVICE_URI : %s\n" % device_uri
        while destination.startswith("/") :
            destination = destination[1:]
        return destination.split("/")[0].split(":")[0]
        
    def warnQuotaPrinter(self, username) :
        """Checks a user quota and send him a message if quota is exceeded on current printer."""
        (action, grace, gracedate) = self.storage.checkUserPQuota(username, self.printername)
        if action == "DENY" :
            adminmessage = "Print Quota exceeded for user %s on printer %s" % (username, self.printername)
            self.logger.log_message(adminmessage)
            self.sendMessageToUser(username, "Print Quota Exceeded", "You are not allowed to print anymore because your Print Quota is exceeded.")
            self.sendMessageToAdmin("Print Quota", adminmessage)
        elif action == "WARN" :    
            adminmessage = "Print Quota soft limit exceeded for user %s on printer %s" % (username, self.printername)
            self.logger.log_message(adminmessage)
            self.sendMessageToUser(username, "Print Quota Exceeded", "You will soon be forbidden to print anymore because your Print Quota is almost reached.")
            self.sendMessageToAdmin("Print Quota", adminmessage)
        return action        
    
