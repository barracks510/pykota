# PyKota Print Quota Data Dumper
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
#

import sys
import os
import pwd
from mx import DateTime

try :
    import jaxml
except ImportError :    
    sys.stderr.write("The jaxml Python module is not installed. XML output is disabled.\n")
    sys.stderr.write("Download jaxml from http://www.librelogiciel.com/software/ or from your Debian archive of choice\n")
    hasJAXML = 0
else :    
    hasJAXML = 1

from pykota import version
from pykota.tool import PyKotaTool, PyKotaToolError, N_

class DumPyKota(PyKotaTool) :        
    """A class for dumpykota."""
    validdatatypes = { "history" : N_("History"),
                       "users" : N_("Users"),
                       "groups" : N_("Groups"),
                       "printers" : N_("Printers"),
                       "upquotas" : N_("Users Print Quotas"),
                       "gpquotas" : N_("Users Groups Print Quotas"),
                       "payments" : N_("History of Payments"),
                       "pmembers" : N_("Printers Groups Membership"), 
                       "umembers" : N_("Users Groups Membership"),
                     }
    validformats = { "csv" : N_("Comma Separated Values"),
                     "ssv" : N_("Semicolon Separated Values"),
                     "tsv" : N_("Tabulation Separated Values"),
                     "xml" : N_("eXtensible Markup Language"),
                     "cups" : N_("CUPS' page_log"),
                   }  
    validfilterkeys = [ "username",
                        "groupname",
                        "printername",
                        "pgroupname",
                      ]
    def main(self, arguments, options, restricted=1) :
        """Print Quota Data Dumper."""
        if restricted and not self.config.isAdmin :
            raise PyKotaToolError, "%s : %s" % (pwd.getpwuid(os.geteuid())[0], _("You're not allowed to use this command."))
            
        extractonly = {}
        for filterexp in arguments :
            if filterexp.strip() :
                try :
                    (filterkey, filtervalue) = [part.strip() for part in filterexp.split("=")]
                    if filterkey not in self.validfilterkeys :
                        raise ValueError                
                except ValueError :    
                    raise PyKotaToolError, _("Invalid value [%s] for --filter command line option, see help.") % filterexp
                else :    
                    extractonly.update({ filterkey : filtervalue })
            
        datatype = options["data"]
        if datatype not in self.validdatatypes.keys() :
            raise PyKotaToolError, _("Invalid modifier [%s] for --data command line option, see help.") % datatype
                    
        format = options["format"]
        if (format not in self.validformats.keys()) \
              or ((format == "cups") and (datatype != "history")) :
            raise PyKotaToolError, _("Invalid modifier [%s] for --format command line option, see help.") % format
            
        if (format == "xml") and not hasJAXML :
            raise PyKotaToolError, _("XML output is disabled because the jaxml module is not available.")
            
        entries = getattr(self.storage, "extract%s" % datatype.title())(extractonly)    
        if entries :
            mustclose = 0    
            if options["output"].strip() == "-" :    
                self.outfile = sys.stdout
            else :    
                self.outfile = open(options["output"], "w")
                mustclose = 1
                
            retcode = getattr(self, "dump%s" % format.title())(entries, datatype)
            
            if mustclose :
                self.outfile.close()
                
            return retcode    
        return 0
        
    def dumpWithSeparator(self, separator, entries) :    
        """Dumps datas with a separator."""
        for entry in entries :
            line = separator.join([ '"%s"' % field for field in entry ])
            try :
                self.outfile.write("%s\n" % line)
            except IOError, msg :    
                sys.stderr.write("%s : %s\n" % (_("PyKota data dumper failed : I/O error"), msg))
                return -1
        return 0        
        
    def dumpCsv(self, entries, dummy) :    
        """Dumps datas with a comma as the separator."""
        return self.dumpWithSeparator(",", entries)
                           
    def dumpSsv(self, entries, dummy) :    
        """Dumps datas with a comma as the separator."""
        return self.dumpWithSeparator(";", entries)
                           
    def dumpTsv(self, entries, dummy) :    
        """Dumps datas with a comma as the separator."""
        return self.dumpWithSeparator("\t", entries)
        
    def dumpCups(self, entries, dummy) :    
        """Dumps history datas as CUPS' page_log format."""
        fieldnames = entries[0]
        fields = {}
        for i in range(len(fieldnames)) :
            fields[fieldnames[i]] = i
        sortindex = fields["jobdate"]    
        entries = entries[1:]
        entries.sort(lambda m,n,si=sortindex : cmp(m[si], n[si]))
        for entry in entries[1:] :    
            printername = entry[fields["printername"]]
            username = entry[fields["username"]]
            jobid = entry[fields["jobid"]]
            jobdate = DateTime.ISO.ParseDateTime(entry[fields["jobdate"]])
            gmtoffset = jobdate.gmtoffset()
            jobdate = "%s %+03i00" % (jobdate.strftime("%d/%b/%Y:%H:%M:%S"), gmtoffset.hour)
            jobsize = entry[fields["jobsize"]] or 0
            copies = entry[fields["copies"]] or 1
            hostname = entry[fields["hostname"]] or ""
            self.outfile.write("%s %s %s [%s] %s %s - %s\n" % (printername, username, jobid, jobdate, jobsize, copies, hostname))
        
    def dumpXml(self, entries, datatype) :    
        """Dumps datas as XML."""
        x = jaxml.XML_document(encoding="UTF-8")
        x.pykota(version=version.__version__, author=version.__author__)
        x.dump(storage=self.config.getStorageBackend()["storagebackend"], type=datatype)
        headers = entries[0]
        for entry in entries[1:] :
            x._push()
            x.entry()
            for i in range(len(entry)) :
                value = str(entry[i])
                typval = type(entry[i]).__name__
                try :
                    value = unicode(value, self.getCharset()).encode("UTF-8")
                except UnicodeError :    
                    pass
                x.attribute(value, type=typval, name=headers[i])
            x._pop()    
        x._output(self.outfile)
