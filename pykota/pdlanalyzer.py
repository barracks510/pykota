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
# Revision 1.36  2004/09/01 22:31:49  jalet
# Some more work on ESC/P2 analyzer to avoid missing \r\n sequences. Not
# exactly optimal though...
#
# Revision 1.35  2004/08/30 23:10:24  jalet
# Improved the ESC/P2 analyzer so that more GhostScript devices are supported
#
# Revision 1.34  2004/08/27 09:08:22  jalet
# Improvement in PostScript parser to avoid being fooled by clever "students"
#
# Revision 1.33  2004/08/27 09:02:34  jalet
# Forgot to remove some special debugging code...
#
# Revision 1.32  2004/08/27 08:58:50  jalet
# Relax checks for PCL5 header to accomodate strange printer drivers
#
# Revision 1.31  2004/08/22 08:25:33  jalet
# Improved ESC/P2 miniparser thanks to Paulo Silva
#
# Revision 1.30  2004/08/21 23:16:57  jalet
# First draft of ESC/P2 (mini-)parser.
#
# Revision 1.29  2004/08/11 16:25:38  jalet
# Fixed index problem in PCLXL parser when retrieving number of copies for
# each page
#
# Revision 1.28  2004/08/10 23:01:49  jalet
# Fixed number of copies in PCL5 parser
#
# Revision 1.27  2004/08/09 18:14:22  jalet
# Added workaround for number of copies and some PostScript drivers
#
# Revision 1.26  2004/07/22 13:49:51  jalet
# Added support for binary PostScript through GhostScript if native DSC
# compliant PostScript analyzer doesn't find any page. This is much
# slower though, so native analyzer is tried first.
#
# Revision 1.25  2004/07/10 14:06:36  jalet
# Fix for Python2.1 incompatibilities
#
# Revision 1.24  2004/07/05 21:00:39  jalet
# Fix for number of copies for each page in PCLXL parser
#
# Revision 1.23  2004/07/03 08:21:59  jalet
# Testsuite for PDL Analyzer added
#
# Revision 1.22  2004/06/29 14:21:41  jalet
# Smallish optimization
#
# Revision 1.21  2004/06/28 23:11:26  jalet
# Code de-factorization in PCLXL parser
#
# Revision 1.20  2004/06/28 22:38:41  jalet
# Increased speed by a factor of 2 in PCLXL parser
#
# Revision 1.19  2004/06/28 21:20:30  jalet
# PCLXL support now works !
#
# Revision 1.18  2004/06/27 22:59:37  jalet
# More work on PCLXL parser
#
# Revision 1.17  2004/06/26 23:20:01  jalet
# Additionnal speedup for GhostScript generated PCL5 files
#
# Revision 1.16  2004/06/26 15:31:00  jalet
# mmap reintroduced in PCL5 parser
#
# Revision 1.15  2004/06/26 14:14:31  jalet
# Now uses Psyco if it is available
#
# Revision 1.14  2004/06/25 09:50:28  jalet
# More debug info in PCLXL parser
#
# Revision 1.13  2004/06/25 08:10:08  jalet
# Another fix for PCL5 parser
#
# Revision 1.12  2004/06/24 23:09:53  jalet
# Fix for number of copies in PCL5 parser
#
# Revision 1.11  2004/06/23 22:07:50  jalet
# Fixed PCL5 parser according to the sources of rastertohp
#
# Revision 1.10  2004/06/18 22:24:03  jalet
# Removed old comments
#
# Revision 1.9  2004/06/18 22:21:27  jalet
# Native PDF parser greatly improved.
# GhostScript based PDF parser completely removed because native code
# is now portable across Python versions.
#
# Revision 1.8  2004/06/18 20:49:46  jalet
# "ERROR:" prefix added
#
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
import re
from struct import unpack
import tempfile
import mmap
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
        self.copies = 1
       
    def throughGhostScript(self) :
        """Get the count through GhostScript, useful for non-DSC compliant PS files."""
        self.infile.seek(0)
        command = 'gs -sDEVICE=bbox -dNOPAUSE -dBATCH -dQUIET - 2>&1 | grep -c "%%HiResBoundingBox:" 2>/dev/null'
        child = popen2.Popen4(command)
        try :
            data = self.infile.read(MEGABYTE)    
            while data :
                child.tochild.write(data)
                data = self.infile.read(MEGABYTE)
            child.tochild.flush()
            child.tochild.close()    
        except (IOError, OSError), msg :    
            raise PDLAnalyzerError, "Problem during analysis of Binary PostScript document."
            
        pagecount = 0
        try :
            pagecount = int(child.fromchild.readline().strip())
        except (IOError, OSError, AttributeError, ValueError) :
            raise PDLAnalyzerError, "Problem during analysis of Binary PostScript document."
        child.fromchild.close()
        
        try :
            retcode = child.wait()
        except OSError, msg :    
            raise PDLAnalyzerError, "Problem during analysis of Binary PostScript document."
        return pagecount * self.copies
        
    def natively(self) :
        """Count pages in a DSC compliant PostScript document."""
        self.infile.seek(0)
        pagecount = 0
        for line in self.infile.xreadlines() : 
            if line.startswith("%%Page: ") :
                pagecount += 1
            elif line.startswith("%%BeginNonPPDFeature: NumCopies ") :
                # handle # of copies set by some Windows printer driver
                try :
                    number = int(line.strip().split()[2])
                except :     
                    pass
                else :    
                    if number > self.copies :
                        self.copies = number
            elif line.startswith("1 dict dup /NumCopies ") :
                # handle # of copies set by mozilla/kprinter
                try :
                    number = int(line.strip().split()[4])
                except :     
                    pass
                else :    
                    if number > self.copies :
                        self.copies = number
        return pagecount * self.copies
        
    def getJobSize(self) :    
        """Count pages in PostScript document."""
        return self.natively() or self.throughGhostScript()
        
