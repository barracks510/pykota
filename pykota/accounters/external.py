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
# Revision 1.6  2003/09/04 07:57:18  jalet
# Problem with Python 2.3 fixed : a bug of me.
#
# Revision 1.5  2003/07/07 11:49:24  jalet
# Lots of small fixes with the help of PyChecker
#
# Revision 1.4  2003/06/25 14:10:01  jalet
# Hey, it may work (edpykota --reset excepted) !
#
# Revision 1.3  2003/05/27 23:00:21  jalet
# Big rewrite of external accounting methods.
# Should work well now.
#
# Revision 1.2  2003/05/13 13:54:20  jalet
# Better handling of broken pipes
#
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
    def doAccounting(self, printer, user) :
        """Deletgates the computation of the job size to an external command.
        
           The command must print the job size on its standard output and exit successfully.
        """
        # get the job size, which is real job size * number of copies.
        jobsize = self.getJobSize() * self.filter.copies
            
        # get last job information for this printer
        if not printer.LastJob.Exists :
            # The printer hasn't been used yet, from PyKota's point of view
            counterbeforejob = 0
        else :    
            # get last job size and page counter from Quota Storage
            # Last lifetime page counter before actual job is 
            # last page counter + last job size
            counterbeforejob = int(printer.LastJob.PrinterPageCounter or 0) + int(printer.LastJob.JobSize or 0)
            
        # Is the current user allowed to print at all ?
        userpquota = self.filter.storage.getUserPQuota(user, printer)
        action = self.filter.warnUserPQuota(userpquota)
        
        # update the quota for the current user on this printer, if allowed to print
        if action == "DENY" :
            jobsize = 0
        else :    
            userpquota.increasePagesUsage(jobsize)
        
        # adds the current job to history    
        printer.addJobToHistory(self.filter.jobid, user, counterbeforejob, action, jobsize)
            
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
        # TODO : USE tempfile.mkstemp() instead ! Needs some work !
        infilename = tempfile.mktemp()
        outfilename = tempfile.mktemp()
        errfilename = tempfile.mktemp()
        
        try :
            # feed it with our data
            fakeinput = open(infilename, "wb")
            data = infile.read(256*1024)    
            while data :
                fakeinput.write(data)
                if temporary is not None :
                    temporary.write(data)
                data = infile.read(256*1024)
            fakeinput.close()
        
            # launches child process
            command = "%s <%s >%s 2>%s" % (self.arguments, infilename, outfilename, errfilename)
            retcode = os.system(command)
            
            # check exit status
            if (os.WIFEXITED(retcode) and not os.WEXITSTATUS(retcode)) or os.stat(errfilename) :
                # tries to extract the job size from the external accounter's
                # standard output
                childoutput = open(outfilename, "r")
                try :
                    pagecount = int(childoutput.readline().strip())
                except (AttributeError, ValueError) :
                    self.filter.logger.log_message(_("Unable to compute job size with external accounter %s") % self.arguments)
                    pagecount = 0
                childoutput.close()    
            else :
                self.filter.logger.log_message(_("Unable to compute job size with external accounter %s") % self.arguments)
                pagecount = 0
            os.remove(infilename)
            os.remove(outfilename)
            os.remove(errfilename)
        except IOError, msg :    
            # TODO : temporary files may remain on the filesystem...
            msg = "%s : %s" % (self.arguments, msg) 
            self.filter.logger.log_message(_("Unable to compute job size with external accounter %s") % msg)
            pagecount = 0
            
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
            
