# -*- coding: utf-8 -*-
#
# PyKota : Print Quotas for CUPS
#
# (c) 2003-2013 Jerome Alet <alet@librelogiciel.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# $Id$
#
#

"""This module is used to extract printer's internal page counter
and status informations using SNMP queries.

The values extracted are defined at least in RFC3805 and RFC2970.
"""


import sys
import os
import time
import select
import socket

try :
    from pysnmp.entity.rfc3413.oneliner import cmdgen
except ImportError :
    raise RuntimeError, "The pysnmp v4.x module is not available. Download it from http://pysnmp.sf.net/\nPyKota doesn't support earlier releases anymore."

from pykota import constants

#
# Documentation taken from RFC 3805 (Printer MIB v2) and RFC 2790 (Host Resource MIB)
#
pageCounterOID = "1.3.6.1.2.1.43.10.2.1.4.1.1"  # SNMPv2-SMI::mib-2.43.10.2.1.4.1.1
hrPrinterStatusOID = "1.3.6.1.2.1.25.3.5.1.1.1" # SNMPv2-SMI::mib-2.25.3.5.1.1.1
printerStatusValues = { 1 : 'other',
                        2 : 'unknown',
                        3 : 'idle',
                        4 : 'printing',
                        5 : 'warmup',
                      }
hrDeviceStatusOID = "1.3.6.1.2.1.25.3.2.1.5.1" # SNMPv2-SMI::mib-2.25.3.2.1.5.1
deviceStatusValues = { 1 : 'unknown',
                       2 : 'running',
                       3 : 'warning',
                       4 : 'testing',
                       5 : 'down',
                     }
hrPrinterDetectedErrorStateOID = "1.3.6.1.2.1.25.3.5.1.2.1" # SNMPv2-SMI::mib-2.25.3.5.1.2.1
printerDetectedErrorStateValues = [ { 128 : 'Low Paper',
                                       64 : 'No Paper',
                                       32 : 'Low Toner',
                                       16 : 'No Toner',
                                        8 : 'Door Open',
                                        4 : 'Jammed',
                                        2 : 'Offline',
                                        1 : 'Service Requested',
                                    },
                                    { 128 : 'Input Tray Missing',
                                       64 : 'Output Tray Missing',
                                       32 : 'Marker Supply Missing',
                                       16 : 'Output Near Full',
                                        8 : 'Output Full',
                                        4 : 'Input Tray Empty',
                                        2 : 'Overdue Preventive Maintainance',
                                        1 : 'Not Assigned in RFC3805',
                                    },
                                  ]

# The default error mask to use when checking error conditions.
defaultErrorMask = 0x4fcc # [ 'No Paper',
                          #   'Door Open',
                          #   'Jammed',
                          #   'Offline',
                          #   'Service Requested',
                          #   'Input Tray Missing',
                          #   'Output Tray Missing',
                          #   'Output Full',
                          #   'Input Tray Empty',
                          # ]

