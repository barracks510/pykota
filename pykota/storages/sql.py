# PyKota
#
# PyKota : Print Quotas for CUPS
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
# Revision 1.5  2003/02/05 23:26:22  jalet
# Incorrect handling of grace delay
#
# Revision 1.4  2003/02/05 23:02:10  jalet
# Typo
#
# Revision 1.3  2003/02/05 23:00:12  jalet
# Forgotten import
# Bad datetime conversion
#
# Revision 1.2  2003/02/05 22:28:38  jalet
# More robust storage
#
# Revision 1.1  2003/02/05 21:28:17  jalet
# Initial import into CVS
#
#
#

class SQLStorage :    
    def getUserId(self, username) :
        result = self.doQuery("SELECT id FROM users WHERE username=%s;" % self.doQuote(username))
        try :
            return self.doParseResult(result)[0]["id"]
        except TypeError :      # Not found
            return
            
    def getPrinterId(self, printername) :        
        result = self.doQuery("SELECT id FROM printers WHERE printername=%s;" % self.doQuote(printername))
        try :
            return self.doParseResult(result)[0]["id"]
        except TypeError :      # Not found    
            return
            
    def getPrinterPageCounter(self, printername) :
        result = self.doQuery("SELECT pagecounter, lastusername FROM printers WHERE printername=%s;" % self.doQuote(printername))
        try :
            return self.doParseResult(result)[0]
        except TypeError :      # Not found
            return
        
    def updatePrinterPageCounter(self, printername, username, pagecount) :
        return self.doQuery("UPDATE printers SET pagecounter=%s, lastusername=%s WHERE printername=%s;" % (self.doQuote(pagecount), self.doQuote(username), self.doQuote(printername)))
        
    def addUserPQuota(self, username, printername) :
        printerid = self.getPrinterId(printername)
        if printerid is None :    
            self.doQuery("INSERT INTO printers (printername) VALUES (%s);" % self.doQuote(printername))
            printerid = self.getPrinterId(printername)
        userid = self.getUserId(username)
        if userid is None :    
            self.doQuery("INSERT INTO users (username) VALUES (%s);" % self.doQuote(username))
            userid = self.getUserId(username)
        if (printerid is not None) and (userid is not None) :    
            return self.doQuery("INSERT INTO userpquota (userid, printerid) VALUES (%s, %s);" % (self.doQuote(userid), self.doQuote(printerid)))
        
    def getUserPQuota(self, username, printername) :
        result = self.doQuery("SELECT pagecounter, softlimit, hardlimit, datelimit FROM userpquota WHERE userid=%s AND printerid=%s;" % (self.doQuote(self.getUserId(username)), self.doQuote(self.getPrinterId(printername))))
        try :
            return self.doParseResult(result)[0]
        except TypeError :      # Not found    
            return
        
    def setUserPQuota(self, username, printername, softlimit, hardlimit) :
        self.doQuery("UPDATE userpquota SET softlimit=%s, hardlimit=%s, datelimit=NULL WHERE userid=%s AND printerid=%s;" % (self.doQuote(softlimit), self.doQuote(hardlimit), self.doQuote(self.getUserId(username)), self.doQuote(self.getPrinterId(printername))))
        
    def updateUserPQuota(self, username, printername, pagecount) :
        self.doQuery("UPDATE userpquota SET pagecounter=pagecounter+(%s) WHERE userid=%s AND printerid=%s;" % (self.doQuote(pagecount), self.doQuote(self.getUserId(username)), self.doQuote(self.getPrinterId(printername))))
        
    def buyUserPQuota(self, username, printername, pagebought) :
        self.updateUserPQuota(username, printername, -pagebought)
        
