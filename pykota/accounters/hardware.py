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
# Revision 1.35  2005/01/12 22:44:06  jalet
# Tried to fix a problem with printers which are slow to pass into printing mode.
#
# Revision 1.34  2004/11/19 11:57:51  jalet
# Modified the SNMP fix as hinted by pysnmp's maintainer
#
# Revision 1.33  2004/11/19 10:35:37  jalet
# Catches TypeMismatchError in SNMP answer handling code
#
# Revision 1.32  2004/11/16 23:23:40  jalet
# Fixed internal PJL handling wrt the 35078 PowerSave mode.
#
# Revision 1.31  2004/11/01 14:32:26  jalet
# Fix for unneeded out of band status in pjl_over_tcp/9100
#
# Revision 1.30  2004/10/05 09:21:34  jalet
# Removed misleading comments
#
# Revision 1.29  2004/10/05 09:20:07  jalet
# Reduced delay from 2 to 1 seconds in internal SNMP and PJL_over_TCP
# handlers
#
# Revision 1.28  2004/09/27 20:09:30  jalet
# Lowered timeout delay for PJL queries
#
# Revision 1.27  2004/09/27 20:00:35  jalet
# Typo
#
# Revision 1.26  2004/09/27 19:56:27  jalet
# Added internal handling for PJL queries over port tcp/9100. Now waits
# for printer being idle before asking, just like with SNMP.
#
# Revision 1.25  2004/09/27 09:21:37  jalet
# Now includes printer's hostname in SNMP error messages
#
# Revision 1.24  2004/09/24 21:19:48  jalet
# Did a pass of PyChecker
#
# Revision 1.23  2004/09/23 19:18:12  jalet
# Now loops when the external hardware accounter fails, until it returns a correct value
#
# Revision 1.22  2004/09/22 19:48:01  jalet
# Logs the looping message as debug instead of as info
#
# Revision 1.21  2004/09/22 19:27:41  jalet
# Bad import statement
#
# Revision 1.20  2004/09/22 19:22:27  jalet
# Just loop in case a network error occur
#
# Revision 1.19  2004/09/22 14:29:01  jalet
# Fixed nasty typo
#
# Revision 1.18  2004/09/21 16:00:46  jalet
# More informational messages
#
# Revision 1.17  2004/09/21 13:42:18  jalet
# Typo
#
# Revision 1.16  2004/09/21 13:30:53  jalet
# First try at full SNMP handling from the Python code.
#
# Revision 1.15  2004/09/14 11:38:59  jalet
# Minor fix
#
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

import os
import socket
import time
import signal
import popen2

from pykota.accounter import AccounterBase, PyKotaAccounterError

ITERATIONDELAY = 1.0   # 1 Second
STABILIZATIONDELAY = 3 # We must read three times the same value to consider it to be stable

try :
    from pysnmp.asn1.encoding.ber.error import TypeMismatchError
    from pysnmp.mapping.udp.error import SnmpOverUdpError
    from pysnmp.mapping.udp.role import Manager
    from pysnmp.proto.api import alpha
except ImportError :
    hasSNMP = 0