class PDFAnalyzer :
    def __init__(self, infile) :
        """Initialize PDF Analyzer."""
        self.infile = infile
                
    def getJobSize(self) :    
        """Counts pages in a PDF document."""
        regexp = re.compile(r"(/Type) ?(/Page)[/ \t\r\n]")
        pagecount = 0
        for line in self.infile.xreadlines() : 
            pagecount += len(regexp.findall(line))
        return pagecount    
        
class ESCP2Analyzer :
    def __init__(self, infile) :
        """Initialize ESC/P2 Analyzer."""
        self.infile = infile
                
    def getJobSize(self) :    
        """Counts pages in an ESC/P2 document."""
        # with Gimpprint, at least, for each page there
        # are two Reset Printer sequences (ESC + @)
        marker1 = "\033@"
        
        # with other software or printer driver, we
        # may prefer to search for "\r\n\fESCAPE"
        # or "\r\fESCAPE"
        marker2r = "\r\f\033"
        marker2rn = "\r\n\f\033"
        
        # and ghostscript's stcolor for example seems to
        # output ESC + @ + \f for each page plus one
        marker3 = "\033@\f"
        
        # while ghostscript's escp driver outputs instead
        # \f + ESC + @
        marker4 = "\f\033@"
        
        data = self.infile.read()
        pagecount1 = data.count(marker1)
        pagecount2 = max(data.count(marker2r), data.count(marker2rn))
        pagecount3 = data.count(marker3)
        pagecount4 = data.count(marker4)
            
        if pagecount2 :    
            return pagecount2
        elif pagecount3 > 1 :     
            return pagecount3 - 1
        elif pagecount4 :    
            return pagecount4
        else :    
            return int(pagecount1 / 2)       
        
