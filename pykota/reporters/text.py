# -*- coding: UTF-8 -*-
#
# PyKota : Print Quotas for CUPS
#
# (c) 2003, 2004, 2005, 2006, 2007 Jerome Alet <alet@librelogiciel.com>
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

"""This module defines a class for plain text reporting."""

from pykota.reporter import BaseReporter
    
class Reporter(BaseReporter) :    
    """Text reporter."""
    def generateReport(self) :
        """Produces a simple text report."""
        self.report = []
        if self.isgroup :
            prefix = "Group"
        else :    
            prefix = "User"
        for printer in self.printers :
            self.report.append(self.getPrinterTitle(printer))
            self.report.append(self.getPrinterGraceDelay(printer))
            (pjob, ppage) = self.getPrinterPrices(printer)
            self.report.append(pjob)
            self.report.append(ppage)
            
            total = 0
            totalmoney = 0.0
            header = self.getReportHeader()
            self.report.append(header)
            self.report.append('-' * len(header))
            for (entry, entrypquota) in getattr(self.tool.storage, "getPrinter%ssAndQuotas" % prefix)(printer, self.ugnames) :
                (pages, money, name, reached, pagecounter, soft, hard, balance, datelimit, lifepagecounter, lifetimepaid, overcharge, warncount) = self.getQuota(entry, entrypquota)
                self.report.append("%-15.15s %s %5s %7i %7s %7s %10s %-10.10s %8i %10s %4s" % (name, reached, overcharge, pagecounter, soft, hard, balance, datelimit, lifepagecounter, lifetimepaid, warncount))
                total += pages
                totalmoney += money
                
            if total or totalmoney :        
                (tpage, tmoney) = self.getTotals(total, totalmoney)
                self.report.append((" " * 62) + tpage + tmoney)
            self.report.append((" " * 63) + self.getPrinterRealPageCounter(printer))
            self.report.append("")        
        if self.isgroup :    
            self.report.append(_("Totals may be inaccurate if some users are members of several groups."))
        return "\n".join(self.report)    
                        
