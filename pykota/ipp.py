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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# $Id$
#
#

import sys
from struct import pack, unpack

class IPPError(Exception):
    """An exception for IPP related stuff."""
    def __init__(self, message = ""):
        self.message = message
        Exception.__init__(self, message)
    def __repr__(self):
        return self.message
    __str__ = __repr__

class IPPRequest :
    """A class for IPP requests.
    
       Usage :
       
         fp = open("/var/spool/cups/c00001", "rb")
         message = IPPRequest(fp.read())
         fp.close()
         message.parse()
         # print message.dump() # dumps an equivalent to the original IPP message
         # print str(message)   # returns a string of text with the same content as below
         print "IPP version : %s.%s" % message.version
         print "IPP operation Id : 0x%04x" % message.operation_id
         print "IPP request Id : 0x%08x" % message.request_id
         for attrtype in message.attributes_types :
             attrdict = getattr(message, "%s_attributes" % attrtype)
             if attrdict :
                 print "%s attributes :" % attrtype.title()
                 for key in attrdict.keys() :
                     print "  %s : %s" % (key, attrdict[key])
         if message.data :            
             print "IPP datas : ", repr(message.data)            
    """
    attributes_types = ("operation", "job", "printer", "unsupported", \
                                     "subscription", "event_notification")
    def __init__(self, data="", version=None, operation_id=None, \
                                              request_id=None, debug=0) :
        """Initializes an IPP Message object.
        
           Parameters :
           
             data : the complete IPP Message's content.
             debug : a boolean value to output debug info on stderr.
        """
        self.debug = debug
        self._data = data
        self.parsed = 0
        
        # Initializes message
        if version is not None :
            try :
                self.version = [int(p) for p in version.split(".")]
            except AttributeError :
                if len(version) == 2 : # 2-tuple
                    self.version = version
                else :    
                    try :
                        self.version = [int(p) for p in str(float(version)).split(".")]
                    except :
                        self.version = (1, 1) # default version number
        self.operation_id = operation_id
        self.request_id = request_id
        self.data = ""
        
        # Initialize attributes mappings
        for attrtype in self.attributes_types :
            setattr(self, "%s_attributes" % attrtype, {})
            
        # Initialize tags    
        self.tags = [ None ] * 256 # by default all tags reserved
        
        # Delimiter tags
        self.tags[0x01] = "operation-attributes-tag"
        self.tags[0x02] = "job-attributes-tag"
        self.tags[0x03] = "end-of-attributes-tag"
        self.tags[0x04] = "printer-attributes-tag"
        self.tags[0x05] = "unsupported-attributes-tag"
        self.tags[0x06] = "subscription-attributes-tag"
        self.tags[0x07] = "event-notification-attributes-tag"
        
        # out of band values
        self.tags[0x10] = "unsupported"
        self.tags[0x11] = "reserved-for-future-default"
        self.tags[0x12] = "unknown"
        self.tags[0x13] = "no-value"
        self.tags[0x15] = "not-settable"
        self.tags[0x16] = "delete-attribute"
        self.tags[0x17] = "admin-define"
  
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
        self.tags[0x34] = "begCollection" # TODO : find sample files for testing
        self.tags[0x35] = "textWithLanguage"
        self.tags[0x36] = "nameWithLanguage"
        self.tags[0x37] = "endCollection"
        
        # character strings
        self.tags[0x40] = "generic-character-string"
        self.tags[0x41] = "textWithoutLanguage"
        self.tags[0x42] = "nameWithoutLanguage"
        self.tags[0x44] = "keyword"
        self.tags[0x45] = "uri"
        self.tags[0x46] = "uriScheme"
        self.tags[0x47] = "charset"
        self.tags[0x48] = "naturalLanguage"
        self.tags[0x49] = "mimeMediaType"
        self.tags[0x4a] = "memberAttrName"
        
        # Reverse mapping to generate IPP messages
        self.dictags = {}
        for i in range(len(self.tags)) :
            value = self.tags[i]
            if value is not None :
                self.dictags[value] = i
        
    def printInfo(self, msg) :    
        """Prints a debug message."""
        if self.debug :
            sys.stderr.write("%s\n" % msg)
            sys.stderr.flush()
            
    def __str__(self) :        
        """Returns the parsed IPP message in a readable form."""
        if not self.parsed :
            return ""
        buffer = []
        buffer.append("IPP version : %s.%s" % self.version)
        buffer.append("IPP operation Id : 0x%04x" % self.operation_id)
        buffer.append("IPP request Id : 0x%08x" % self.request_id)
        for attrtype in self.attributes_types :
            attrdict = getattr(self, "%s_attributes" % attrtype)
            if attrdict :
                buffer.append("%s attributes :" % attrtype.title())
                for key in attrdict.keys() :
                    buffer.append("  %s : %s" % (key, attrdict[key]))
        if self.data :            
            buffer.append("IPP datas : %s" % repr(message.data))
        return "\n".join(buffer)
        
    def dump(self) :    
        """Generates an IPP Message.
        
           Returns the message as a string of text.
        """    
        buffer = []
        if None not in (self.version, self.operation_id, self.request_id) :
            buffer.append(chr(self.version[0]) + chr(self.version[1]))
            buffer.append(pack(">H", self.operation_id))
            buffer.append(pack(">I", self.request_id))
            for attrtype in self.attributes_types :
                tagprinted = 0
                for (attrname, value) in getattr(self, "%s_attributes" % attrtype).items() :
                    if not tagprinted :
                        buffer.append(chr(self.dictags["%s-attributes-tag" % attrtype]))
                        tagprinted = 1
                    if type(value) != type([]) :
                        value = [ value ]
                    for (vtype, val) in value :
                        buffer.append(chr(self.dictags[vtype]))
                        buffer.append(pack(">H", len(attrname)))
                        buffer.append(attrname)
                        if vtype in ("integer", "enum") :
                            buffer.append(pack(">H", 4))
                            buffer.append(pack(">I", val))
                        elif vtype == "boolean" :
                            buffer.append(pack(">H", 1))
                            buffer.append(chr(val))
                        else :    
                            buffer.append(pack(">H", len(val)))
                            buffer.append(val)
            buffer.append(chr(self.dictags["end-of-attributes-tag"]))
        buffer.append(self.data)    
        return "".join(buffer)
            
    def parse(self) :
        """Parses an IPP Request.
        
           NB : Only a subset of RFC2910 is implemented.
        """
        self._curname = None
        self._curdict = None
        self.version = (ord(self._data[0]), ord(self._data[1]))
        self.operation_id = unpack(">H", self._data[2:4])[0]
        self.request_id = unpack(">I", self._data[4:8])[0]
        self.position = 8
        endofattributes = self.dictags["end-of-attributes-tag"]
        maxdelimiter = self.dictags["event-notification-attributes-tag"]
        try :
            tag = ord(self._data[self.position])
            while tag != endofattributes :
                self.position += 1
                name = self.tags[tag]
                if name is not None :
                    func = getattr(self, name.replace("-", "_"), None)
                    if func is not None :
                        self.position += func()
                        if ord(self._data[self.position]) > maxdelimiter :
                            self.position -= 1
                            continue
                tag = ord(self._data[self.position])
        except IndexError :
            raise IPPError, "Unexpected end of IPP message."
            
        # Now transform all one-element lists into single values
        for attrtype in self.attributes_types :
            attrdict = getattr(self, "%s_attributes" % attrtype)
            for (key, value) in attrdict.items() :
                if len(value) == 1 :
                    attrdict[key] = value[0]
        self.data = self._data[self.position+1:]            
        self.parsed = 1            
        
    def parseTag(self) :    
        """Extracts information from an IPP tag."""
        pos = self.position
        tagtype = self.tags[ord(self._data[pos])]
        pos += 1
        posend = pos2 = pos + 2
        namelength = unpack(">H", self._data[pos:pos2])[0]
        if not namelength :
            name = self._curname
        else :    
            posend += namelength
            self._curname = name = self._data[pos2:posend]
        pos2 = posend + 2
        valuelength = unpack(">H", self._data[posend:pos2])[0]
        posend = pos2 + valuelength
        value = self._data[pos2:posend]
        if tagtype in ("integer", "enum") :
            value = unpack(">I", value)[0]
        elif tagtype == "boolean" :    
            value = ord(value)
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
        
    def subscription_attributes_tag(self) : 
        """Indicates that the parser enters into a subscription-attributes-tag group."""
        self.printInfo("Start of subscription_attributes_tag")
        self._curdict = self.subscription_attributes
        return self.parseTag()
        
    def event_notification_attributes_tag(self) : 
        """Indicates that the parser enters into an event-notification-attributes-tag group."""
        self.printInfo("Start of event_notification_attributes_tag")
        self._curdict = self.event_notification_attributes
        return self.parseTag()
            
if __name__ == "__main__" :            
    if (len(sys.argv) < 2) or (sys.argv[1] == "--debug") :
        print "usage : python ipp.py /var/spool/cups/c00005 [--debug] (for example)\n"
    else :    
        infile = open(sys.argv[1], "rb")
        data = infile.read()
        message = IPPRequest(data, debug=(sys.argv[-1]=="--debug"))
        infile.close()
        message.parse()
        
        message2 = IPPRequest(message.dump())
        message2.parse()
        
        # We now compare the message parsed, and the output
        # of the parsing of the dumped message which was parsed.
        # We sort the results for the test, because the attributes ordering 
        # may vary since Python dictionnaries are not sorted.
        strmessage = str(message)
        strmessage2 = str(message2)
        lstmessage = strmessage.split("\n")
        lstmessage.sort()
        lstmessage2 = strmessage2.split("\n")
        lstmessage2.sort()
        if lstmessage == lstmessage2 :
            print "Test OK : parsing original and parsing the output of the dump produce the same result !"
            print strmessage
        else :    
            print "Test Failed !"
            print strmessage
            print
            print strmessage2
