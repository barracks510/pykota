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
# Revision 1.12  2005/02/19 18:16:06  jalet
# Optimize print job parsing by avoiding to pass the job's datas through
# PyKota's internal parser if the special construct "software()" is used
# with no argument in the 'accounter' directive.
#
# Revision 1.11  2004/09/24 21:19:48  jalet
# Did a pass of PyChecker
#
# Revision 1.10  2004/08/31 23:29:53  jalet
# Introduction of the new 'onaccountererror' configuration directive.
# Small fix for software accounter's return code which can't be None anymore.
# Make software and hardware accounting code look similar : will be factorized
# later.
#
# Revision 1.9  2004/08/25 22:34:39  jalet
# Now both software and hardware accounting raise an exception when no valid
# result can be extracted from the subprocess' output.
# Hardware accounting now reads subprocess' output until an integer is read
# or data is exhausted : it now behaves just like software accounting in this
# aspect.
#
# Revision 1.8  2004/08/22 14:04:47  jalet
# Tries to fix problem with subprocesses outputting more datas than needed
#
# Revision 1.7  2004/08/06 13:45:51  jalet
# Fixed french translation problem.
# Fixed problem with group quotas and strict enforcement.
#
# Revision 1.6  2004/07/01 19:56:43  jalet
# Better dispatching of error messages
#
# Revision 1.5  2004/06/10 22:42:06  jalet
# Better messages in logs
#
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
                self.filter.printInfo(_("Unable to compute job size with accounter %s") % msg)
            
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
