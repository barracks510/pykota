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
# Revision 1.7  2004/06/18 17:48:04  jalet
# Added native fast PDF parsing method
#
# Revision 1.6  2004/06/18 14:00:16  jalet
# Added PDF support in smart PDL analyzer (through GhostScript for now)
#
# Revision 1.5  2004/06/18 10:09:05  jalet
# Resets file pointer to start of file in all cases
#
# Revision 1.4  2004/06/18 06:16:14  jalet
# Fixes PostScript detection code for incorrect drivers
#
# Revision 1.3  2004/05/21 20:40:08  jalet
# All the code for pkpgcounter is now in pdlanalyzer.py
#
# Revision 1.2  2004/05/19 19:09:36  jalet
# Speed improvement
#
# Revision 1.1  2004/05/18 09:59:54  jalet
# pkpgcounter is now just a wrapper around the PDLAnalyzer class
#
#
#

import sys
import os
import struct
import tempfile
import popen2
    
KILOBYTE = 1024    
MEGABYTE = 1024 * KILOBYTE    

class PDLAnalyzerError(Exception):
    """An exception for PDL Analyzer related stuff."""
    def __init__(self, message = ""):
        self.message = message
        Exception.__init__(self, message)
    def __repr__(self):
        return self.message
    __str__ = __repr__
    
class PostScriptAnalyzer :
    def __init__(self, infile) :
        """Initialize PostScript Analyzer."""
        self.infile = infile
        
    def getJobSize(self) :    
        """Count pages in a DSC compliant PostScript document."""
        pagecount = 0
        while 1 :
            line = self.infile.readline()
            if not line :
                break
            if line.startswith("%%Page: ") :
                pagecount += 1
        return pagecount
        
class PDFAnalyzer :
    def __init__(self, infile) :
        """Initialize PDF Analyzer."""
        self.infile = infile
        try :
            if float(sys.version[:3]) >= 2.3 :
                self.getJobSize = self.native_getJobSize
            else :    
                self.getJobSize = self.gs_getJobSize
        except :
            self.getJobSize = self.gs_getJobSize
                
    def native_getJobSize(self) :    
        """Counts pages in a PDF document natively."""
        pagecount = 0
        content = []
        while 1 :     
            line = self.infile.readline()
            if not line :
                break
            line = line.strip()
            content.append(line)
            if line.endswith("endobj") :
                pagecount += " /".join([x.strip() for x in " ".join(content).split("/")]).count(" /Type /Page ")
                content = []
        return pagecount    
        
    def gs_getJobSize(self) :    
        """Counts pages in a PDF document using GhostScript to convert PDF to PS."""
        MEGABYTE = 1024*1024
        child = popen2.Popen4("gs -q -dNOPAUSE -dBATCH -dSAFER -sDEVICE=pswrite -sOutputFile=- -c save pop -f - 2>/dev/null")
        try :
            data = self.infile.read(MEGABYTE)    
            while data :
                child.tochild.write(data)
                data = self.infile.read(MEGABYTE)
            child.tochild.flush()
            child.tochild.close()    
        except (IOError, OSError), msg :    
            raise PDLAnalyzerError, "Unable to convert PDF input to PS with GhostScript : %s" % msg
        
        psanalyzer = PostScriptAnalyzer(child.fromchild)
        pagecount = psanalyzer.getJobSize()
        child.fromchild.close()
        try :
            retcode = child.wait()
        except OSError, msg :    
            self.filter.logger.log_message(_("Problem while waiting for PDF to PS converter (GhostScript pid %s) to exit : %s") % (child.pid, msg))
        else :    
            if os.WIFEXITED(retcode) :
                status = os.WEXITSTATUS(retcode)
            else :    
                status = retcode
            if status :    
                raise PDLAnalyzerError, "PDF to PS converter (GhostScript pid %s) exit code is %s" % (child.pid, repr(status))
        return pagecount    
        
