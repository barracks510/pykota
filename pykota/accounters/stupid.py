# PyKota
# -*- coding: ISO-8859-15 -*-
#
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
# Revision 1.9  2003/12/27 15:43:36  uid67467
# Savannah is back online...
#
# Revision 1.8  2003/11/23 19:01:37  jalet
# Job price added to history
#
# Revision 1.7  2003/11/21 14:28:46  jalet
# More complete job history.
#
# Revision 1.6  2003/11/12 23:29:24  jalet
# More work on new backend. This commit may be unstable.
#
# Revision 1.5  2003/10/07 09:07:29  jalet
# Character encoding added to please latest version of Python
#
# Revision 1.4  2003/06/25 14:10:01  jalet
# Hey, it may work (edpykota --reset excepted) !
#
# Revision 1.3  2003/05/27 23:00:21  jalet
# Big rewrite of external accounting methods.
# Should work well now.
#
# Revision 1.2  2003/04/30 13:40:47  jalet
# Small fix
#
# Revision 1.1  2003/04/30 13:36:40  jalet
# Stupid accounting method was added.
#
#
#

import sys
import tempfile
from pykota.accounter import AccounterBase, PyKotaAccounterError

class Accounter(AccounterBase) :
    def computeJobSize(self) :    
        """Computes the job size and return its value.
        
           THIS METHOD IS COMPLETELY UNRELIABLE BUT SERVES AS AN EXAMPLE.
        """
        # first we log a message because using this accounting method is not recommended.
        self.filter.logger.log_message(_("Using the 'stupid' accounting method is unreliable."), "warn")
        
        temporary = None    
        if self.filter.inputfile is None :    
            infile = sys.stdin
            # we will have to duplicate our standard input
            temporary = tempfile.TemporaryFile()
        else :    
            infile = open(self.filter.inputfile, "rb")
            
        pagecount = 0
        for line in infile.xreadlines() :
            pagecount += line.count("showpage")
            if temporary is not None :    
                temporary.write(line)    
                
        if temporary is not None :    
            # this is a copy of our previous standard input
            # flush, then rewind
            temporary.flush()
            temporary.seek(0, 0)
            # our temporary file will be used later if the
            # job is allowed.
            self.filter.inputfile = temporary
        else :
            infile.close()
        return pagecount    
