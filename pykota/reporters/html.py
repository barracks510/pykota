# PyKota
# -*- coding: ISO-8859-15 -*-

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
# Revision 1.2  2003/12/27 15:43:36  uid67467
# Savannah is back online...
#
# Revision 1.1  2003/12/02 14:41:17  jalet
# And as always, I forgot most of the new files :-)
#
#
#

from mx import DateTime

from pykota.reporter import BaseReporter, PyKotaReporterError
    
class Reporter(BaseReporter) :    
    """HTML reporter."""
    def generateReport(self) :
        """Produces a simple HTML report."""
        self.report = []
        for printer in self.printers :
            self.report.append('<h2 class="printername">%s</h2>' % self.getPrinterTitle(printer))
            self.report.append('<h3 class="printergracedelay">%s</h3>' % self.getPrinterGraceDelay(printer))
            (pjob, ppage) = self.getPrinterPrices(printer)
            self.report.append('<h4 class="priceperjob">%s</h4>' % pjob)
            self.report.append('<h4 class="priceperpage">%s</h4>' % ppage)
            total = 0
            totalmoney = 0.0
            self.report.append('<table class="pykotatable" border="1">')
            headers = self.getReportHeader().split()
            headers.insert(1, "LimitBy")
            self.report.append('<tr class="pykotacolsheader">%s</tr>' % "".join(["<th>%s</th>" % h for h in headers]))
            oddeven = 0
            if self.isgroup :
                for (group, grouppquota) in self.tool.storage.getPrinterGroupsAndQuotas(printer, self.ugnames) :
                    oddeven += 1
                    if oddeven % 1 :
                        oddevenclass = "odd"
                    else :    
                        oddevenclass = "even"
                    (pages, money, name, reached, soft, hard, balance, datelimit, lifepagecounter, lifetimepaid) = self.getQuota(group, grouppquota)
                    self.report.append('<tr class="%s">%s</tr>' % (oddevenclass, "".join(["<td>%s</td>" % h for h in (name, reached, pagecounter, soft, hard, balance, datelimit or "&nbsp;", lifepagecounter, lifetimepaid)])))
                    total += pages
                    totalmoney += money
            else :
                # default is user quota report
                for (user, userpquota) in self.tool.storage.getPrinterUsersAndQuotas(printer, self.ugnames) :
                    oddeven += 1
                    if oddeven % 1 :
                        oddevenclass = "odd"
                    else :    
                        oddevenclass = "even"
                    (pages, money, name, reached, pagecounter, soft, hard, balance, datelimit, lifepagecounter, lifetimepaid) = self.getQuota(user, userpquota)
                    self.report.append('<tr class="%s">%s</tr>' % (oddevenclass, "".join(["<td>%s</td>" % h for h in (name, reached, pagecounter, soft, hard, balance, datelimit or "&nbsp;", lifepagecounter, lifetimepaid)])))
                    total += pages
                    totalmoney += money
            if total or totalmoney :        
                (tpage, tmoney) = self.getTotals(total, totalmoney)
                self.report.append('<tr class="totals"><td colspan="7">&nbsp;</td><td align="right">%s</td><td align="right">%s</td></tr>' % (tpage, tmoney))
            self.report.append('<tr class="realpagecounter"><td colspan="7">&nbsp;</td><td align="right">%s</td></tr>' % self.getPrinterRealPageCounter(printer))
            self.report.append('</table>')
        if self.isgroup :    
            self.report.append('<p class="warning">%s</p>' % _("Totals may be inaccurate if some users are members of several groups."))
        return "\n".join(self.report)    
                        