class PCLAnalyzer :
    def __init__(self, infile) :
        """Initialize PCL Analyzer."""
        self.infile = infile
        
    def skip(self, nb) :    
        """Reads a new datablock."""
        newpos = self.pos + nb
        if newpos >= self.len :
            oldlen = self.len
            self.data = self.infile.read(MEGABYTE)
            self.len = len(self.data)
            if not self.len :
                return
            self.pos = newpos - oldlen
        else :    
            self.pos = newpos
        
    def readone(self) :
        """Reads a new byte."""
        if self.pos < self.len :
            char = self.data[self.pos]
        else :    
            self.data = self.infile.read(MEGABYTE)
            self.len = len(self.data)
            self.pos = 0
            if not self.len :    
                return
            char = self.data[0]
        self.pos += 1    
        return char
        
    def getJobSize(self) :     
        """Count pages in a PCL5 document."""
        #
        # Algorithm from pclcount
        # (c) 2003, by Eduardo Gielamo Oliveira & Rodolfo Broco Manin 
        # published under the terms of the GNU General Public Licence v2.
        # 
        # Backported from C to Python by Jerome Alet, then enhanced
        # with more PCL tags detected. I think all the necessary PCL tags
        # are recognized to correctly handle PCL5 files wrt their number
        # of pages. The documentation used for this was :
        #
        # HP PCL/PJL Reference Set
        # PCL5 Printer Language Technical Quick Reference Guide
        # http://h20000.www2.hp.com/bc/docs/support/SupportManual/bpl13205/bpl13205.pdf 
        #
        tagsends = { "&n" : "W", 
                     "&b" : "W", 
                     "*i" : "W", 
                     "*l" : "W", 
                     "*m" : "W", 
                     "*v" : "W", 
                     "*c" : "W", 
                     "(f" : "W", 
                     "*b" : "VW",
                     "(s" : "W", 
                     ")s" : "W", 
                     "&p" : "X", 
                     "&l" : "X" } 
        self.data = []             
        self.pos = self.len = 0
        copies = 1
        pagecount = resets = 0
        tag = None
        while 1 :
            char = self.readone()
            if not char :       # EOF ?
                break   
            if char == "\014" :    
                pagecount += 1
            elif char == "\033" :    
                #
                #     <ESC>*b###W -> Start of a raster data row/block
                #     <ESC>*b###V -> Start of a raster data plane
                #     <ESC>*c###W -> Start of a user defined pattern
                #     <ESC>*i###W -> Start of a viewing illuminant block
                #     <ESC>*l###W -> Start of a color lookup table
                #     <ESC>*m###W -> Start of a download dither matrix block
                #     <ESC>*v###W -> Start of a configure image data block
                #     <ESC>(s###W -> Start of a characters description block
                #     <ESC>)s###W -> Start of a fonts description block
                #     <ESC>(f###W -> Start of a symbol set block
                #     <ESC>&b###W -> Start of configuration data block
                #     <ESC>&l###X -> Number of copies
                #     <ESC>&n###W -> Starts an alphanumeric string ID block
                #     <ESC>&p###X -> Start of a non printable characters block
                #
                tagstart = self.readone()
                if tagstart in "E9=YZ" : # one byte PCL tag
                    if tagstart == "E" :
                        resets += 1
                    continue             # skip to next tag
                tag = tagstart + self.readone()
                try :
                    tagend = tagsends[tag]
                except KeyError :    
                    pass    # Unsupported PCL tag
                else :    
                    # Now read the numeric argument
                    size = 0
                    while 1 :
                        char = self.readone()
                        if not char.isdigit() :
                            break
                        size = (size * 10) + int(char)    
                    if char in tagend :    
                        if tag == "&l" :
                            copies = size
                        else :    
                            # doing a read will prevent the seek 
                            # for unseekable streams. 
                            # we just ignore the block anyway.
                            if tag == "&n" : 
                                # we have to take care of the operation id byte
                                # which is before the string itself
                                size += 1
                            self.skip(size)
                            
        # if pagecount is still 0, we will return the number
        # of resets instead of the number of form feed characters.
        # but the number of resets is always at least 2 with a valid
        # pcl file : one at the very start and one at the very end
        # of the job's data. So we substract 2 from the number of
        # resets. And since on our test data we needed to substract
        # 1 more, we finally substract 3, and will test several
        # PCL files with this. If resets < 2, then the file is
        # probably not a valid PCL file, so we return 0
        return copies * (pagecount or ((resets - 3) * (resets > 2)))
        