else :    
    hasSNMP = 1
    pageCounterOID = ".1.3.6.1.2.1.43.10.2.1.4.1.1"
    hrPrinterStatusOID = ".1.3.6.1.2.1.25.3.5.1.1.1"
    printerStatusValues = { 1 : 'other',
                            2 : 'unknown',
                            3 : 'idle',
                            4 : 'printing',
                            5 : 'warmup',
                          }
                          
    class SNMPAccounter :
        """A class for SNMP print accounting."""
        def __init__(self, parent, printerhostname) :
            self.parent = parent
            self.printerHostname = printerhostname
            self.printerInternalPageCounter = self.printerStatus = None
            
        def retrieveSNMPValues(self) :    
            """Retrieves a printer's internal page counter and status via SNMP."""
            ver = alpha.protoVersions[alpha.protoVersionId1]
            req = ver.Message()
            req.apiAlphaSetCommunity('public')
            req.apiAlphaSetPdu(ver.GetRequestPdu())
            req.apiAlphaGetPdu().apiAlphaSetVarBindList((pageCounterOID, ver.Null()), (hrPrinterStatusOID, ver.Null()))
            tsp = Manager()
            try :
                tsp.sendAndReceive(req.berEncode(), (self.printerHostname, 161), (self.handleAnswer, req))
            except SnmpOverUdpError, msg :    
                self.parent.filter.printInfo(_("Network error while doing SNMP queries on printer %s : %s") % (self.printerHostname, msg), "warn")
            tsp.close()
    
        def handleAnswer(self, wholeMsg, notusedhere, req):
            """Decodes and handles the SNMP answer."""
            self.parent.filter.logdebug("SNMP message : '%s'" % repr(wholeMsg))
            ver = alpha.protoVersions[alpha.protoVersionId1]
            rsp = ver.Message()
            try :
                rsp.berDecode(wholeMsg)
            except TypeMismatchError, msg :    
                self.parent.filter.printInfo(_("SNMP message decoding error for printer %s : %s") % (self.printerHostname, msg), "warn")
            else :
                if req.apiAlphaMatch(rsp):
                    errorStatus = rsp.apiAlphaGetPdu().apiAlphaGetErrorStatus()
                    if errorStatus:
                        self.parent.filter.printInfo(_("Problem encountered while doing SNMP queries on printer %s : %s") % (self.printerHostname, errorStatus), "warn")
                    else:
                        self.values = []
                        for varBind in rsp.apiAlphaGetPdu().apiAlphaGetVarBindList():
                            self.values.append(varBind.apiAlphaGetOidVal()[1].rawAsn1Value)
                        try :    
                            # keep maximum value seen for printer's internal page counter
                            self.printerInternalPageCounter = max(self.printerInternalPageCounter, self.values[0])
                            self.printerStatus = self.values[1]
                        except IndexError :    
                            pass
                        else :    
                            return 1
                        
        def waitPrinting(self) :
            """Waits for printer status being 'printing'."""
            while 1:
                self.retrieveSNMPValues()
                statusAsString = printerStatusValues.get(self.printerStatus)
                if statusAsString in ('printing',) :
                    break
                self.parent.filter.logdebug(_("Waiting for printer %s to be printing...") % self.parent.filter.printername)    
                time.sleep(ITERATIONDELAY)
            
        def waitIdle(self) :
            """Waits for printer status being 'idle'."""
            idle_num = idle_flag = 0
            while 1 :
                self.retrieveSNMPValues()
                statusAsString = printerStatusValues.get(self.printerStatus)
                idle_flag = 0
                if statusAsString in ('idle',) :
                    idle_flag = 1
                if idle_flag :    
                    idle_num += 1
                    if idle_num > STABILIZATIONDELAY :
                        # printer status is stable, we can exit
                        break
                else :    
                    idle_num = 0
                self.parent.filter.logdebug(_("Waiting for printer %s's idle status to stabilize...") % self.parent.filter.printername)    
                time.sleep(ITERATIONDELAY)
                
pjlMessage = "\033%-12345X@PJL USTATUSOFF\r\n@PJL INFO STATUS\r\n@PJL INFO PAGECOUNT\r\n\033%-12345X"
pjlStatusValues = {
                    "10000" : "Powersave Mode",
                    "10001" : "Ready Online",
                    "10002" : "Ready Offline",
                    "10003" : "Warming Up",
                    "10004" : "Self Test",
                    "10005" : "Reset",
                    "10023" : "Printing",
                    "35078" : "Powersave Mode",         # 10000 is ALSO powersave !!!
                  }
