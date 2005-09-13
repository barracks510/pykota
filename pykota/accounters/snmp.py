# PyKota
# -*- coding: ISO-8859-15 -*-
#
# PyKota - Print Quotas for CUPS and LPRng
#
# (c) 2003, 2004, 2005 Jerome Alet <alet@librelogiciel.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# $Id$
#
#

ITERATIONDELAY = 1.5   # 1.5 Second
STABILIZATIONDELAY = 3 # We must read three times the same value to consider it to be stable

import sys
import os
import time
import select

try :
    from pysnmp.asn1.encoding.ber.error import TypeMismatchError
    from pysnmp.mapping.udp.error import SnmpOverUdpError
    from pysnmp.mapping.udp.role import Manager
    from pysnmp.proto.api import alpha
except ImportError :
    class Handler :
        def __init__(self, parent, printerhostname) :
            """Just there to raise an exception."""
            raise RuntimeError, "The pysnmp module is not available. Download it from http://pysnmp.sf.net/"
else :    
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
    class Handler :
        """A class for SNMP print accounting."""
        def __init__(self, parent, printerhostname) :
            self.parent = parent
            self.printerHostname = printerhostname
            try :
                self.community = self.parent.arguments.split(":")[1].strip()
            except IndexError :    
                self.community = "public"
            self.port = 161
            self.printerInternalPageCounter = None
            self.printerStatus = None
            self.deviceStatus = None
            
        def retrieveSNMPValues(self) :    
            """Retrieves a printer's internal page counter and status via SNMP."""
            ver = alpha.protoVersions[alpha.protoVersionId1]
            req = ver.Message()
            req.apiAlphaSetCommunity(self.community)
            req.apiAlphaSetPdu(ver.GetRequestPdu())
            req.apiAlphaGetPdu().apiAlphaSetVarBindList((pageCounterOID, ver.Null()), \
                                                        (hrPrinterStatusOID, ver.Null()), \
                                                        (hrDeviceStatusOID, ver.Null()))
            tsp = Manager()
            try :
                tsp.sendAndReceive(req.berEncode(), \
                                   (self.printerHostname, self.port), \
                                   (self.handleAnswer, req))
            except (SnmpOverUdpError, select.error), msg :    
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
                            self.deviceStatus = self.values[2]
                            self.parent.filter.logdebug("SNMP answer is decoded : PageCounter : %s  PrinterStatus : %s  DeviceStatus : %s" % tuple(self.values))
                        except IndexError :    
                            self.parent.filter.logdebug("SNMP answer is incomplete : %s" % str(self.values))
                            pass
                        else :    
                            return 1
                        
        def waitPrinting(self) :
            """Waits for printer status being 'printing'."""
            firstvalue = None
            while 1:
                self.retrieveSNMPValues()
                statusAsString = printerStatusValues.get(self.printerStatus)
                if statusAsString in ('printing', 'warmup') :
                    break
                if self.printerInternalPageCounter is not None :    
                    if firstvalue is None :
                        # first time we retrieved a page counter, save it
                        firstvalue = self.printerInternalPageCounter
                    else :     
                        # second time (or later)
                        if firstvalue < self.printerInternalPageCounter :
                            # Here we have a printer which lies :
                            # it says it is not printing or warming up
                            # BUT the page counter increases !!!
                            # So we can probably quit being sure it is printing.
                            self.parent.filter.printInfo("Printer %s is lying to us !!!" % self.parent.filter.PrinterName, "warn")
                            break
                self.parent.filter.logdebug(_("Waiting for printer %s to be printing...") % self.parent.filter.PrinterName)    
                time.sleep(ITERATIONDELAY)
            
        def waitIdle(self) :
            """Waits for printer status being 'idle'."""
            idle_num = idle_flag = 0
            while 1 :
                self.retrieveSNMPValues()
                pstatusAsString = printerStatusValues.get(self.printerStatus)
                dstatusAsString = deviceStatusValues.get(self.deviceStatus)
                idle_flag = 0
                if (pstatusAsString == 'idle') or \
                   ((pstatusAsString == 'other') and \
                    (dstatusAsString == 'running')) :
                    idle_flag = 1       # Standby / Powersave is considered idle
                if idle_flag :    
                    idle_num += 1
                    if idle_num >= STABILIZATIONDELAY :
                        # printer status is stable, we can exit
                        break
                else :    
                    idle_num = 0
                self.parent.filter.logdebug(_("Waiting for printer %s's idle status to stabilize...") % self.parent.filter.PrinterName)    
                time.sleep(ITERATIONDELAY)
                
        def retrieveInternalPageCounter(self) :
            """Returns the page counter from the printer via internal SNMP handling."""
            try :
                if (os.environ.get("PYKOTASTATUS") != "CANCELLED") and \
                   (os.environ.get("PYKOTAACTION") != "DENY") and \
                   (os.environ.get("PYKOTAPHASE") == "AFTER") and \
                   self.parent.filter.JobSizeBytes :
                    self.waitPrinting()
                self.waitIdle()    
            except :    
                if self.printerInternalPageCounter is None :
                    raise
                else :    
                    self.parent.filter.printInfo(_("SNMP querying stage interrupted. Using latest value seen for internal page counter (%s) on printer %s.") % (self.printerInternalPageCounter, self.parent.filter.PrinterName), "warn")
            return self.printerInternalPageCounter
            
if __name__ == "__main__" :            
    if len(sys.argv) != 2 :    
        sys.stderr.write("Usage :  python  %s  printer_ip_address\n" % sys.argv[0])
    else :    
        def _(msg) :
            return msg
            
        class fakeFilter :
            def __init__(self) :
                self.PrinterName = "FakePrintQueue"
                self.JobSizeBytes = 1
                
            def printInfo(self, msg, level="info") :
                sys.stderr.write("%s : %s\n" % (level.upper(), msg))
                sys.stderr.flush()
                
            def logdebug(self, msg) :    
                self.printInfo(msg, "debug")
                
        class fakeAccounter :        
            def __init__(self) :
                self.arguments = "snmp:public"
                self.filter = fakeFilter()
                self.protocolHandler = Handler(self, sys.argv[1])
            
        acc = fakeAccounter()            
        print "Internal page counter's value is : %s" % acc.protocolHandler.retrieveInternalPageCounter()
