# PyKota
# -*- coding: ISO-8859-15 -*-
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
# Revision 1.13  2004/04/09 22:24:47  jalet
# Began work on correct handling of child processes when jobs are cancelled by
# the user. Especially important when an external requester is running for a
# long time.
#
# Revision 1.12  2004/01/11 23:22:42  jalet
# Major code refactoring, it's way cleaner, and now allows automated addition
# of printers on first print.
#
# Revision 1.11  2004/01/08 14:10:32  jalet
# Copyright year changed.
#
# Revision 1.10  2003/12/27 16:49:25  uid67467
# Should be ok now.
#
# Revision 1.8  2003/11/21 14:28:46  jalet
# More complete job history.
#
# Revision 1.7  2003/11/12 23:29:24  jalet
# More work on new backend. This commit may be unstable.
#
# Revision 1.6  2003/10/07 09:07:29  jalet
# Character encoding added to please latest version of Python
#
# Revision 1.5  2003/07/07 11:49:24  jalet
# Lots of small fixes with the help of PyChecker
#
# Revision 1.4  2003/06/25 14:10:01  jalet
# Hey, it may work (edpykota --reset excepted) !
#
# Revision 1.3  2003/05/06 14:55:47  jalet
# Missing import !
#
# Revision 1.2  2003/04/30 13:36:40  jalet
# Stupid accounting method was added.
#
# Revision 1.1  2003/04/29 18:37:54  jalet
# Pluggable accounting methods (actually doesn't support external scripts)
#
#
#

import sys
import os
import time
from pykota.accounter import AccounterBase, PyKotaAccounterError
from pykota.requester import openRequester, PyKotaRequesterError

MAXTRIES = 12    # maximum number of tries to get the printer's internal page counter
TIMETOSLEEP = 10 # number of seconds to sleep between two tries to get the printer's internal page counter

class Accounter(AccounterBase) :
    def __init__(self, kotabackend, arguments) :
        """Initializes querying accounter."""
        AccounterBase.__init__(self, kotabackend, arguments)
        self.requester = openRequester(kotabackend, kotabackend.printername)
        self.isDelayed = 1 # With the pykota filter, accounting is delayed by one job
        
    def getPrinterInternalPageCounter(self) :    
        """Returns the printer's internal page counter."""
        global MAXTRIES, TIMETOSLEEP
        self.filter.logdebug("Reading printer's internal page counter...")
        for dummy in range(MAXTRIES) :
            try :
                counter = self.requester.getPrinterPageCounter(self.filter.printerhostname)
            except PyKotaRequesterError, msg :
                # can't get actual page counter, assume printer is off or warming up
                # log the message anyway.
                self.filter.logger.log_message("%s" % msg, "warn")
                counter = None
            else :    
                # printer answered, it is on so we can exit the loop
                break
            time.sleep(TIMETOSLEEP)    
        self.filter.logdebug("Printer's internal page counter value is : %s" % str(counter))
        return counter    
        
    def beginJob(self, userpquota) :    
        """Saves printer internal page counter at start of job."""
        # save page counter before job
        self.LastPageCounter = self.counterbefore = self.getPrinterInternalPageCounter()
        
    def endJob(self, userpquota) :    
        """Saves printer internal page counter at end of job."""
        # save page counter after job
        self.LastPageCounter = self.counterafter = self.getPrinterInternalPageCounter()
        
    def getJobSize(self) :    
        """Returns the actual job size."""
        try :
            jobsize = (self.counterafter - self.counterbefore)    
            if jobsize < 0 :
                # Try to take care of HP printers 
                # Their internal page counter is saved to NVRAM
                # only every 10 pages. If the printer was switched
                # off then back on during the job, and that the
                # counters difference is negative, we know 
                # the formula (we can't know if more than eleven
                # pages were printed though) :
                if jobsize > -10 :
                    jobsize += 10
                else :    
                    # here we may have got a printer being replaced
                    # DURING the job. This is HIGHLY improbable !
                    jobsize = 0
        except :    
            # takes care of the case where one counter (or both) was never set.
            jobsize = 0
        return jobsize
        
    def doAccounting(self, userpquota) :
        """Does print accounting and returns if the job status is ALLOW or DENY."""
        # Get the page counter directly from the printer itself
        counterbeforejob = self.getPrinterInternalPageCounter() or 0
        
        # Is the current user allowed to print at all ?
        action = self.filter.warnUserPQuota(userpquota)
        
        # adds the current job to history    
        userpquota.Printer.addJobToHistory(self.filter.jobid, userpquota.User, counterbeforejob, action, filename=self.filter.preserveinputfile, title=self.filter.title, copies=self.filter.copies, options=self.filter.options)
        return action
            
