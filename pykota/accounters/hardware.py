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
# Revision 1.14  2004/09/14 06:53:53  jalet
# Small test added
#
# Revision 1.13  2004/09/13 16:02:45  jalet
# Added fix for incorrect job's size when hardware accounting fails
#
# Revision 1.12  2004/09/06 15:42:34  jalet
# Fix missing import statement for the signal module
#
# Revision 1.11  2004/08/31 23:29:53  jalet
# Introduction of the new 'onaccountererror' configuration directive.
# Small fix for software accounter's return code which can't be None anymore.
# Make software and hardware accounting code look similar : will be factorized
# later.
#
# Revision 1.10  2004/08/27 22:49:04  jalet
# No answer from subprocess now is really a fatal error. Waiting for some
# time to make this configurable...
#
# Revision 1.9  2004/08/25 22:34:39  jalet
# Now both software and hardware accounting raise an exception when no valid
# result can be extracted from the subprocess' output.
# Hardware accounting now reads subprocess' output until an integer is read
# or data is exhausted : it now behaves just like software accounting in this
# aspect.
#
# Revision 1.8  2004/07/22 22:41:48  jalet
# Hardware accounting for LPRng should be OK now. UNTESTED.
#
# Revision 1.7  2004/07/16 12:22:47  jalet
# LPRng support early version
#
# Revision 1.6  2004/07/01 19:56:42  jalet
# Better dispatching of error messages
#
# Revision 1.5  2004/06/10 22:42:06  jalet
# Better messages in logs
#
# Revision 1.4  2004/05/24 22:45:49  jalet
# New 'enforcement' directive added
# Polling loop improvements
#
# Revision 1.3  2004/05/24 14:36:40  jalet
# Revert to old polling loop. Will need optimisations
#
# Revision 1.2  2004/05/18 14:49:22  jalet
# Big code changes to completely remove the need for "requester" directives,
# jsut use "hardware(... your previous requester directive's content ...)"
#
# Revision 1.1  2004/05/13 13:59:30  jalet
# Code simplifications
#
#
#

import sys
import os
import signal
import popen2
from pykota.accounter import AccounterBase, PyKotaAccounterError

class Accounter(AccounterBase) :
    def __init__(self, kotabackend, arguments) :
        """Initializes querying accounter."""
        AccounterBase.__init__(self, kotabackend, arguments)
        self.isSoftware = 0
        
    def getPrinterInternalPageCounter(self) :    
        """Returns the printer's internal page counter."""
        self.filter.logdebug("Reading printer's internal page counter...")
        counter = self.askPrinterPageCounter(self.filter.printerhostname)
        self.filter.logdebug("Printer's internal page counter value is : %s" % str(counter))
        return counter    
        
    def beginJob(self, printer) :    
        """Saves printer internal page counter at start of job."""
        # save page counter before job
        self.LastPageCounter = self.getPrinterInternalPageCounter()
        self.fakeBeginJob()
        
    def fakeBeginJob(self) :    
        """Fakes a begining of a job."""
        self.counterbefore = self.getLastPageCounter()
        
    def endJob(self, printer) :    
        """Saves printer internal page counter at end of job."""
        # save page counter after job
        self.LastPageCounter = self.counterafter = self.getPrinterInternalPageCounter()
        
    def getJobSize(self, printer) :    
        """Returns the actual job size."""
        if (not self.counterbefore) or (not self.counterafter) :
            # there was a problem retrieving page counter
            self.filter.printInfo(_("A problem occured while reading printer %s's internal page counter.") % printer.Name, "warn")
            if printer.LastJob.Exists :
                # if there's a previous job, use the last value from database
                self.filter.printInfo(_("Retrieving printer %s's page counter from database instead.") % printer.Name, "warn")
                if not self.counterbefore : 
                    self.counterbefore = printer.LastJob.PrinterPageCounter or 0
                if not self.counterafter :
                    self.counterafter = printer.LastJob.PrinterPageCounter or 0
                before = min(self.counterbefore, self.counterafter)    
                after = max(self.counterbefore, self.counterafter)    
                self.counterbefore = before
                self.counterafter = after
                if (not self.counterbefore) or (self.counterbefore == self.counterafter) :
                    self.filter.printInfo(_("Couldn't retrieve printer %s's internal page counter either before or after printing.") % printer.Name, "warn")
                    self.filter.printInfo(_("Job's size forced to 1 page for printer %s.") % printer.Name, "warn")
                    self.counterbefore = 0
                    self.counterafter = 1
            else :
                self.filter.printInfo(_("No previous job in database for printer %s.") % printer.Name, "warn")
                self.filter.printInfo(_("Job's size forced to 1 page for printer %s.") % printer.Name, "warn")
                self.counterbefore = 0
                self.counterafter = 1
                
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
                self.filter.printInfo(_("Inconsistent values for printer %s's internal page counter.") % printer.Name, "warn")
                self.filter.printInfo(_("Job's size forced to 1 page for printer %s.") % printer.Name, "warn")
                jobsize = 1
        return jobsize
        
    def askPrinterPageCounter(self, printer) :
        """Returns the page counter from the printer via an external command.
        
           The external command must report the life time page number of the printer on stdout.
        """
        commandline = self.arguments.strip() % locals()
        if printer is None :
            raise PyKotaAccounterError, _("Unknown printer address in HARDWARE(%s) for printer %s") % (commandline, self.filter.printername)
        self.filter.printInfo(_("Launching HARDWARE(%s)...") % commandline)
        pagecounter = None
        child = popen2.Popen4(commandline)    
        try :
            answer = child.fromchild.read()
        except IOError :    
            # we were interrupted by a signal, certainely a SIGTERM
            # caused by the user cancelling the current job
            try :
                os.kill(child.pid, signal.SIGTERM)
            except :    
                pass # already killed ?
            self.filter.printInfo(_("SIGTERM was sent to hardware accounter %s (pid: %s)") % (commandline, child.pid))
        else :    
            lines = [l.strip() for l in answer.split("\n")]
            for i in range(len(lines)) : 
                try :
                    pagecounter = int(lines[i])
                except (AttributeError, ValueError) :
                    self.filter.printInfo(_("Line [%s] skipped in accounter's output. Trying again...") % lines[i])
                else :    
                    break
        child.fromchild.close()    
        child.tochild.close()
        try :
            status = child.wait()
        except OSError, msg :    
            self.filter.logdebug("Error while waiting for hardware accounter pid %s : %s" % (child.pid, msg))
        else :    
            if os.WIFEXITED(status) :
                status = os.WEXITSTATUS(status)
            self.filter.printInfo(_("Hardware accounter %s exit code is %s") % (self.arguments, str(status)))
            
        if pagecounter is None :
            message = _("Unable to query printer %s via HARDWARE(%s)") % (printer, commandline)
            if self.onerror == "CONTINUE" :
                self.filter.printInfo(message, "error")
            else :
                raise PyKotaAccounterError, message 
        return pagecounter        
