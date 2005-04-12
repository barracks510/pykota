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

import sys
import os
import socket
import time
import signal

ITERATIONDELAY = 1.0   # 1 Second
STABILIZATIONDELAY = 3 # We must read three times the same value to consider it to be stable

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
                    "40000" : "Sleep Mode",             # Standby
                  }
                  
class Handler :
    """A class for PJL print accounting."""
    def __init__(self, parent, printerhostname) :
        self.parent = parent
        self.printerHostname = printerhostname
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
        firstvalue = None
        while 1:
            self.retrievePJLValues()
            if self.printerStatus in ('10023', '10003') :
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
                        self.parent.filter.printInfo("Printer %s is lying to us !!!" % self.parent.filter.printername, "warn")
                        break
            self.parent.filter.logdebug(_("Waiting for printer %s to be printing...") % self.parent.filter.printername)
            time.sleep(ITERATIONDELAY)
        
    def waitIdle(self) :
        """Waits for printer status being 'idle'."""
        idle_num = idle_flag = 0
        while 1 :
            self.retrievePJLValues()
            idle_flag = 0
            if self.printerStatus in ('10000', '10001', '35078', '40000') :
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
    
    def retrieveInternalPageCounter(self) :
        """Returns the page counter from the printer via internal PJL handling."""
        try :
            if (os.environ.get("PYKOTASTATUS") != "CANCELLED") and \
               (os.environ.get("PYKOTAACTION") != "DENY") and \
               (os.environ.get("PYKOTAPHASE") == "AFTER") and \
               self.parent.filter.jobSizeBytes :
                self.waitPrinting()
            self.waitIdle()    
        except :    
            if self.printerInternalPageCounter is None :
                raise
            else :    
                self.parent.filter.printInfo(_("PJL querying stage interrupted. Using latest value seen for internal page counter (%s) on printer %s.") % (self.printerInternalPageCounter, self.parent.filter.printername), "warn")
        return self.printerInternalPageCounter
            
if __name__ == "__main__" :            
    if len(sys.argv) != 2 :    
        sys.stderr.write("Usage :  python  %s  printer_ip_address\n" % sys.argv[0])
    else :    
        def _(msg) :
            return msg
            
        class fakeFilter :
            def __init__(self) :
                self.printername = "FakePrintQueue"
                self.jobSizeBytes = 1
                
            def printInfo(self, msg, level="info") :
                sys.stderr.write("%s : %s\n" % (level.upper(), msg))
                sys.stderr.flush()
                
            def logdebug(self, msg) :    
                self.printInfo(msg, "debug")
                
        class fakeAccounter :        
            def __init__(self) :
                self.filter = fakeFilter()
                self.protocolHandler = Handler(self, sys.argv[1])
            
        acc = fakeAccounter()            
        print "Internal page counter's value is : %s" % acc.protocolHandler.retrieveInternalPageCounter()