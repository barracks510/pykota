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
# $Log$
# Revision 1.2  2004/05/18 14:49:23  jalet
# Big code changes to completely remove the need for "requester" directives,
# jsut use "hardware(... your previous requester directive's content ...)"
#
# Revision 1.1  2004/05/13 13:59:30  jalet
# Code simplifications
#
#
#

import sys
import os
import popen2
import tempfile
from pykota.accounter import AccounterBase, PyKotaAccounterError

class Accounter(AccounterBase) :
    def computeJobSize(self) :    
        """Feeds an external command with our datas to let it compute the job size, and return its value."""
        temporary = None    
        if self.filter.inputfile is None :    
            infile = sys.stdin
            # we will have to duplicate our standard input
            temporary = tempfile.TemporaryFile()
        else :    
            infile = open(self.filter.inputfile, "rb")
            
        # launches software accounter
        # TODO : USE tempfile.mkstemp() instead ! Needs some work !
        infilename = tempfile.mktemp()
        outfilename = tempfile.mktemp()
        errfilename = tempfile.mktemp()
        
        try :
            # feed it with our data
            fakeinput = open(infilename, "wb")
            data = infile.read(256*1024)    
            while data :
                fakeinput.write(data)
                if temporary is not None :
                    temporary.write(data)
                data = infile.read(256*1024)
            fakeinput.close()
        
            # launches child process
            command = "%s <%s >%s 2>%s" % (self.arguments, infilename, outfilename, errfilename)
            retcode = os.system(command)
            
            # check exit status
            if (os.WIFEXITED(retcode) and not os.WEXITSTATUS(retcode)) or os.stat(errfilename) :
                # tries to extract the job size from the software accounter's
                # standard output
                childoutput = open(outfilename, "r")
                try :
                    pagecount = int(childoutput.readline().strip())
                except (AttributeError, ValueError) :
                    self.filter.logger.log_message(_("Unable to compute job size with accounter %s") % self.arguments)
                    pagecount = 0
                childoutput.close()    
            else :
                self.filter.logger.log_message(_("Unable to compute job size with accounter %s") % self.arguments)
                pagecount = 0
            os.remove(infilename)
            os.remove(outfilename)
            os.remove(errfilename)
        except IOError, msg :    
            # TODO : temporary files may remain on the filesystem...
            msg = "%s : %s" % (self.arguments, msg) 
            self.filter.logger.log_message(_("Unable to compute job size with accounter %s") % msg)
            pagecount = 0
            
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
            