# WARNING : some printers don't support this one :
prtConsoleDisplayBufferTextOID = "1.3.6.1.2.1.43.16.5.1.2.1.1" # SNMPv2-SMI::mib-2.43.16.5.1.2.1.1
class BaseHandler :
    """A class for SNMP print accounting."""
    def __init__(self, parent, printerhostname, skipinitialwait=False) :
        self.parent = parent
        self.printerHostname = printerhostname
        self.skipinitialwait = skipinitialwait
        try :
            self.community = self.parent.arguments.split(":")[1].strip()
        except IndexError :
            self.community = "public"
        self.port = 161
        self.initValues()

    def initValues(self) :
        """Initializes SNMP values."""
        self.printerInternalPageCounter = None
        self.printerStatus = None
        self.deviceStatus = None
        self.printerDetectedErrorState = None
        self.timebefore = time.time()   # resets timer also in case of error

    def retrieveSNMPValues(self) :
        """Retrieves a printer's internal page counter and status via SNMP."""
        raise RuntimeError, "You have to overload this method."

    def extractErrorStates(self, value) :
        """Returns a list of textual error states from a binary value."""
        states = []
        for i in range(min(len(value), len(printerDetectedErrorStateValues))) :
            byte = ord(value[i])
            bytedescription = printerDetectedErrorStateValues[i]
            for (k, v) in bytedescription.items() :
                if byte & k :
                    states.append(v)
        return states

    def checkIfError(self, errorstates) :
        """Checks if any error state is fatal or not."""
        if errorstates is None :
            return True
        else :
            try :
                errormask = self.parent.filter.config.getPrinterSNMPErrorMask(self.parent.filter.PrinterName)
            except AttributeError : # debug mode
                errormask = defaultErrorMask
            if errormask is None :
                errormask = defaultErrorMask
            errormaskbytes = [ chr((errormask & 0xff00) >> 8),
                               chr((errormask & 0x00ff)),
                             ]
            errorConditions = self.extractErrorStates(errormaskbytes)
            self.parent.filter.logdebug("Error conditions for mask 0x%04x : %s" \
                                               % (errormask, errorConditions))
            for err in errorstates :
                if err in errorConditions :
                    self.parent.filter.logdebug("Error condition '%s' encountered. PyKota will wait until this problem is fixed." % err)
                    return True
            self.parent.filter.logdebug("No error condition matching mask 0x%04x" % errormask)
            return False

    def waitPrinting(self) :
        """Waits for printer status being 'printing'."""
        statusstabilizationdelay = constants.get(self.parent.filter, "StatusStabilizationDelay")
        noprintingmaxdelay = constants.get(self.parent.filter, "NoPrintingMaxDelay")
        if not noprintingmaxdelay :
            self.parent.filter.logdebug("Will wait indefinitely until printer %s is in 'printing' state." % self.parent.filter.PrinterName)
        else :
            self.parent.filter.logdebug("Will wait until printer %s is in 'printing' state or %i seconds have elapsed." % (self.parent.filter.PrinterName, noprintingmaxdelay))
        previousValue = self.parent.getLastPageCounter()
        firstvalue = None
        increment = 1
        waitdelay = statusstabilizationdelay * increment
        while True :
            self.retrieveSNMPValues()
            error = self.checkIfError(self.printerDetectedErrorState)
            pstatusAsString = printerStatusValues.get(self.printerStatus)
            dstatusAsString = deviceStatusValues.get(self.deviceStatus)
            if pstatusAsString in ('printing', 'warmup') :
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
                    elif noprintingmaxdelay \
                         and ((time.time() - self.timebefore) > noprintingmaxdelay) \
                         and not error :
                        # More than X seconds without the printer being in 'printing' mode
                        # We can safely assume this won't change if printer is now 'idle'
                        if (pstatusAsString == 'idle') or \
                            ((pstatusAsString == 'other') and \
                             (dstatusAsString in ('running', 'warning'))) :
                            if self.printerInternalPageCounter == previousValue :
                                # Here the job won't be printed, because probably
                                # the printer rejected it for some reason.
                                self.parent.filter.printInfo("Printer %s probably won't print this job !!!" % self.parent.filter.PrinterName, "warn")
                            else :
                                # Here the job has already been entirely printed, and
                                # the printer has already passed from 'idle' to 'printing' to 'idle' again.
                                self.parent.filter.printInfo("Printer %s has probably already printed this job !!!" % self.parent.filter.PrinterName, "warn")
                            break
                    if error or (dstatusAsString == "down") :
                        if waitdelay < constants.FIVEMINUTES :
                            increment *= 2
                    else :
                        increment = 1
            self.parent.filter.logdebug("Waiting %s seconds for printer %s to be printing..." % (waitdelay,
                                                                                                 self.parent.filter.PrinterName))
            time.sleep(waitdelay)
            waitdelay = statusstabilizationdelay * increment

    def waitIdle(self) :
        """Waits for printer status being 'idle'."""
        statusstabilizationdelay = constants.get(self.parent.filter, "StatusStabilizationDelay")
        statusstabilizationloops = constants.get(self.parent.filter, "StatusStabilizationLoops")
        increment = 1
        waitdelay = statusstabilizationdelay * increment
        idle_num = 0
        while True :
            self.retrieveSNMPValues()
            error = self.checkIfError(self.printerDetectedErrorState)
            pstatusAsString = printerStatusValues.get(self.printerStatus)
            dstatusAsString = deviceStatusValues.get(self.deviceStatus)
            idle_flag = False
            if (not error) and ((pstatusAsString == 'idle') or \
                                    ((pstatusAsString == 'other') and \
                                         (dstatusAsString in ('running', 'warning')))) :
                idle_flag = True # Standby / Powersave is considered idle
                increment = 1 # Reset initial stabilization delay
            if idle_flag :
                if (self.printerInternalPageCounter is not None) \
                   and self.skipinitialwait \
                   and (os.environ.get("PYKOTAPHASE") == "BEFORE") :
                    self.parent.filter.logdebug("No need to wait for the printer to be idle, it is the case already.")
                    return
                idle_num += 1
                if idle_num >= statusstabilizationloops :
                    # printer status is stable, we can exit
                    break
            else :
                idle_num = 0
            if error or (dstatusAsString == "down") :
                if waitdelay < constants.FIVEMINUTES :
                    increment *= 2
            else :
                increment = 1
            self.parent.filter.logdebug("Waiting %s seconds for printer %s's idle status to stabilize..." % (waitdelay,
                                                                                                             self.parent.filter.PrinterName))
            time.sleep(waitdelay)
            waitdelay = statusstabilizationdelay * increment

    def retrieveInternalPageCounter(self) :
        """Returns the page counter from the printer via internal SNMP handling."""
        try :
            if (os.environ.get("PYKOTASTATUS") != "CANCELLED") and \
               (os.environ.get("PYKOTAACTION") == "ALLOW") and \
               (os.environ.get("PYKOTAPHASE") == "AFTER") and \
               self.parent.filter.JobSizeBytes :
                self.waitPrinting()
            self.waitIdle()
        except :
            self.parent.filter.printInfo("SNMP querying stage interrupted. Using latest value seen for internal page counter (%s) on printer %s." % (self.printerInternalPageCounter, self.parent.filter.PrinterName), "warn")
            raise
        return self.printerInternalPageCounter

