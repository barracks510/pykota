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
# Revision 1.7  2003/02/06 14:28:59  jalet
# edpykota should be ok, minus some typos
#
# Revision 1.6  2003/02/06 09:19:02  jalet
# More robust behavior (hopefully) when the user or printer is not managed
# correctly by the Quota System : e.g. cupsFilter added in ppd file, but
# printer and/or user not 'yet?' in storage.
#
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
    def getMatchingPrinters(self, printerpattern) :
        """Returns the list of all printer names which match a certain pattern."""
        printerslist = []
        # We 'could' do a SELECT printername FROM printers WHERE printername LIKE ...
        # but we don't because other storages semantics may be different, so every
        # storage should use fnmatch to match patterns and be storage agnostic
        result = self.doQuery("SELECT printername FROM printers;")
        result = self.doParseResult()
        if result is not None :
            for printer in result :
                if fnmatch.fnmatchcase(printer["printername"], printerpattern) :
                    printerslist.append(printer["printername"])
        return printerslist        
            
    def getUserId(self, username) :
        """Returns a userid given a username."""
        result = self.doQuery("SELECT id FROM users WHERE username=%s;" % self.doQuote(username))
        try :
            return self.doParseResult(result)[0]["id"]
        except TypeError :      # Not found
            return
            
    def getPrinterId(self, printername) :        
        """Returns a printerid given a printername."""
        result = self.doQuery("SELECT id FROM printers WHERE printername=%s;" % self.doQuote(printername))
        try :
            return self.doParseResult(result)[0]["id"]
        except TypeError :      # Not found    
            return
            
    def getPrinterPageCounter(self, printername) :
        """Returns the last page counter value for a printer given its name."""
        result = self.doQuery("SELECT pagecounter, lastusername FROM printers WHERE printername=%s;" % self.doQuote(printername))
        try :
            return self.doParseResult(result)[0]
        except TypeError :      # Not found
            return
        
    def updatePrinterPageCounter(self, printername, username, pagecount) :
        """Updates the last page counter information for a printer given its name, last username and pagecount."""
        return self.doQuery("UPDATE printers SET pagecounter=%s, lastusername=%s WHERE printername=%s;" % (self.doQuote(pagecount), self.doQuote(username), self.doQuote(printername)))
        
    def addUserPQuota(self, username, printername) :
        (userid, printerid) = self.getUPIds(username, printername)
        if printerid is None :    
            self.doQuery("INSERT INTO printers (printername) VALUES (%s);" % self.doQuote(printername))
        if userid is None :    
            self.doQuery("INSERT INTO users (username) VALUES (%s);" % self.doQuote(username))
        (userid, printerid) = self.getUPIds(username, printername)
        if (userid is not None) and (printerid is not None) :
            return self.doQuery("INSERT INTO userpquota (userid, printerid) VALUES (%s, %s);" % (self.doQuote(userid), self.doQuote(printerid)))
        
    def getUPIds(self, username, printername) :    
        """Returns a tuple (userid, printerid) given a username and a printername."""
        return (self.getUserId(username), self.getPrinterId(printername))
        
    def getUserPQuota(self, username, printername) :
        """Returns the Print Quota information for a given (username, printername)."""
        (userid, printerid) = self.getUPIds(username, printername)
        if (userid is not None) and (printerid is not None) :
            result = self.doQuery("SELECT pagecounter, softlimit, hardlimit, datelimit FROM userpquota WHERE userid=%s AND printerid=%s;" % (self.doQuote(userid), self.doQuote(printerid)))
            try :
                return self.doParseResult(result)[0]
            except TypeError :      # Not found    
                pass
        
    def setUserPQuota(self, username, printername, softlimit, hardlimit) :
        """Sets soft and hard limits for a user quota on a specific printer given (username, printername)."""
        (userid, printerid) = self.getUPIds(username, printername)
        if (userid is not None) and (printerid is not None) :
            self.doQuery("UPDATE userpquota SET softlimit=%s, hardlimit=%s, datelimit=NULL WHERE userid=%s AND printerid=%s;" % (self.doQuote(softlimit), self.doQuote(hardlimit), self.doQuote(userid), self.doQuote(printerid)))
        
    def updateUserPQuota(self, username, printername, pagecount) :
        """Updates the used user Quota information given (username, printername) and a job size in pages."""
        (userid, printerid) = self.getUPIds(username, printername)
        if (userid is not None) and (printerid is not None) :
            self.doQuery("UPDATE userpquota SET pagecounter=pagecounter+(%s) WHERE userid=%s AND printerid=%s;" % (self.doQuote(pagecount), self.doQuote(userid), self.doQuote(printerid)))
        
    def buyUserPQuota(self, username, printername, pagebought) :
        """Buys pages for a given (username, printername)."""
        self.updateUserPQuota(username, printername, -pagebought)
        