class PJLAccounter :
    """A class for PJL print accounting."""
    def __init__(self, parent, printerhostname) :
        self.parent = parent
        self.printerHostname = printerhostname
        self.printerInternalPageCounter = self.printerStatus = None
        self.printerInternalPageCounter = self.printerStatus = None
        self.timedout = 0
        
    def alarmHandler(self, signum, frame) :    
        """Query has timedout, handle this."""
        self.timedout = 1
        raise IOError, "Waiting for PJL answer timed out. Please try again later."
        
    def retrievePJLValues(self) :    
        """Retrieves a printer's internal page counter and status via PJL."""
        port = 9100
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try :
            sock.connect((self.printerHostname, port))
        except socket.error, msg :
            self.parent.filter.printInfo(_("Problem during connection to %s:%s : %s") % (self.printerHostname, port, msg), "warn")
        else :
            try :
                sock.send(pjlMessage)
            except socket.error, msg :
                self.parent.filter.printInfo(_("Problem while sending PJL query to %s:%s : %s") % (self.printerHostname, port, msg), "warn")
            else :    
                actualpagecount = self.printerStatus = None
                self.timedout = 0
                while (self.timedout == 0) or (actualpagecount is None) or (self.printerStatus is None) :
                    signal.signal(signal.SIGALRM, self.alarmHandler)
                    signal.alarm(3)
                    try :
                        answer = sock.recv(1024)
                    except IOError, msg :    
                        break   # our alarm handler was launched, probably
                    else :    
                        readnext = 0
                        for line in [l.strip() for l in answer.split()] : 
                            if line.startswith("CODE=") :
                                self.printerStatus = line.split("=")[1]
                            elif line.startswith("PAGECOUNT") :    
                                readnext = 1 # page counter is on next line
                            elif readnext :    
                                actualpagecount = int(line.strip())
                                readnext = 0
                    signal.alarm(0)
                self.printerInternalPageCounter = max(actualpagecount, self.printerInternalPageCounter)
        sock.close()
        
    def waitPrinting(self) :
        """Waits for printer status being 'printing'."""
        while 1:
            self.retrievePJLValues()
            if self.printerStatus in ('10023',) :
                break
            self.parent.filter.logdebug(_("Waiting for printer %s to be printing...") % self.parent.filter.printername)
            time.sleep(ITERATIONDELAY)
        
    def waitIdle(self) :
        """Waits for printer status being 'idle'."""
        idle_num = idle_flag = 0
        while 1 :
            self.retrievePJLValues()
            idle_flag = 0
            if self.printerStatus in ('10000', '10001', '35078') :
                idle_flag = 1
            if idle_flag :    
                idle_num += 1
                if idle_num > STABILIZATIONDELAY :
                    # printer status is stable, we can exit
                    break
            else :    
                idle_num = 0
            self.parent.filter.logdebug(_("Waiting for printer %s's idle status to stabilize...") % self.parent.filter.printername)
            time.sleep(ITERATIONDELAY)
    
class Accounter(AccounterBase) :
    def __init__(self, kotabackend, arguments) :
        """Initializes querying accounter."""
        AccounterBase.__init__(self, kotabackend, arguments)
        self.isSoftware = 0
        
    def getPrinterInternalPageCounter(self) :    
        """Returns the printer's internal page counter."""
        self.filter.logdebug("Reading printer %s's internal page counter..." % self.filter.printername)
        counter = self.askPrinterPageCounter(self.filter.printerhostname)
        self.filter.logdebug("Printer %s's internal page counter value is : %s" % (self.filter.printername, str(counter)))
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
                if (not self.counterbefore) or (not self.counterafter) or (self.counterbefore == self.counterafter) :
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
        cmdlower = commandline.lower()
        if cmdlower == "snmp" :
            if hasSNMP :
                return self.askWithSNMP(printer)
            else :    
                raise PyKotaAccounterError, _("Internal SNMP accounting asked, but Python-SNMP is not available. Please download it from http://pysnmp.sourceforge.net")
        elif cmdlower == "pjl" :
            return self.askWithPJL(printer)
            
        if printer is None :
            raise PyKotaAccounterError, _("Unknown printer address in HARDWARE(%s) for printer %s") % (commandline, self.filter.printername)
        while 1 :    
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
            else :        
                return pagecounter        
        
    def askWithSNMP(self, printer) :
        """Returns the page counter from the printer via internal SNMP handling."""
        acc = SNMPAccounter(self, printer)
        try :
            if (os.environ.get("PYKOTASTATUS") != "CANCELLED") and \
               (os.environ.get("PYKOTAACTION") != "DENY") and \
               (os.environ.get("PYKOTAPHASE") == "AFTER") and \
               self.filter.jobSizeBytes :
                acc.waitPrinting()
            acc.waitIdle()    
        except :    
            if acc.printerInternalPageCounter is None :
                raise
            else :    
                self.filter.printInfo(_("SNMP querying stage interrupted. Using latest value seen for internal page counter (%s) on printer %s.") % (acc.printerInternalPageCounter, self.filter.printername), "warn")
        return acc.printerInternalPageCounter
        
    def askWithPJL(self, printer) :
        """Returns the page counter from the printer via internal PJL handling."""
        acc = PJLAccounter(self, printer)
        try :
            if (os.environ.get("PYKOTASTATUS") != "CANCELLED") and \
               (os.environ.get("PYKOTAACTION") != "DENY") and \
               (os.environ.get("PYKOTAPHASE") == "AFTER") and \
               self.filter.jobSizeBytes :
                acc.waitPrinting()
            acc.waitIdle()    
        except :    
            if acc.printerInternalPageCounter is None :
                raise
            else :    
                self.filter.printInfo(_("PJL querying stage interrupted. Using latest value seen for internal page counter (%s) on printer %s.") % (acc.printerInternalPageCounter, self.filter.printername), "warn")
        return acc.printerInternalPageCounter
