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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# $Id$
#
#

import sys
import os
import socket
import time
import signal

# NB : in fact these variables don't do much, since the time 
# is in fact wasted in the sock.recv() blocking call, with the timeout
ITERATIONDELAY = 1   # 1 Second
STABILIZATIONDELAY = 3 # We must read three times the same value to consider it to be stable

# Here's the real thing :
TIMEOUT = 5

# Old method : pjlMessage = "\033%-12345X@PJL USTATUSOFF\r\n@PJL INFO STATUS\r\n@PJL INFO PAGECOUNT\r\n\033%-12345X"
# Here's a new method, which seems to work fine on my HP2300N, while the 
# previous one didn't.
# TODO : We could also experiment with USTATUS JOB=ON and we would know for sure 
# when the job is finished, without having to poll the printer repeatedly.
pjlMessage = "\033%-12345X@PJL USTATUS DEVICE=ON\r\n@PJL INFO STATUS\r\n@PJL INFO PAGECOUNT\r\n@PJL USTATUS DEVICE=OFF\033%-12345X"
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
        try :
            self.port = int(self.parent.arguments.split(":")[1].strip())
        except (IndexError, ValueError) :
            self.port = 9100
        self.printerInternalPageCounter = self.printerStatus = None
        self.timedout = 0
        
    def alarmHandler(self, signum, frame) :    
        """Query has timedout, handle this."""
        self.timedout = 1
        raise IOError, "Waiting for PJL answer timed out. Please try again later."
        
    def retrievePJLValues(self) :    
        """Retrieves a printer's internal page counter and status via PJL."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try :
            sock.connect((self.printerHostname, self.port))
        except socket.error, msg :
            self.parent.filter.printInfo(_("Problem during connection to %s:%s : %s") % (self.printerHostname, self.port, msg), "warn")
        else :
            self.parent.filter.logdebug("Connected to printer %s" % self.printerHostname)
            try :
                sock.send(pjlMessage)
            except socket.error, msg :
                self.parent.filter.printInfo(_("Problem while sending PJL query to %s:%s : %s") % (self.printerHostname, self.port, msg), "warn")
            else :    
                self.parent.filter.logdebug("Query sent to %s : %s" % (self.printerHostname, repr(pjlMessage)))
                actualpagecount = self.printerStatus = None
                self.timedout = 0
                while (self.timedout == 0) or (actualpagecount is None) or (self.printerStatus is None) :
                    signal.signal(signal.SIGALRM, self.alarmHandler)
                    signal.alarm(TIMEOUT)
                    try :
                        answer = sock.recv(1024)
                    except IOError, msg :    
                        self.parent.filter.logdebug("I/O Error [%s] : alarm handler probably called" % msg)
                        break   # our alarm handler was launched, probably
                    except socket.error :    
                        self.parent.filter.printInfo(_("Problem while receiving PJL answer from %s:%s : %s") % (self.printerHostname, self.port, msg), "warn")
                    else :    
                        readnext = 0
                        self.parent.filter.logdebug("PJL answer : %s" % repr(answer))
                        for line in [l.strip() for l in answer.split()] : 
                            if line.startswith("CODE=") :
                                self.printerStatus = line.split("=")[1]
                                self.parent.filter.logdebug("Found status : %s" % self.printerStatus)
                            elif line.startswith("PAGECOUNT=") :    
                                try :
                                    actualpagecount = int(line.split('=')[1].strip())
                                except ValueError :    
                                    self.parent.filter.logdebug("Received incorrect datas : [%s]" % line.strip())
                                else :
                                    self.parent.filter.logdebug("Found pages counter : %s" % actualpagecount)
                            elif line.startswith("PAGECOUNT") :    
                                readnext = 1 # page counter is on next line
                            elif readnext :    
                                try :
                                    actualpagecount = int(line.strip())
                                except ValueError :    
                                    self.parent.filter.logdebug("Received incorrect datas : [%s]" % line.strip())
                                else :
                                    self.parent.filter.logdebug("Found pages counter : %s" % actualpagecount)
                                    readnext = 0
                    signal.alarm(0)
                self.printerInternalPageCounter = max(actualpagecount, self.printerInternalPageCounter)
        sock.close()
        self.parent.filter.logdebug("Connection to %s is now closed." % self.printerHostname)
        
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
                        self.parent.filter.printInfo("Printer %s is lying to us !!!" % self.parent.filter.PrinterName, "warn")
                        break
            self.parent.filter.logdebug(_("Waiting for printer %s to be printing...") % self.parent.filter.PrinterName)
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
                if idle_num >= STABILIZATIONDELAY :
                    # printer status is stable, we can exit
                    break
            else :    
                idle_num = 0
            self.parent.filter.logdebug(_("Waiting for printer %s's idle status to stabilize...") % self.parent.filter.PrinterName)
            time.sleep(ITERATIONDELAY)
    
    def retrieveInternalPageCounter(self) :
        """Returns the page counter from the printer via internal PJL handling."""
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
                self.parent.filter.printInfo(_("PJL querying stage interrupted. Using latest value seen for internal page counter (%s) on printer %s.") % (self.printerInternalPageCounter, self.parent.filter.PrinterName), "warn")
        return self.printerInternalPageCounter
            
def main(hostname) :
    """Tries PJL accounting for a printer host."""
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
            self.arguments = "pjl:9100"
            self.filter = fakeFilter()
            self.protocolHandler = Handler(self, sys.argv[1])
        
    acc = fakeAccounter()            
    return acc.protocolHandler.retrieveInternalPageCounter()
    
if __name__ == "__main__" :            
    if len(sys.argv) != 2 :    
        sys.stderr.write("Usage :  python  %s  printer_ip_address\n" % sys.argv[0])
    else :    
        def _(msg) :
            return msg
            
        pagecounter = main(sys.argv[1])
        print "Internal page counter's value is : %s" % pagecounter
        
