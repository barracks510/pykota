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
# Revision 1.1  2003/02/05 21:28:17  jalet
# Initial import into CVS
#
#
#

from mx import DateTime

class SQLStorage :    
    def getUserId(self, username) :
        result = self.doQuery("SELECT id FROM users WHERE username=%s;" % self.doQuote(username))
        return self.doParseResult(result)["id"]
            
    def getPrinterId(self, printername) :        
        result = self.doQuery("SELECT id FROM printers WHERE printername=%s;" % self.doQuote(printername))
        return self.doParseResult(result)["id"]
            
    def getPrinterPageCounter(self, printername) :
        result = self.doQuery("SELECT pagecounter, lastusername FROM printers WHERE printername=%s;" % self.doQuote(printername))
        return self.doParseResult(result)
        
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
        return self.doParseResult(result)
        
    def setUserPQuota(self, username, printername, softlimit, hardlimit) :
        self.doQuery("UPDATE userpquota SET softlimit=%s, hardlimit=%s, datelimit=NULL WHERE userid=%s AND printerid=%s;" % (self.doQuote(softlimit), self.doQuote(hardlimit), self.doQuote(self.getUserId(username)), self.doQuote(self.getPrinterId(printername))))
        
    def updateUserPQuota(self, username, printername, pagecount) :
        self.doQuery("UPDATE userpquota SET pagecounter=pagecounter+(%s) WHERE userid=%s AND printerid=%s;" % (self.doQuote(pagecount), self.doQuote(self.getUserId(username)), self.doQuote(self.getPrinterId(printername))))
        
    def buyUserPQuota(self, username, printername, pagebought) :
        self.updateUserPQuota(username, printername, -pagebought)
        
    def checkUserPQuota(self, username, printername) :
        # TODO : this doesn't work as expected wrt dates
        # TODO : GRACEDELAY should come from the configuration file
        # TODO : move this into the PyKotaTool class
        now = DateTime.now()
        quota = self.getUserPQuota(username, printername)
        pagecounter = quota["pagecounter"]
        softlimit = quota["softlimit"]
        hardlimit = quota["hardlimit"]
        datelimit = quota["datelimit"]
        if datelimit :
            datelimit = DateTime.DateTime(datelimit)    # TODO : check this !
        if softlimit is not None :
            if pagecounter < softlimit :
                action = "ALLOW"
            elif hardlimit is not None :
                 if softlimit <= pagecounter < hardlimit :    
                     if datelimit is None :
                         self.doQuery("UPDATE userpquota SET datelimit=%s WHERE userid=%s AND printerid=%s;" % ('%04i-%02i-%02i' % (now.year, now.month, now.day), self.doQuote(self.getUserId(username)), self.doQuote(self.getPrinterId(printername))))
                         datelimit = now
                     if (now - datelimit) <= GRACEDELAY :
                         action = "WARN"
                     else :    
                         action = "DENY"
                 else :         
                     action = "DENY"
            else :        
                action = "DENY"
        else :        
            action = "ALLOW"
        return (action, (hardlimit - pagecounter), datelimit)
    
