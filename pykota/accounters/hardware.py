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
# Revision 1.1  2004/05/13 13:59:30  jalet
# Code simplifications
#
#
#

import sys
import os
from pykota.accounter import AccounterBase, PyKotaAccounterError
from pykota.requester import openRequester, PyKotaRequesterError

class Accounter(AccounterBase) :
    def __init__(self, kotabackend, arguments) :
        """Initializes querying accounter."""
        AccounterBase.__init__(self, kotabackend, arguments)
        self.requester = openRequester(kotabackend, kotabackend.printername)
        self.isDelayed = 1 # With the pykota filter, accounting is delayed by one job
        
    def getPrinterInternalPageCounter(self) :    
        """Returns the printer's internal page counter."""
        self.filter.logdebug("Reading printer's internal page counter...")
        try :
            counter = self.requester.getPrinterPageCounter(self.filter.printerhostname)
        except PyKotaRequesterError, msg :
            # can't get actual page counter, assume printer is off or warming up
            # log the message anyway.
            self.filter.logger.log_message("%s" % msg, "warn")
            counter = None
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
            