class Handler(BaseHandler) :
    """A class for pysnmp v4.x, PyKota doesn't support earlier releases of pysnmp anymore.'"""
    def __init__(self, *args):
        BaseHandler.__init__(self, *args)
        self.snmpEngine = cmdgen.CommandGenerator()
        self.snmpAuth = cmdgen.CommunityData("pykota", self.community, 0)
        self.snmpTarget = cmdgen.UdpTransportTarget((self.printerHostname, self.port))

    def retrieveSNMPValues(self) :
        """Retrieves a printer's internal page counter and status via SNMP."""
        try :
            errorIndication, errorStatus, errorIndex, varBinds = \
                self.snmpEngine.getCmd(self.snmpAuth, \
                                       self.snmpTarget, \
                                       tuple([int(i) for i in pageCounterOID.split('.')]), \
                                       tuple([int(i) for i in hrPrinterStatusOID.split('.')]), \
                                       tuple([int(i) for i in hrDeviceStatusOID.split('.')]), \
                                       tuple([int(i) for i in hrPrinterDetectedErrorStateOID.split('.')]))
        except socket.gaierror, msg :
            errorIndication = repr(msg)
        except :
            errorIndication = "Unknown SNMP/Network error. Check your wires."
        if errorIndication :
            self.parent.filter.printInfo("SNMP Error : %s" % errorIndication, "error")
            self.initValues()
        elif errorStatus :
            self.parent.filter.printInfo("SNMP Error : %s at %s" % (errorStatus.prettyPrint(), \
                                                                        varBinds[int(errorIndex)-1]), \
                                             "error")
            self.initValues()
        else :
            self.printerInternalPageCounter = max(self.printerInternalPageCounter, int(varBinds[0][1].prettyPrint() or "0"))
            try :
                self.printerStatus = int(varBinds[1][1].prettyPrint())
            except ValueError :
                self.parent.filter.logdebug("The printer reported a non-integer printer status, it will be converted to 2 ('unknown')")
                self.printerStatus = 2
            try :
                self.deviceStatus = int(varBinds[2][1].prettyPrint())
            except ValueError :
                self.parent.filter.logdebug("The printer reported a non-integer device status, it will be converted to 1 ('unknown')")
                self.deviceStatus = 1
            self.printerDetectedErrorState = self.extractErrorStates(str(varBinds[3][1]))
            self.parent.filter.logdebug("SNMP answer decoded : PageCounter : %s  PrinterStatus : '%s'  DeviceStatus : '%s'  PrinterErrorState : '%s'" \
                                            % (self.printerInternalPageCounter, \
                                                   printerStatusValues.get(self.printerStatus), \
                                                   deviceStatusValues.get(self.deviceStatus), \
                                                   self.printerDetectedErrorState))

def main(hostname) :
    """Tries SNMP accounting for a printer host."""
    class fakeFilter :
        """Fakes a filter for testing purposes."""
        def __init__(self) :
            """Initializes the fake filter."""
            self.PrinterName = "FakePrintQueue"
            self.JobSizeBytes = 1

        def printInfo(self, msg, level="info") :
            """Prints informational message."""
            sys.stderr.write("%s : %s\n" % (level.upper(), msg))
            sys.stderr.flush()

        def logdebug(self, msg) :
            """Prints debug message."""
            self.printInfo(msg, "debug")

    class fakeAccounter :
        """Fakes an accounter for testing purposes."""
        def __init__(self) :
            """Initializes fake accounter."""
            self.arguments = "snmp:public"
            self.filter = fakeFilter()
            self.protocolHandler = Handler(self, hostname)

        def getLastPageCounter(self) :
            """Fakes the return of a page counter."""
            return 0

    acc = fakeAccounter()
    return acc.protocolHandler.retrieveInternalPageCounter()

if __name__ == "__main__" :
    if len(sys.argv) != 2 :
        sys.stderr.write("Usage :  python  %s  printer_ip_address\n" % sys.argv[0])
    else :
        pagecounter = main(sys.argv[1])
        print "Internal page counter's value is : %s" % pagecounter
