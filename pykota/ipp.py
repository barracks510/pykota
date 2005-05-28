#! /usr/bin/env python
# -*- coding: ISO-8859-15 -*-
#
# PyKota
#
# PyKota : Print Quotas for CUPS and LPRng
#
# (c) 2003, 2004, 2005 Jerome Alet <alet@librelogiciel.com>
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
from struct import unpack

OPERATION_ATTRIBUTES_TAG = 0x01
JOB_ATTRIBUTES_TAG = 0x02
END_OF_ATTRIBUTES_TAG = 0x03
PRINTER_ATTRIBUTES_TAG = 0x04
UNSUPPORTED_ATTRIBUTES_TAG = 0x05

class IPPError(Exception):
    """An exception for IPP related stuff."""
    def __init__(self, message = ""):
        self.message = message
        Exception.__init__(self, message)
    def __repr__(self):
        return self.message
    __str__ = __repr__

class IPPMessage :
    """A class for IPP message files.
    
       Usage :
       
         fp = open("/var/spool/cups/c00001", "rb")
         message = IPPMessage(fp.read())
         fp.close()
         print "IPP version : %s" % message.version
         print "IPP operation Id : %s" % message.operation_id
         print "IPP request Id : %s" % message.request_id
         for attrtype in ("operation", "job", "printer", "unsupported") :
             attrdict = getattr(message, "%s_attributes" % attrtype)
             if attrdict :
                 print "%s attributes :" % attrtype.title()
                 for key in attrdict.keys() :
                     print "  %s : %s" % (key, attrdict[key])
    """
    attributes_types = ("operation", "job", "printer", "unsupported")
    def __init__(self, data, debug=0) :
        """Initializes and parses IPP Message object.
        
           Parameters :
           
             data : the IPP Message's content.
             debug : a boolean value to output debug info on stderr.
        """
        self.debug = debug
        self.data = data
        for attrtype in self.attributes_types :
            setattr(self, "%s_attributes" % attrtype, {})
        self.tags = [ None ] * 256      # by default all tags reserved
        
        # Delimiter tags
        self.tags[OPERATION_ATTRIBUTES_TAG] = "operation-attributes-tag"
        self.tags[JOB_ATTRIBUTES_TAG] = "job-attributes-tag"
        self.tags[END_OF_ATTRIBUTES_TAG] = "end-of-attributes-tag"
        self.tags[PRINTER_ATTRIBUTES_TAG] = "printer-attributes-tag"
        self.tags[UNSUPPORTED_ATTRIBUTES_TAG] = "unsupported-attributes-tag"
        
        # out of band values
        self.tags[0x10] = "unsupported"
        self.tags[0x11] = "reserved-for-future-default"
        self.tags[0x12] = "unknown"
        self.tags[0x13] = "no-value"
        
        # integer values
        self.tags[0x20] = "generic-integer"
        self.tags[0x21] = "integer"
        self.tags[0x22] = "boolean"
        self.tags[0x23] = "enum"
        
        # octetString
        self.tags[0x30] = "octetString-with-an-unspecified-format"
        self.tags[0x31] = "dateTime"
        self.tags[0x32] = "resolution"
        self.tags[0x33] = "rangeOfInteger"
        self.tags[0x34] = "reserved-for-collection"
        self.tags[0x35] = "textWithLanguage"
        self.tags[0x36] = "nameWithLanguage"
        
        # character strings
        self.tags[0x20] = "generic-character-string"
        self.tags[0x41] = "textWithoutLanguage"
        self.tags[0x42] = "nameWithoutLanguage"
        # self.tags[0x43] = "reserved"
        self.tags[0x44] = "keyword"
        self.tags[0x45] = "uri"
        self.tags[0x46] = "uriScheme"
        self.tags[0x47] = "charset"
        self.tags[0x48] = "naturalLanguage"
        self.tags[0x49] = "mimeMediaType"
        
        # now parses the IPP message
        self.parse()
        
    def printInfo(self, msg) :    
        """Prints a debug message."""
        if self.debug :
            sys.stderr.write("%s\n" % msg)
            sys.stderr.flush()
            
    def parseTag(self) :    
        """Extracts information from an IPP tag."""
        pos = self.position
        tagtype = self.tags[ord(self.data[pos])]
        pos += 1
        posend = pos2 = pos + 2
        namelength = unpack(">H", self.data[pos:pos2])[0]
        if not namelength :
            name = self._curname
        else :    
            posend += namelength
            self._curname = name = self.data[pos2:posend]
        pos2 = posend + 2
        valuelength = unpack(">H", self.data[posend:pos2])[0]
        posend = pos2 + valuelength
        value = self.data[pos2:posend]
        if tagtype in ("integer", "enum") :
            value = unpack(">I", value)[0]
        oldval = self._curdict.setdefault(name, [])
        oldval.append((tagtype, value))
        self.printInfo("%s(%s) : %s" % (name, tagtype, value))
        return posend - self.position
        
    def operation_attributes_tag(self) : 
        """Indicates that the parser enters into an operation-attributes-tag group."""
        self.printInfo("Start of operation_attributes_tag")
        self._curdict = self.operation_attributes
        return self.parseTag()
        
    def job_attributes_tag(self) : 
        """Indicates that the parser enters into a job-attributes-tag group."""
        self.printInfo("Start of job_attributes_tag")
        self._curdict = self.job_attributes
        return self.parseTag()
        
    def printer_attributes_tag(self) : 
        """Indicates that the parser enters into a printer-attributes-tag group."""
        self.printInfo("Start of printer_attributes_tag")
        self._curdict = self.printer_attributes
        return self.parseTag()
        
    def unsupported_attributes_tag(self) : 
        """Indicates that the parser enters into an unsupported-attributes-tag group."""
        self.printInfo("Start of unsupported_attributes_tag")
        self._curdict = self.unsupported_attributes
        return self.parseTag()
        
    def parse(self) :
        """Parses an IPP Message.
        
           NB : Only a subset of RFC2910 is implemented.
        """
        self._curname = None
        self._curdict = None
        self.version = "%s.%s" % (ord(self.data[0]), ord(self.data[1]))
        self.operation_id = "0x%04x" % unpack(">H", self.data[2:4])[0]
        self.request_id = "0x%08x" % unpack(">I", self.data[4:8])[0]
        self.position = 8
        try :
            tag = ord(self.data[self.position])
            while tag != END_OF_ATTRIBUTES_TAG :
                self.position += 1
                name = self.tags[tag]
                if name is not None :
                    func = getattr(self, name.replace("-", "_"), None)
                    if func is not None :
                        self.position += func()
                        if ord(self.data[self.position]) > UNSUPPORTED_ATTRIBUTES_TAG :
                            self.position -= 1
                            continue
                tag = ord(self.data[self.position])
        except IndexError :
            raise IPPError, "Unexpected end of IPP message."
            
        # Now transform all one-element lists into single values
        for attrtype in self.attributes_types :
            attrdict = getattr(self, "%s_attributes" % attrtype)
            for (key, value) in attrdict.items() :
                if len(value) == 1 :
                    attrdict[key] = value[0]
            
if __name__ == "__main__" :            
    if (len(sys.argv) < 2) or (sys.argv[1] == "--debug") :
        print "usage : python ipp.py /var/spool/cups/c00005 [--debug] (for example)\n"
    else :    
        infile = open(sys.argv[1], "rb")
        message = IPPMessage(infile.read(), debug=(sys.argv[-1]=="--debug"))
        infile.close()
        print "IPP version : %s" % message.version
        print "IPP operation Id : %s" % message.operation_id
        print "IPP request Id : %s" % message.request_id
        for attrtype in message.attributes_types :
            attrdict = getattr(message, "%s_attributes" % attrtype)
            if attrdict :
                print "%s attributes :" % attrtype.title()
                for key in attrdict.keys() :
                    print "  %s : %s" % (key, attrdict[key])
