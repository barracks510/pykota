# PyKota
# -*- coding: ISO-8859-15 -*-
#
# PyKota - Print Quotas for CUPS and LPRng
#
# (c) 2003, 2004, 2005, 2006 Jerome Alet <alet@librelogiciel.com>
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

import os
import popen2
from pykota.accounter import AccounterBase, PyKotaAccounterError

class Accounter(AccounterBase) :
    def computeJobSize(self) :    
        """Feeds an external command with our datas to let it compute the job size, and return its value."""
        self.filter.printInfo(_("Launching SOFTWARE(%s)...") % self.arguments)
        if not self.arguments :
            pagecounter = self.filter.softwareJobSize   # Optimize : already computed !
            self.filter.logdebug("Internal software accounter said job is %s pages long." % repr(pagecounter))
        else :
            MEGABYTE = 1024*1024
            infile = open(self.filter.DataFile, "rb")
            child = popen2.Popen4(self.arguments)
            try :
                data = infile.read(MEGABYTE)    
                while data :
                    child.tochild.write(data)
                    data = infile.read(MEGABYTE)
                child.tochild.flush()
                child.tochild.close()    
            except (IOError, OSError), msg :    
                msg = "%s : %s" % (self.arguments, msg) 
                self.filter.printInfo(_("Unable to compute job size with accounter %s") % msg)
            infile.close()
            pagecounter = None
            try :
                answer = child.fromchild.read()
            except (IOError, OSError), msg :    
                msg = "%s : %s" % (self.arguments, msg) 
                self.filter.printInfo(_("Unable to compute job size with accounter %s") % msg)
            else :    
                lines = [l.strip() for l in answer.split("\n")]
                for i in range(len(lines)) : 
                    try :
                        pagecounter = int(lines[i])
                    except (AttributeError, ValueError) :
                        self.filter.printInfo(_("Line [%s] skipped in accounter's output. Trying again...") % lines[i])
                    else :    
                        break
            child.fromchild.close()
            
            try :
                status = child.wait()
            except OSError, msg :    
                self.filter.printInfo(_("Problem while waiting for software accounter pid %s to exit : %s") % (child.pid, msg))
            else :    
                if os.WIFEXITED(status) :
                    status = os.WEXITSTATUS(status)
                self.filter.printInfo(_("Software accounter %s exit code is %s") % (self.arguments, str(status)))
                
            if pagecounter is None :    
                message = _("Unable to compute job size with accounter %s") % self.arguments
                if self.onerror == "CONTINUE" :
                    self.filter.printInfo(message, "error")
                else :
                    raise PyKotaAccounterError, message
            self.filter.logdebug("Software accounter %s said job is %s pages long." % (self.arguments, repr(pagecounter)))
            
        return pagecounter or 0
