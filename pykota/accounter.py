# PyKota
# -*- coding: ISO-8859-15 -*-
#
# PyKota : Print Quotas for CUPS and LPRng
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
# Revision 1.10  2004/01/08 14:10:32  jalet
# Copyright year changed.
#
# Revision 1.9  2003/12/27 16:49:25  uid67467
# Should be ok now.
#
# Revision 1.7  2003/11/25 23:46:40  jalet
# Don't try to verify if module name is valid, Python does this better than us.
#
# Revision 1.6  2003/11/12 23:28:55  jalet
# More work on new backend. This commit may be unstable.
#
# Revision 1.5  2003/10/07 09:07:28  jalet
# Character encoding added to please latest version of Python
#
# Revision 1.4  2003/07/14 14:14:59  jalet
# Old template
#
# Revision 1.3  2003/04/30 19:53:58  jalet
# 1.05
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

class PyKotaAccounterError(Exception):
    """An exception for Accounter related stuff."""
    def __init__(self, message = ""):
        self.message = message
        Exception.__init__(self, message)
    def __repr__(self):
        return self.message
    __str__ = __repr__
    
class AccounterBase :    
    """A class to account print usage by querying printers."""
    def __init__(self, kotafilter, arguments) :
        """Sets instance vars depending on the current printer."""
        self.filter = kotafilter
        self.arguments = arguments
        
    def getLastPageCounter(self) :    
        """Returns last internal page counter value (possibly faked)."""
        try :
            return self.LastPageCounter
        except :    
            return 0
        
    def filterInput(self, inputfile) :
        """Transparent filter."""
        mustclose = 0    
        if inputfile is not None :    
            if hasattr(inputfile, "read") :
                infile = inputfile
            else :    
                infile = open(inputfile, "rb")
            mustclose = 1
        else :    
            infile = sys.stdin
        data = infile.read(256*1024)    
        while data :
            sys.stdout.write(data)
            data = infile.read(256*1024)
        if mustclose :    
            infile.close()
            
    def beginJob(self, printer, user) :    
        """Saves the computed job size."""
        # computes job's size
        self.JobSize = self.computeJobSize()
        
        # get last job information for this printer
        if not printer.LastJob.Exists :
            # The printer hasn't been used yet, from PyKota's point of view
            self.LastPageCounter = 0
        else :    
            # get last job size and page counter from Quota Storage
            # Last lifetime page counter before actual job is 
            # last page counter + last job size
            self.LastPageCounter = int(printer.LastJob.PrinterPageCounter or 0) + int(printer.LastJob.JobSize or 0)
        
    def endJob(self, printer, user) :    
        """Do nothing."""
        pass
        
    def getJobSize(self) :    
        """Returns the actual job size."""
        try :
            return self.JobSize
        except AttributeError :    
            return 0
        
    def doAccounting(self, printer, user) :
        """Deletgates the computation of the job size to an external command.
        
           The command must print the job size on its standard output and exit successfully.
        """
        self.beginJob(printer, user)
        
        # get the job size, which is real job size * number of copies.
        jobsize = self.getJobSize() * self.filter.copies
            
        # Is the current user allowed to print at all ?
        userpquota = self.filter.storage.getUserPQuota(user, printer)
        action = self.filter.warnUserPQuota(userpquota)
        
        # update the quota for the current user on this printer, if allowed to print
        if action == "DENY" :
            jobsize = 0
        else :    
            userpquota.increasePagesUsage(jobsize)
        
        # adds the current job to history    
        jobprice = (float(printer.PricePerPage or 0.0) * jobsize) + float(printer.PricePerJob or 0.0)
        printer.addJobToHistory(self.filter.jobid, user, self.getLastPageCounter(), action, jobsize, jobprice, self.filter.preserveinputfile, self.filter.title, self.filter.copies, self.filter.options)
        self.endJob(printer, user)
        return action
        
    def computeJobSize(self) :    
        """Must be overriden in children classes."""
        raise RuntimeError, "AccounterBase.computeJobSize() must be overriden !"
        
        
def openAccounter(kotafilter) :
    """Returns a connection handle to the appropriate accounter."""
    (backend, args) = kotafilter.config.getAccounterBackend(kotafilter.printername)
    try :
        exec "from pykota.accounters import %s as accounterbackend" % backend.lower()
    except ImportError :
        raise PyKotaAccounterError, _("Unsupported accounter backend %s") % backend
    else :    
        return accounterbackend.Accounter(kotafilter, args)
