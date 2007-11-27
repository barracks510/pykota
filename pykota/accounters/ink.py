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

import os
from pykota.accounter import AccounterBase, PyKotaAccounterError


class Accounter(AccounterBase) :
    cspaceExpanded = {
                        "CMYK" : { "C" : "cyan", "M" : "magenta", "Y" : "yellow", "K" : "black" } ,
                        "CMY" : { "C" : "cyan", "M" : "magenta", "Y" : "yellow" } ,
                        "RGB" : { "R" : "red", "G" : "green", "B" : "blue" } ,
                        "BW" : { "B" : "black", "W" : "white" } ,
                        "GC" : { "G" : "grayscale", "C" : "colored" } ,
                     }
    def computeJobSize(self) :    
        """Do ink accounting for a print job."""
        if (not self.isPreAccounter) and \
            (self.filter.accounter.arguments == self.filter.preaccounter.arguments) :
            # if precomputing has been done and both accounter and preaccounter are
            # configured the same, no need to launch a second pass since we already
            # know the result.
            self.filter.logdebug("Precomputing pass told us that job is %s pages long." % self.filter.softwareJobSize)
            self.inkUsage = self.filter.preaccounter.inkUsage   # Optimize : already computed !
            return self.filter.softwareJobSize                  # Optimize : already computed !
            
        parameters = [p.strip() for p in self.arguments.split(',')]
        if len(parameters) == 1 :
            parameters.append("72")
        (colorspace, resolution) = parameters
        colorspace = colorspace.lower()
        if colorspace not in ("cmyk", "bw", "cmy", "rgb", "gc") :
            raise PyKotaAccounterError, "Invalid parameters for ink accounter : [%s]" % self.arguments
            
        try :    
            resolution = int(resolution)
        except ValueError :    
            raise PyKotaAccounterError, "Invalid parameters for ink accounter : [%s]" % self.arguments
            
        self.filter.logdebug("Using internal parser to compute job's size and ink usage.")
        
        jobsize = 0
        if self.filter.JobSizeBytes :
            try :
                from pkpgpdls import analyzer, pdlparser
            except ImportError :    
                self.filter.printInfo("pkpgcounter is now distributed separately, please grab it from http://www.pykota.com/software/pkpgcounter", "error")
                self.filter.printInfo("Precomputed job size will be forced to 0 pages.", "error")
            else :     
                options = analyzer.AnalyzerOptions(colorspace=colorspace, resolution=resolution)
                try :
                    parser = analyzer.PDLAnalyzer(self.filter.DataFile, options)
                    (cspace, pages) = parser.getInkCoverage()
                except pdlparser.PDLParserError, msg :    
                    # Here we just log the failure, but
                    # we finally ignore it and return 0 since this
                    # computation is just an indication of what the
                    # job's size MAY be.
                    self.filter.printInfo(_("Unable to precompute the job's size and ink coverage with the generic PDL analyzer : %s") % msg, "warn")
                else :    
                    cspacelabels = self.cspaceExpanded[cspace]
                    for page in pages :
                        colordict = {}
                        for color in page.keys() :
                            colordict[cspacelabels[color]] = page[color]
                        self.inkUsage.append(colordict)    
                    jobsize = len(pages)
                    try :
                        if self.filter.Ticket.FileName is not None :
                            # when a filename is passed as an argument, the backend 
                            # must generate the correct number of copies.
                            jobsize *= self.filter.Ticket.Copies
                            self.inkUsage *= self.filter.Ticket.Copies
                    except AttributeError : # When not run from the cupspykota backend 
                        pass
                    self.filter.logdebug("Ink usage : %s ===> %s" % (cspace, repr(self.inkUsage)))
        return jobsize        
