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
# Revision 1.4  2004/06/02 21:51:14  jalet
# Moved the sigterm capturing elsewhere
#
# Revision 1.3  2004/05/24 22:45:49  jalet
# New 'enforcement' directive added
# Polling loop improvements
#
# Revision 1.2  2004/05/18 14:49:23  jalet
# Big code changes to completely remove the need for "requester" directives,
# jsut use "hardware(... your previous requester directive's content ...)"
#
# Revision 1.1  2004/05/13 13:59:30  jalet
# Code simplifications
#
#

import sys
import os
import popen2
from pykota.accounter import AccounterBase, PyKotaAccounterError

class Accounter(AccounterBase) :
    def computeJobSize(self) :    
        """Feeds an external command with our datas to let it compute the job size, and return its value."""
        self.filter.logdebug("Launching software accounter %s" % self.arguments)
        MEGABYTE = 1024*1024
        self.filter.jobdatastream.seek(0)
        child = popen2.Popen4(self.arguments)
        try :
            data = self.filter.jobdatastream.read(MEGABYTE)    
            while data :
                child.tochild.write(data)
                data = self.filter.jobdatastream.read(MEGABYTE)
            child.tochild.flush()
            child.tochild.close()    
        except (IOError, OSError), msg :    
            msg = "%s : %s" % (self.arguments, msg) 
            self.filter.logger.log_message(_("Unable to compute job size with accounter %s") % msg)
        
        pagecount = 0
        try :
            pagecount = int(child.fromchild.readline().strip())
        except (AttributeError, ValueError) :
            self.filter.logger.log_message(_("Unable to compute job size with accounter %s") % self.arguments)
        except (IOError, OSError), msg :    
            msg = "%s : %s" % (self.arguments, msg) 
            self.filter.logger.log_message(_("Unable to compute job size with accounter %s") % msg)
        child.fromchild.close()
        
        try :
            retcode = child.wait()
        except OSError, msg :    
            self.filter.logger.log_message(_("Problem while waiting for software accounter pid %s to exit : %s") % (child.pid, msg))
        else :    
            if os.WIFEXITED(retcode) :
                status = os.WEXITSTATUS(retcode)
            else :    
                status = retcode
            self.filter.logger.log_message(_("Software accounter %s exit code is %s") % (self.arguments, repr(retcode)))
        self.filter.logdebug("Software accounter %s said job is %s pages long." % (self.arguments, pagecount))
        return pagecount    
            