class PCLAnalyzer :
    def __init__(self, infile) :
        """Initialize PCL Analyzer."""
        self.infile = infile
        
    def getJobSize(self) :     
        """Count pages in a PCL5 document.
         
           Should also work for PCL3 and PCL4 documents.
           
           Algorithm from pclcount
           (c) 2003, by Eduardo Gielamo Oliveira & Rodolfo Broco Manin 
           published under the terms of the GNU General Public Licence v2.
          
           Backported from C to Python by Jerome Alet, then enhanced
           with more PCL tags detected. I think all the necessary PCL tags
           are recognized to correctly handle PCL5 files wrt their number
           of pages. The documentation used for this was :
         
           HP PCL/PJL Reference Set
           PCL5 Printer Language Technical Quick Reference Guide
           http://h20000.www2.hp.com/bc/docs/support/SupportManual/bpl13205/bpl13205.pdf 
        """
        infileno = self.infile.fileno()
        minfile = mmap.mmap(infileno, os.fstat(infileno)[6], prot=mmap.PROT_READ, flags=mmap.MAP_SHARED)
        tagsends = { "&n" : "W", 
                     "&b" : "W", 
                     "*i" : "W", 
                     "*l" : "W", 
                     "*m" : "W", 
                     "*v" : "W", 
                     "*c" : "W", 
                     "(f" : "W", 
                     "(s" : "W", 
                     ")s" : "W", 
                     "&p" : "X", 
                     "&l" : "XH",
                     "&a" : "G",
                     # "*b" : "VW", # treated specially because it occurs very often
                   }  
        pagecount = resets = ejects = backsides = 0
        tag = None
        copies = {}
        pos = 0
        try :
            while 1 :
                char = minfile[pos] ; pos += 1
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
                    #     <ESC>&l###X -> Number of copies for current page
                    #     <ESC>&n###W -> Starts an alphanumeric string ID block
                    #     <ESC>&p###X -> Start of a non printable characters block
                    #     <ESC>&a2G -> Back side when duplex mode as generated by rastertohp
                    #     <ESC>&l0H -> Eject if NumPlanes > 1, as generated by rastertohp
                    #
                    tagstart = minfile[pos] ; pos += 1
                    if tagstart in "E9=YZ" : # one byte PCL tag
                        if tagstart == "E" :
                            resets += 1
                        continue             # skip to next tag
                    tag = tagstart + minfile[pos] ; pos += 1
                    if tag == "*b" : 
                        tagend = "VW"
                    else :    
                        try :
                            tagend = tagsends[tag]
                        except KeyError :    
                            continue # Unsupported PCL tag
                    # Now read the numeric argument
                    size = 0
                    while 1 :
                        char = minfile[pos] ; pos += 1
                        if not char.isdigit() :
                            break
                        size = (size * 10) + int(char)    
                    if char in tagend :    
                        if (tag == "&l") and (char == "X") : # copies for current page
                            copies[pagecount] = size
                        elif (tag == "&l") and (char == "H") and (size == 0) :    
                            ejects += 1         # Eject 
                        elif (tag == "&a") and (size == 2) :
                            backsides += 1      # Back side in duplex mode
                        else :    
                            # we just ignore the block.
                            if tag == "&n" : 
                                # we have to take care of the operation id byte
                                # which is before the string itself
                                size += 1
                            pos += size    
        except IndexError : # EOF ?
            minfile.close() # reached EOF
                            
        # if pagecount is still 0, we will use the number
        # of resets instead of the number of form feed characters.
        # but the number of resets is always at least 2 with a valid
        # pcl file : one at the very start and one at the very end
        # of the job's data. So we substract 2 from the number of
        # resets. And since on our test data we needed to substract
        # 1 more, we finally substract 3, and will test several
        # PCL files with this. If resets < 2, then the file is
        # probably not a valid PCL file, so we use 0
        if not pagecount :
            pagecount = (pagecount or ((resets - 3) * (resets > 2)))
        else :    
            # here we add counters for other ways new pages may have
            # been printed and ejected by the printer
            pagecount += ejects + backsides
        
        # now handle number of copies for each page (may differ).
        # in duplex mode, number of copies may be sent only once.
        for pnum in range(pagecount) :
            # if no number of copies defined, take the preceding one else the one set before any page else 1.
            nb = copies.get(pnum, copies.get(pnum-1, copies.get(0, 1)))
            pagecount += (nb - 1)
        return pagecount
        