class PCLXLAnalyzer :
    def __init__(self, infile) :
        """Initialize PCLXL Analyzer."""
        raise PDLAnalyzerError, "PCLXL (aka PCL6) is not supported yet."
        self.infile = infile
        self.islittleendian = None
        found = 0
        while not found :
            line = self.infile.readline()
            if not line :
                break
            if line[1:12] == " HP-PCL XL;" :
                found = 1
                if line[0] == ")" :
                    self.littleendian()
                elif line[0] == "(" :    
                    self.bigendian()
        if not found :
            raise PDLAnalyzerError, "This file doesn't seem to be PCLXL (aka PCL6)"
        else :    
            self.tags = [lambda: None] * 256    
            self.tags[0x28] = self.bigendian    # big endian
            self.tags[0x29] = self.littleendian # big endian
            self.tags[0x43] = self.beginPage    # BeginPage
            self.tags[0x44] = self.endPage      # EndPage
            
            self.tags[0xc0] = lambda: 1 # ubyte
            self.tags[0xc1] = lambda: 2 # uint16
            self.tags[0xc2] = lambda: 4 # uint32
            self.tags[0xc3] = lambda: 2 # sint16
            self.tags[0xc4] = lambda: 4 # sint32
            self.tags[0xc5] = lambda: 4 # real32
            
            self.tags[0xc8] = self.array_8  # ubyte_array
            self.tags[0xc9] = self.array_16 # uint16_array
            self.tags[0xca] = self.array_32 # uint32_array
            self.tags[0xcb] = self.array_16 # sint16_array
            self.tags[0xcc] = self.array_32 # sint32_array
            self.tags[0xcd] = self.array_32 # real32_array
            
            self.tags[0xd0] = lambda: 2 # ubyte_xy
            self.tags[0xd1] = lambda: 4 # uint16_xy
            self.tags[0xd2] = lambda: 8 # uint32_xy
            self.tags[0xd3] = lambda: 4 # sint16_xy
            self.tags[0xd4] = lambda: 8 # sint32_xy
            self.tags[0xd5] = lambda: 8 # real32_xy
            
            self.tags[0xd0] = lambda: 4  # ubyte_box
            self.tags[0xd1] = lambda: 8  # uint16_box
            self.tags[0xd2] = lambda: 16 # uint32_box
            self.tags[0xd3] = lambda: 8  # sint16_box
            self.tags[0xd4] = lambda: 16 # sint32_box
            self.tags[0xd5] = lambda: 16 # real32_box
            
            self.tags[0xf8] = lambda: 1 # attr_ubyte
            self.tags[0xf9] = lambda: 2 # attr_uint16
            
            self.tags[0xfa] = self.embeddedData      # dataLength
            self.tags[0xfb] = self.embeddedDataSmall # dataLengthByte
            
    def debug(self, msg) :
        """Outputs a debug message on stderr."""
        sys.stderr.write("%s\n" % msg)
        sys.stderr.flush()
        
    def beginPage(self) :
        """Indicates the beginning of a new page."""
        self.pagecount += 1
        self.debug("Begin page %i at %s" % (self.pagecount, self.infile.tell()))
        
    def endPage(self) :
        """Indicates the end of a page."""
        self.debug("End page %i at %s" % (self.pagecount, self.infile.tell()))
        
    def handleArray(self, itemsize) :        
        """Handles arrays."""
        pos = self.infile.tell()
        datatype = self.infile.read(1)
        length = self.tags[ord(datatype)]()
        if length is None :
            self.debug("Bogus array length at %s" % pos)
        else :    
            sarraysize = self.infile.read(length)
            if self.islittleendian :
                fmt = "<"
            else :    
                fmt = ">"
            if length == 1 :    
                fmt += "B"
            elif length == 2 :    
                fmt += "H"
            elif length == 4 :    
                fmt += "I"
            else :    
                raise PDLAnalyzerError, "Error on array size at %s" % self.infile.tell()
            arraysize = struct.unpack(fmt, sarraysize)[0]
            self.debug("Array at %s, itemsize %s, datatype 0x%02x, size %s" % (pos, itemsize, ord(datatype), arraysize))
            return arraysize * itemsize
        
    def array_8(self) :    
        """Handles byte arrays."""
        return self.handleArray(1)
        
    def array_16(self) :    
        """Handles byte arrays."""
        return self.handleArray(2)
        
    def array_32(self) :    
        """Handles byte arrays."""
        return self.handleArray(4)
        
    def embeddedDataSmall(self) :
        """Handle small amounts of data."""
        pos = self.infile.tell()
        val = ord(self.infile.read(1))
        self.debug("smalldatablock at %s (0x%02x)" % (pos, val))
        return val
        
    def embeddedData(self) :
        """Handle normal amounts of data."""
        if self.islittleendian :
            fmt = "<I"
        else :    
            fmt = ">I"
        pos = self.infile.tell()
        val = struct.unpack(fmt, self.infile.read(4))[0]
        self.debug("datablock at %s (0x%08x)" % (pos, val))
        return val
        
    def littleendian(self) :        
        """Toggles to little endianness."""
        self.islittleendian = 1 # little endian
        
    def bigendian(self) :    
        """Toggles to big endianness."""
        self.islittleendian = 0 # big endian
    
    def getJobSize(self) :
        """Counts pages in a PCLXL (PCL6) document."""
        self.pagecount = 0
        while 1 :
            char = self.infile.read(1)
            if not char :
                break
            index = ord(char)    
            length = self.tags[index]()
            if length :    
                self.infile.read(length)    
        return self.pagecount
        
