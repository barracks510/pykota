# PyKota
# -*- coding: ISO-8859-15 -*-

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
# Revision 1.10  2005/02/13 22:02:29  jalet
# Big database structure changes. Upgrade script is now included as well as
# the new LDAP schema.
# Introduction of the -o | --overcharge command line option to edpykota.
# The output of repykota is more complete, but doesn't fit in 80 columns anymore.
# Introduction of the new 'maxdenybanners' directive.
#
# Revision 1.9  2004/01/08 14:10:33  jalet
# Copyright year changed.
#
# Revision 1.8  2004/01/06 15:51:46  jalet
# Code factorization
#
# Revision 1.7  2003/12/27 16:49:25  uid67467
# Should be ok now.
#
# Revision 1.6  2003/12/02 14:40:21  jalet
# Some code refactoring.
# New HTML reporter added, which is now used in the CGI script for web based
# print quota reports. It will need some de-uglyfication though...
#
# Revision 1.5  2003/10/07 09:07:29  jalet
# Character encoding added to please latest version of Python
#
# Revision 1.4  2003/07/07 11:49:24  jalet
# Lots of small fixes with the help of PyChecker
#
# Revision 1.3  2003/07/05 07:46:50  jalet
# The previous bug fix was incomplete.
#
# Revision 1.2  2003/07/02 09:29:12  jalet
# Bug fixed when wanting a report and an user/group was limited by account balance
#
# Revision 1.1  2003/06/30 12:46:15  jalet
# Extracted reporting code.
#
#
#

from pykota.reporter import BaseReporter, PyKotaReporterError
    
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
                        