class PCLXLAnalyzer :
    def __init__(self, infile) :
        """Initialize PCLXL Analyzer."""
        self.infile = infile
        self.endianness = None
        found = 0
        while not found :
            line = self.infile.readline()
            if not line :
                break
            if line[1:12] == " HP-PCL XL;" :
                found = 1
                endian = ord(line[0])
                if endian == 0x29 :
                    self.littleEndian()
                elif endian == 0x28 :    
                    self.bigEndian()
                # elif endian == 0x27 : TODO : What can we do here ?    
                # 
                else :    
                    raise PDLAnalyzerError, "Unknown endianness marker 0x%02x at start !" % endian
        if not found :
            raise PDLAnalyzerError, "This file doesn't seem to be PCLXL (aka PCL6)"
        else :    
            # Initialize table of tags
            self.tags = [ 0 ] * 256    
            
            # GhostScript's sources tell us that HP printers
            # only accept little endianness, but we can handle both.
            self.tags[0x28] = self.bigEndian    # BigEndian
            self.tags[0x29] = self.littleEndian # LittleEndian
            
            self.tags[0x43] = self.beginPage    # BeginPage
            self.tags[0x44] = self.endPage      # EndPage
            
            self.tags[0xc0] = 1 # ubyte
            self.tags[0xc1] = 2 # uint16
            self.tags[0xc2] = 4 # uint32
            self.tags[0xc3] = 2 # sint16
            self.tags[0xc4] = 4 # sint32
            self.tags[0xc5] = 4 # real32
            
            self.tags[0xc8] = self.array_8  # ubyte_array
            self.tags[0xc9] = self.array_16 # uint16_array
            self.tags[0xca] = self.array_32 # uint32_array
            self.tags[0xcb] = self.array_16 # sint16_array
            self.tags[0xcc] = self.array_32 # sint32_array
            self.tags[0xcd] = self.array_32 # real32_array
            
            self.tags[0xd0] = 2 # ubyte_xy
            self.tags[0xd1] = 4 # uint16_xy
            self.tags[0xd2] = 8 # uint32_xy
            self.tags[0xd3] = 4 # sint16_xy
            self.tags[0xd4] = 8 # sint32_xy
            self.tags[0xd5] = 8 # real32_xy
            
            self.tags[0xe0] = 4  # ubyte_box
            self.tags[0xe1] = 8  # uint16_box
            self.tags[0xe2] = 16 # uint32_box
            self.tags[0xe3] = 8  # sint16_box
            self.tags[0xe4] = 16 # sint32_box
            self.tags[0xe5] = 16 # real32_box
            
            self.tags[0xf8] = 1 # attr_ubyte
            self.tags[0xf9] = 2 # attr_uint16
            
            self.tags[0xfa] = self.embeddedData      # dataLength
            self.tags[0xfb] = self.embeddedDataSmall # dataLengthByte
            
    def beginPage(self) :
        """Indicates the beginning of a new page."""
        self.pagecount += 1
        return 0
        
    def endPage(self) :    
        """Indicates the end of a page."""
        pos = self.pos
        minfile = self.minfile
        if (ord(minfile[pos-3]) == 0xf8) and (ord(minfile[pos-2]) == 0x31) :
            # The EndPage operator is preceded by a PageCopies attribute
            # So set number of copies for current page.
            # From what I read in PCLXL documentation, the number
            # of copies is an unsigned 16 bits integer
            self.copies[self.pagecount] = unpack(self.endianness + "H", minfile[pos-5:pos-3])[0]
        return 0
        
    def array_8(self) :    
        """Handles byte arrays."""
        pos = self.pos
        datatype = self.minfile[pos]
        pos += 1
        length = self.tags[ord(datatype)]
        if callable(length) :
            self.pos = pos
            length = length()
            pos = self.pos
        posl = pos + length
        self.pos = posl
        if length == 1 :    
            return unpack("B", self.minfile[pos:posl])[0]
        elif length == 2 :    
            return unpack(self.endianness + "H", self.minfile[pos:posl])[0]
        elif length == 4 :    
            return unpack(self.endianness + "I", self.minfile[pos:posl])[0]
        else :    
            raise PDLAnalyzerError, "Error on array size at %s" % self.pos
        
    def array_16(self) :    
        """Handles byte arrays."""
        pos = self.pos
        datatype = self.minfile[pos]
        pos += 1
        length = self.tags[ord(datatype)]
        if callable(length) :
            self.pos = pos
            length = length()
            pos = self.pos
        posl = pos + length
        self.pos = posl
        if length == 1 :    
            return 2 * unpack("B", self.minfile[pos:posl])[0]
        elif length == 2 :    
            return 2 * unpack(self.endianness + "H", self.minfile[pos:posl])[0]
        elif length == 4 :    
            return 2 * unpack(self.endianness + "I", self.minfile[pos:posl])[0]
        else :    
            raise PDLAnalyzerError, "Error on array size at %s" % self.pos
        
    def array_32(self) :    
        """Handles byte arrays."""
        pos = self.pos
        datatype = self.minfile[pos]
        pos += 1
        length = self.tags[ord(datatype)]
        if callable(length) :
            self.pos = pos
            length = length()
            pos = self.pos
        posl = pos + length
        self.pos = posl
        if length == 1 :    
            return 4 * unpack("B", self.minfile[pos:posl])[0]
        elif length == 2 :    
            return 4 * unpack(self.endianness + "H", self.minfile[pos:posl])[0]
        elif length == 4 :    
            return 4 * unpack(self.endianness + "I", self.minfile[pos:posl])[0]
        else :    
            raise PDLAnalyzerError, "Error on array size at %s" % self.pos
        
    def embeddedDataSmall(self) :
        """Handle small amounts of data."""
        pos = self.pos
        length = ord(self.minfile[pos])
        self.pos = pos + 1
        return length
        
    def embeddedData(self) :
        """Handle normal amounts of data."""
        pos = self.pos
        pos4 = pos + 4
        self.pos = pos4
        return unpack(self.endianness + "I", self.minfile[pos:pos4])[0]
        
    def littleEndian(self) :        
        """Toggles to little endianness."""
        self.endianness = "<" # little endian
        return 0
        
    def bigEndian(self) :    
        """Toggles to big endianness."""
        self.endianness = ">" # big endian
        return 0
    
    def getJobSize(self) :
        """Counts pages in a PCLXL (PCL6) document.
        
           Algorithm by Jerome Alet.
           
           The documentation used for this was :
         
           HP PCL XL Feature Reference
           Protocol Class 2.0
           http://www.hpdevelopersolutions.com/downloads/64/358/xl_ref20r22.pdf 
        """
        infileno = self.infile.fileno()
        self.copies = {}
        self.minfile = minfile = mmap.mmap(infileno, os.fstat(infileno)[6], prot=mmap.PROT_READ, flags=mmap.MAP_SHARED)
        tags = self.tags
        self.pagecount = 0
        self.pos = pos = self.infile.tell()
        try :
            while 1 :
                char = minfile[pos]
                pos += 1
                length = tags[ord(char)]
                if not length :
                    continue
                if callable(length) :    
                    self.pos = pos
                    length = length()
                    pos = self.pos
                pos += length    
        except IndexError : # EOF ?
            self.minfile.close() # reached EOF
            
        # now handle number of copies for each page (may differ).
        for pnum in range(1, self.pagecount + 1) :
            # if no number of copies defined, take 1, as explained
            # in PCLXL documentation.
            # NB : is number of copies is 0, the page won't be output
            # but the formula below is still correct : we want 
            # to decrease the total number of pages in this case.
            self.pagecount += (self.copies.get(pnum, 1) - 1)
            
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
        try :
            import psyco 
        except ImportError :    
            pass # Psyco is not installed
        else :    
            # Psyco is installed, tell it to compile
            # the CPU intensive methods : PCL and PCLXL
            # parsing will greatly benefit from this, 
            # for PostScript and PDF the difference is
            # barely noticeable since they are already
            # almost optimal, and much more speedy anyway.
            psyco.bind(PostScriptAnalyzer.getJobSize)
            psyco.bind(PDFAnalyzer.getJobSize)
            psyco.bind(ESCP2Analyzer.getJobSize)
            psyco.bind(PCLAnalyzer.getJobSize)
            psyco.bind(PCLXLAnalyzer.getJobSize)
        
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
            self.infile = open(self.filename, "rb")
            self.mustclose = 1
            return
            
        # Use a temporary file, always seekable contrary to standard input.
        self.infile = tempfile.TemporaryFile(mode="w+b")
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
           (data[:128].find("\033%-12345X") != -1) :
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
            
    def isESCP2(self, data) :        
        """Returns 1 if data is ESC/P2, else 0."""
        if data.startswith("\033@") or \
           data.startswith("\033*") or \
           data.startswith("\n\033@") :
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
        elif self.isPDF(firstblock) :    
            return PDFAnalyzer
        elif self.isPCL(firstblock) :    
            return PCLAnalyzer
        elif self.isESCP2(firstblock) :    
            return ESCP2Analyzer
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
            sys.stderr.write("ERROR: %s\n" % msg)
            sys.stderr.flush()
    print "%s" % totalsize
    
if __name__ == "__main__" :    
    main()
