#! /usr/bin/env python
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
#

import sys
from struct import unpack

OPERATION_ATTRIBUTES_TAG = 0x01
JOB_ATTRIBUTES_TAG = 0x02
END_OF_ATTRIBUTES_TAG = 0x03
PRINTER_ATTRIBUTES_TAG = 0x04
UNSUPPORTED_ATTRIBUTES_TAG = 0x05

class PyKotaIPPError(Exception):
    """An exception for PyKota IPP related stuff."""
    def __init__(self, message = ""):
        self.message = message
        Exception.__init__(self, message)
    def __repr__(self):
        return self.message
    __str__ = __repr__

class IPPMessage :
    """A class for IPP message files."""
    def __init__(self, data) :
        """Initializes an IPP Message object."""
        self.data = data
        self._attributes = {}
        self.curname = None
        self.tags = [ None ] * 256      # by default all tags reserved
        
        # Delimiter tags
        self.tags[0x01] = "operation-attributes-tag"
        self.tags[0x02] = "job-attributes-tag"
        self.tags[0x03] = "end-of-attributes-tag"
        self.tags[0x04] = "printer-attributes-tag"
        self.tags[0x05] = "unsupported-attributes-tag"
        
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
        
    def __getattr__(self, attrname) :    
        """Allows self.attributes to return the attributes names."""
        if attrname == "attributes" :
            keys = self._attributes.keys()
            keys.sort()
            return keys
        raise AttributeError, attrname
            
    def __getitem__(self, ippattrname) :    
        """Fakes a dictionnary d['key'] notation."""
        value = self._attributes.get(ippattrname)
        if value is not None :
            if len(value) == 1 :
                value = value[0]
        return value        
    get = __getitem__    
        
    def parseTag(self) :    
        """Extracts information from an IPP tag."""
        pos = self.position
        valuetag = self.tags[ord(self.data[pos])]
        # print valuetag.get("name")
        pos += 1
        posend = pos2 = pos + 2
        namelength = unpack(">H", self.data[pos:pos2])[0]
        if not namelength :
            name = self.curname
        else :    
            posend += namelength
            self.curname = name = self.data[pos2:posend]
        pos2 = posend + 2
        valuelength = unpack(">H", self.data[posend:pos2])[0]
        posend = pos2 + valuelength
        value = self.data[pos2:posend]
        oldval = self._attributes.setdefault(name, [])
        oldval.append(value)
        return posend - self.position
        
    def operation_attributes_tag(self) : 
        """Indicates that the parser enters into an operation-attributes-tag group."""
        return self.parseTag()
        
    def job_attributes_tag(self) : 
        """Indicates that the parser enters into an operation-attributes-tag group."""
        return self.parseTag()
        
    def printer_attributes_tag(self) : 
        """Indicates that the parser enters into an operation-attributes-tag group."""
        return self.parseTag()
        
    def parse(self) :
        """Parses an IPP Message.
        
           NB : Only a subset of RFC2910 is implemented.
           We are only interested in textual informations for now anyway.
        """
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
            raise PyKotaIPPError, "Unexpected end of IPP message."
            
if __name__ == "__main__" :            
    if len(sys.argv) < 2 :
        print "usage : python ipp.py /var/spool/cups/c00005 (for example)\n"
    else :    
        infile = open(sys.argv[1])
        message = IPPMessage(infile.read())
        infile.close()
        print "Client hostname : %s" % message["job-originating-host-name"]
