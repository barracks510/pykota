# PyKota
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
# Revision 1.1  2003/05/07 19:47:06  jalet
# v1.07 Release of the Shame is out !
#
#
#

import sys
import os
import popen2
import tempfile
from pykota.accounter import AccounterBase, PyKotaAccounterError

class Accounter(AccounterBase) :
    def doAccounting(self, printerid, userid) :
        """Deletgates the computation of the job size to an external command.
        
           The command must print the job size on its standard output and exit successfully.
        """
        # get the job size    
        jobsize = self.getJobSize()
            
        # get last job information for this printer
        pgc = self.filter.storage.getPrinterPageCounter(printerid)    
        if pgc is None :
            # The printer hasn't been used yet, from PyKota's point of view
            counterbeforejob = 0
        else :    
            # get last job size and page counter from Quota Storage
            # Last lifetime page counter before actual job is 
            # last page counter + last job size
            counterbeforejob = (pgc["pagecounter"] or 0) + (pgc["jobsize"] or 0)
            
        # Is the current user allowed to print at all ?
        action = self.filter.warnUserPQuota(self.filter.username, self.filter.printername)
        
        # update the quota for the current user on this printer, if allowed to print
        if action == "DENY" :
            jobsize = 0
        else :    
            self.filter.storage.updateUserPQuota(userid, printerid, jobsize)
        
        # adds the current job to history    
        self.filter.storage.addJobToHistory(self.filter.jobid, self.filter.storage.getUserId(self.filter.username), printerid, counterbeforejob, action, jobsize)
            
        return action
        
    def getJobSize(self) :    
        """Feeds an external command with our datas to let it compute the job size, and return its value."""
        temporary = None    
        if self.filter.inputfile is None :    
            infile = sys.stdin
            # we will have to duplicate our standard input
            temporary = tempfile.TemporaryFile()
        else :    
            infile = open(self.filter.inputfile, "rb")
            
        # launches external accounter
        process = popen2.Popen3("%s" % self.arguments)
        
        # feed it with our data
        data = infile.read(256*1024)    
        while data :
            process.tochild.write(data)
            temporary.write(data)
            data = infile.read(256*1024)
        process.tochild.close()
        
        # wait for child process to exit (or die)
        retcode = process.wait()
        
        # check exit status
        if os.WIFEXITED(retcode) and not os.WEXITSTATUS(retcode) :
            # tries to extract the job size from the external accounter's
            # standard output
            try :
                pagecount = int(process.fromchild.readline().strip())
            except (AttributeError, ValueError) :
                self.filter.logger.log_message(_("Unable to compute job size with external accounter %s") % self.arguments)
                pagecount = 0
        else :
            self.filter.logger.log_message(_("Unable to compute job size with external accounter %s") % self.arguments)
            pagecount = 0
        process.fromchild.close()    
            
        if temporary is not None :    
            # this is a copy of our previous standard input
            # flush, then rewind
            temporary.flush()
            temporary.seek(0, 0)
            # our temporary file will be used later if the
            # job is allowed.
            self.filter.inputfile = temporary
        else :
            infile.close()
            
        return pagecount    
            
