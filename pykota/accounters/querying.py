# PyKota
# -*- coding: ISO-8859-15 -*-
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
        self.requester = openRequester(kotabackend.config, kotabackend.printername)
        
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
        
    def beginJob(self, printer, user) :    
        """Saves printer internal page counter at start of job."""
        # save page counter before job
        self.LastPageCounter = self.counterbefore = self.getPrinterInternalPageCounter()
        
    def endJob(self, printer, user) :    
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
        
    def doAccounting(self, printer, user) :
        """Does print accounting and returns if the job status is ALLOW or DENY."""
        # Get the page counter directly from the printer itself
        # Tries MAXTRIES times, sleeping two seconds each time, in case the printer is sleeping.
        # This was seen with my Apple LaserWriter 16/600 PS which doesn't answer before having warmed up.
        counterbeforejob = self.getPrinterInternalPageCounter()
        
        # get last job information for this printer
        if not printer.LastJob.Exists :
            # The printer hasn't been used yet, from PyKota's point of view
            lastuser = user
            lastpagecounter = counterbeforejob
        else :    
            # get last values from Quota Storage
            lastuser = printer.LastJob.User
            lastpagecounter = printer.LastJob.PrinterPageCounter
            
        # if printer is off then we assume the correct counter value is the last one
        if counterbeforejob is None :
            counterbeforejob = lastpagecounter
            
        # if the internal lifetime page counter for this printer is 0    
        # then this may be a printer with a volatile counter (never
        # saved to NVRAM) which has just been switched off and then on
        # so we use the last page counter from the Quota Storage instead
        # explanation at : http://web.mit.edu/source/third/lprng/doc/LPRng-HOWTO-15.html
        if counterbeforejob == 0 :
            counterbeforejob = lastpagecounter
            
        # Computes the last job size as the difference between internal page
        # counter in the printer and last page counter taken from the Quota
        # Storage database for this particular printer
        try :
            jobsize = (counterbeforejob - lastpagecounter)    
        except TypeError :    
            # never used, and internal page counter not accessible
            jobsize = 0
            
        if jobsize < 0 :
            # Probably an HP printer which was switched off and back on, 
            # its primary counter is only saved in a 10 increment, so
            # it may be lower than the last page counter saved in the
            # Quota Storage. 
            # We unconditionnally set the last job's size to 
            # abs(int((10 - abs(lastcounter(snmp) - lastcounter(storage)) / 2))
            # For more accurate accounting, don't switch off your HP printers !
            # explanation at : http://web.mit.edu/source/third/lprng/doc/LPRng-HOWTO-15.html
            self.filter.logger.log_message(_("Error in page count value %i for user %s on printer %s") % (jobsize, lastuser.Name, self.filter.printername), "error")
            jobsize = abs(int((10 - abs(jobsize)) / 2))     # Workaround for HP printers' feature !
            
        # update the quota for the previous user on this printer 
        lastuserquota = self.filter.storage.getUserPQuota(lastuser, printer)
        if lastuserquota.Exists :
            lastuserquota.increasePagesUsage(jobsize)
        
        # update the last job size in the history
        if printer.LastJob.Exists :
            printer.LastJob.setSize(jobsize)
        
        # warns the last user if he is over quota
        if lastuserquota.Exists :
            self.filter.warnUserPQuota(lastuserquota)
            
        # Is the current user allowed to print at all ?
        action = self.filter.warnUserPQuota(self.filter.storage.getUserPQuota(user, printer))
        
        # adds the current job to history    
        printer.addJobToHistory(self.filter.jobid, user, counterbeforejob, action, filename=self.filter.preserveinputfile, title=self.filter.title, copies=self.filter.copies, options=self.filter.options)
        return action
            
