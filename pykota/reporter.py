# PyKota
# -*- coding: ISO-8859-15 -*-
#
# PyKota : Print Quotas for CUPS and LPRng
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
# Revision 1.4  2003/12/02 14:40:21  jalet
# Some code refactoring.
# New HTML reporter added, which is now used in the CGI script for web based
# print quota reports. It will need some de-uglyfication though...
#
# Revision 1.3  2003/11/25 23:46:40  jalet
# Don't try to verify if module name is valid, Python does this better than us.
#
# Revision 1.2  2003/10/07 09:07:28  jalet
# Character encoding added to please latest version of Python
#
# Revision 1.1  2003/06/30 12:46:15  jalet
# Extracted reporting code.
#
#
#

class PyKotaReporterError(Exception):
    """An exception for Reporter related stuff."""
    def __init__(self, message = ""):
        self.message = message
        Exception.__init__(self, message)
    def __repr__(self):
        return self.message
    __str__ = __repr__
    
class BaseReporter :    
    """Base class for all reports."""
    def __init__(self, tool, printers, ugnames, isgroup) :
        """Initialize local datas."""
        self.tool = tool
        self.printers = printers
        self.ugnames = ugnames
        self.isgroup = isgroup
        
    def getPrinterTitle(self, printer) :     
        return _("*** Report for %s quota on printer %s") % ((self.isgroup and "group") or "user", printer.Name)
        
    def getPrinterGraceDelay(self, printer) :    
        return _("Pages grace time: %i days") % self.tool.config.getGraceDelay(printer.Name)
        
    def getPrinterPrices(self, printer) :    
        return (_("Price per job: %.3f") % (printer.PricePerJob or 0.0), _("Price per page: %.3f") % (printer.PricePerPage or 0.0))
            
    def getReportHeader(self) :        
        if self.isgroup :
            return _("Group           used    soft    hard    balance grace         total       paid")
        else :    
            return _("User            used    soft    hard    balance grace         total       paid")
            
    def getPrinterRealPageCounter(self, printer) :        
        try :
            msg = "%9i" % printer.LastJob.PrinterPageCounter
        except TypeError :     
            msg = _("unknown")
        return _("Real : %s") % msg
                
    def getTotals(self, total, totalmoney) :            
        return (_("Total : %9i") % (total or 0.0), ("%11s" % ("%7.2f" % (totalmoney or 0.0))[:11]))
            
    def getQuota(self, entry, quota) :
        """Prints the quota information."""
        lifepagecounter = int(quota.LifePageCounter or 0)
        pagecounter = int(quota.PageCounter or 0)
        balance = float(entry.AccountBalance or 0.0)
        lifetimepaid = float(entry.LifeTimePaid or 0.0)
        
        if entry.LimitBy and (entry.LimitBy.lower() == "balance") :    
            if balance <= 0 :
                datelimit = "DENY"
                reached = "+B"
            else :    
                datelimit = ""
                reached = "-B"
        else :
            if quota.DateLimit is not None :
                now = DateTime.now()
                datelimit = DateTime.ISO.ParseDateTime(quota.DateLimit)
                if now >= datelimit :
                    datelimit = "DENY"
            elif (quota.HardLimit is not None) and (pagecounter >= quota.HardLimit) :    
                datelimit = "DENY"
            elif (quota.HardLimit is None) and (quota.SoftLimit is not None) and (pagecounter >= quota.SoftLimit) :
                datelimit = "DENY"
            else :    
                datelimit = ""
            reached = (((quota.SoftLimit is not None) and (pagecounter >= quota.SoftLimit) and "+") or "-") + "Q"
            
        strbalance = ("%5.2f" % balance)[:10]
        strlifetimepaid = ("%6.2f" % lifetimepaid)[:10]
        return (lifepagecounter, lifetimepaid, entry.Name, reached, pagecounter, str(quota.SoftLimit), str(quota.HardLimit), strbalance, str(datelimit)[:10], lifepagecounter, strlifetimepaid)
        
def openReporter(tool, reporttype, printers, ugnames, isgroup) :
    """Returns a reporter instance of the proper reporter."""
    try :
        exec "from pykota.reporters import %s as reporterbackend" % reporttype.lower()
    except ImportError :
        raise PyKotaReporterError, _("Unsupported reporter backend %s") % reporttype
    else :    
        return getattr(reporterbackend, "Reporter")(tool, printers, ugnames, isgroup)
