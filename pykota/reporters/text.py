#! /usr/bin/env python

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
# Revision 1.1  2003/06/30 12:46:15  jalet
# Extracted reporting code.
#
#
#

import sys

from mx import DateTime

from pykota.reporter import BaseReporter, PyKotaReporterError
    
class Reporter(BaseReporter) :    
    """Base class for all PyKota command line tools."""
    def generateReport(self) :
        """Produces a simple text report."""
        self.report = []
        for printer in self.printers :
            self.report.append(_("*** Report for %s quota on printer %s") % ((self.isgroup and "group") or "user", printer.Name))
            self.report.append(_("Pages grace time: %i days") % self.tool.config.getGraceDelay(printer.Name))
            if printer.PricePerJob is not None :
                self.report.append(_("Price per job: %.3f") % printer.PricePerJob)
            if printer.PricePerPage is not None :    
                self.report.append(_("Price per page: %.3f") % printer.PricePerPage)
            total = 0
            totalmoney = 0.0
            if self.isgroup :
                self.report.append(_("Group           used    soft    hard    balance grace         total       paid"))
                self.report.append("------------------------------------------------------------------------------")
                for (group, grouppquota) in self.tool.storage.getPrinterGroupsAndQuotas(printer, self.ugnames) :
                    (pages, money) = self.printQuota(group, grouppquota)
                    total += pages
                    totalmoney += money
            else :
                # default is user quota report
                self.report.append(_("User            used    soft    hard    balance grace         total       paid"))
                self.report.append("------------------------------------------------------------------------------")
                for (user, userpquota) in self.tool.storage.getPrinterUsersAndQuotas(printer, self.ugnames) :
                    (pages, money) = self.printQuota(user, userpquota)
                    total += pages
                    totalmoney += money
            if total or totalmoney :        
                self.report.append((" " * 50) + (_("Total : %9i") % total) + ("%11s" % ("%7.2f" % totalmoney)[:11]))
            try :
                msg = "%9i" % printer.LastJob.PrinterPageCounter
            except TypeError :     
                msg = _("unknown")
            self.report.append((" " * 51) + (_("Real : %s") % msg))
            self.report.append("")        
        if self.isgroup :    
            self.report.append(_("Totals may be inaccurate if some users are members of several groups."))
        return "\n".join(self.report)    
                        
    def printQuota(self, entry, quota) :
        """Prints the quota information."""
        lifepagecounter = int(quota.LifePageCounter or 0)
        pagecounter = int(quota.PageCounter or 0)
        balance = float(entry.AccountBalance or 0.0)
        lifetimepaid = float(entry.LifeTimePaid or 0.0)
        
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
            
        if entry.LimitBy.lower() == "balance" :    
            reached = (((balance <= 0) and "+") or "-") + "B"
        else :
            reached = (((quota.SoftLimit is not None) and (pagecounter >= quota.SoftLimit) and "+") or "-") + "Q"
            
        strbalance = ("%5.2f" % balance)[:10]
        strlifetimepaid = ("%6.2f" % lifetimepaid)[:10]
        self.report.append("%-9.9s %s %7i %7s %7s %10s %-10.10s %8i %10s" % (entry.Name, reached, pagecounter, str(quota.SoftLimit), str(quota.HardLimit), strbalance, str(datelimit)[:10], lifepagecounter, strlifetimepaid))
        return (lifepagecounter, lifetimepaid)
    