class PDLAnalyzer :    
    """Generic PDL Analyzer class."""
    def __init__(self, filename) :
        """Initializes the PDL analyzer.
        
           filename is the name of the file or '-' for stdin.
           filename can also be a file-like object which 
           supports read() and seek().
        """
        self.filename = filename
        
    def getJobSize(self) :    
        """Returns the job's size."""
        self.openFile()
        try :
            pdlhandler = self.detectPDLHandler()
        except PDLAnalyzerError, msg :    
            self.closeFile()
            raise PDLAnalyzerError, "ERROR : Unknown file format for %s (%s)" % (self.filename, msg)
        else :
            try :
                size = pdlhandler(self.infile).getJobSize()
            finally :    
                self.closeFile()
            return size
        
    def openFile(self) :    
        """Opens the job's data stream for reading."""
        self.mustclose = 0  # by default we don't want to close the file when finished
        if hasattr(self.filename, "read") and hasattr(self.filename, "seek") :
            # filename is in fact a file-like object 
            infile = self.filename
        elif self.filename == "-" :
            # we must read from stdin
            infile = sys.stdin
        else :    
            # normal file
            self.infile = open(self.filename, "rbU") # TODO : "U" mode only works in 2.3, is ignored in 2.1 and 2.2
            self.mustclose = 1
            return
            
        # Use a temporary file, always seekable contrary to standard input.
        # This also has the benefit to let us use the "U" mode (new in Python 2.3)
        self.infile = tempfile.TemporaryFile(mode="w+bU")   # TODO : "U" mode only works in 2.3, is ignored in 2.1 and 2.2
        while 1 :
            data = infile.read(MEGABYTE) 
            if not data :
                break
            self.infile.write(data)
        self.infile.flush()    
        self.infile.seek(0)
            
    def closeFile(self) :        
        """Closes the job's data stream if we can close it."""
        if self.mustclose :
            self.infile.close()    
        else :    
            # if we don't have to close the file, then
            # ensure the file pointer is reset to the 
            # start of the file in case the process wants
            # to read the file again.
            try :
                self.infile.seek(0)
            except :    
                pass    # probably stdin, which is not seekable
        
    def isPostScript(self, data) :    
        """Returns 1 if data is PostScript, else 0."""
        if data.startswith("%!") or \
           data.startswith("\004%!") or \
           data.startswith("\033%-12345X%!PS") or \
           ((data[:128].find("\033%-12345X") != -1) and \
             ((data.find("LANGUAGE=POSTSCRIPT") != -1) or \
              (data.find("LANGUAGE = POSTSCRIPT") != -1) or \
              (data.find("LANGUAGE = Postscript") != -1))) or \
              (data.find("%!PS-Adobe") != -1) :
            return 1
        else :    
            return 0
        
    def isPDF(self, data) :    
        """Returns 1 if data is PDF, else 0."""
        if data.startswith("%PDF-") or \
           data.startswith("\033%-12345X%PDF-") or \
           ((data[:128].find("\033%-12345X") != -1) and (data.upper().find("LANGUAGE=PDF") != -1)) or \
           (data.find("%PDF-") != -1) :
            return 1
        else :    
            return 0
        
    def isPCL(self, data) :    
        """Returns 1 if data is PCL, else 0."""
        if data.startswith("\033E\033") or \
           ((data[:128].find("\033%-12345X") != -1) and \
             ((data.find("LANGUAGE=PCL") != -1) or \
              (data.find("LANGUAGE = PCL") != -1) or \
              (data.find("LANGUAGE = Pcl") != -1))) :
            return 1
        else :    
            return 0
        
    def isPCLXL(self, data) :    
        """Returns 1 if data is PCLXL aka PCL6, else 0."""
        if ((data[:128].find("\033%-12345X") != -1) and \
             (data.find(" HP-PCL XL;") != -1) and \
             ((data.find("LANGUAGE=PCLXL") != -1) or \
              (data.find("LANGUAGE = PCLXL") != -1))) :
            return 1
        else :    
            return 0
            
    def detectPDLHandler(self) :    
        """Tries to autodetect the document format.
        
           Returns the correct PDL handler class or None if format is unknown
        """   
        # Try to detect file type by reading first block of datas    
        self.infile.seek(0)
        firstblock = self.infile.read(KILOBYTE)
        self.infile.seek(0)
        if self.isPostScript(firstblock) :
            return PostScriptAnalyzer
        elif self.isPCLXL(firstblock) :    
            return PCLXLAnalyzer
        elif self.isPCL(firstblock) :    
            return PCLAnalyzer
        elif self.isPDF(firstblock) :    
            return PDFAnalyzer
        else :    
            raise PDLAnalyzerError, "Analysis of first data block failed."
            
def main() :    
    """Entry point for PDL Analyzer."""
    if (len(sys.argv) < 2) or ((not sys.stdin.isatty()) and ("-" not in sys.argv[1:])) :
        sys.argv.append("-")
        
    totalsize = 0    
    for arg in sys.argv[1:] :
        try :
            parser = PDLAnalyzer(arg)
            totalsize += parser.getJobSize()
        except PDLAnalyzerError, msg :    
            sys.stderr.write("%s\n" % msg)
            sys.stderr.flush()
    print "%s" % totalsize
    
if __name__ == "__main__" :    
    main()        
