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
    pageCounterOID = ".1.3.6.1.2.1.43.10.2.1.4.1.1"  # SNMPv2-SMI::mib-2.43.10.2.1.4.1.1
    hrPrinterStatusOID = ".1.3.6.1.2.1.25.3.5.1.1.1" # SNMPv2-SMI::mib-2.25.3.5.1.1.1
    printerStatusValues = { 1 : 'other',
                            2 : 'unknown',
                            3 : 'idle',
                            4 : 'printing',
                            5 : 'warmup',
                          }
    hrDeviceStatusOID = ".1.3.6.1.2.1.25.3.2.1.5.1" # SNMPv2-SMI::mib-2.25.3.2.1.5.1
    deviceStatusValues = { 1 : 'unknown',
                           2 : 'running',
                           3 : 'warning',
                           4 : 'testing',
                           5 : 'down',
                         }  
    hrPrinterDetectedErrorStateOID = ".1.3.6.1.2.1.25.3.5.1.2.1" # SNMPv2-SMI::mib-2.25.3.5.1.2.1
    prtConsoleDisplayBufferTextOID = ".1.3.6.1.2.1.43.16.5.1.2.1.1" # SNMPv2-SMI::mib-2.43.16.5.1.2.1.1
                          
    #                      
    # Documentation taken from RFC 3805 (Printer MIB v2) and RFC 2790 (Host Resource MIB)
    #
    # TODO : if hrDeviceStatus==2 and hrPrinterStatus==1 then it's powersave mode.
    #
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
            req.apiAlphaGetPdu().apiAlphaSetVarBindList((pageCounterOID, ver.Null()), \
                                                        (hrPrinterStatusOID, ver.Null()))
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
                            self.parent.filter.logdebug("SNMP answer is decoded : PageCounter : %s     Status : %s" % (self.values[0], self.values[1]))
                        except IndexError :    
                            self.parent.filter.logdebug("SNMP answer is incomplete : %s" % str(self.values))
                            pass
                        else :    
                            return 1
                        
        def waitPrinting(self) :
            """Waits for printer status being 'printing'."""
            while 1:
                self.retrieveSNMPValues()
                statusAsString = printerStatusValues.get(self.printerStatus)
                if statusAsString in ('printing', 'warmup') :
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
