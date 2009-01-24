# -*- coding: utf-8 -*-*-
#
# PyKota : Print Quotas for CUPS
#
# (c) 2003-2009 Jerome Alet <alet@librelogiciel.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# $Id$
#

"""This module implements some CUPS specific classes."""

from pykota.errors import PyKotaToolError
try :
    from pkipplib import pkipplib
except ImportError :
    raise RuntimeError, "The python-pkipplib module is now mandatory. You can download pkipplib from http://www.pykota.com/"

class JobTicket :
    """A class to hold CUPS print job informations."""
    def __init__(self, jobid=None, printername=None, copies=1, filename=None, \
                       options=None) :
        """Initializes a print job's information."""
        self.JobId = jobid
        self.PrinterName = printername
        self.Copies = copies
        self.FileName = filename
        self.Options = options
        self.Charset = None
        self.OriginatingUserName = None
        self.OriginalUserName = None
        self.Title = None
        self.BillingCode = None
        self.OriginatingHostName = None
        self.TimeAtCreation = None
        self.TimeAtProcessing = None
        self.MimeType = None
        self.UUID = None
        if self.JobId is not None :
            self.retrieveAttributesFromCUPS()

    def getAttributeTypeAndValue(self, ippanswer, attribute, category="job") :
        """Retrieves a particular attribute's type and value from an IPP answer.

           Returns a tuple of the form (type, value).
        """
        try :
            return getattr(ippanswer, category)[attribute][0]
        except KeyError :
            return (None, None)

    def retrieveAttributesFromCUPS(self) :
        """Retrieve attribute's values from CUPS."""
        server = pkipplib.CUPS() # TODO : username and password and/or encryption
        answer = server.getJobAttributes(self.JobId)
        if answer is None :
            raise PyKotaToolError, "Network error while querying the CUPS server : %s" \
                                      % server.lastErrorMessage
        (dummy, self.Charset) = self.getAttributeTypeAndValue(answer, "attributes-charset", "operation")
        (dummy, self.OriginatingUserName) = self.getAttributeTypeAndValue(answer, "job-originating-user-name")
        (dummy, self.Title) = self.getAttributeTypeAndValue(answer, "job-name")
        (dummy, self.BillingCode) = self.getAttributeTypeAndValue(answer, "job-billing")
        (dummy, self.OriginatingHostName) = self.getAttributeTypeAndValue(answer, "job-originating-host-name")
        (dummy, self.UUID) = self.getAttributeTypeAndValue(answer, "job-uuid")
        (dummy, self.TimeAtCreation) = self.getAttributeTypeAndValue(answer, "time-at-creation")
        (dummy, self.TimeAtProcessing) = self.getAttributeTypeAndValue(answer, "time-at-processing")
        (dummy, self.MimeType) = self.getAttributeTypeAndValue(answer, "document-format")

        for attrib in ("OriginatingUserName",
                       "OriginatingHostName",
                       "Title",
                       "BillingCode",
                       "PrinterName",
                       "Options",
                       "Charset",
                       "UUID",
                       "MimeType") :
            try :
                setattr(self, attrib,
                              getattr(self, attrib).decode("UTF-8", "replace"))
            except AttributeError :
                pass

        self.OriginalUserName = self.OriginatingUserName[:]

if __name__ == "__main__" :
    import sys
    if len(sys.argv) != 2 :
        sys.stderr.write("usage : python cups.py jobid\n")
    else :
        job = JobTicket(int(sys.argv[1]), "FakePrinter")
        for attribute in ("PrinterName", "Charset", "JobId", "Copies",
                          "FileName", "OriginatingUserName",
                          "Title", "BillingCode", "OriginatingHostName",
                          "TimeAtCreation", "TimeAtProcessing", "UUID",
                          "MimeType") :
            sys.stdout.write("%s : %s\n" % (attribute, repr(getattr(job, attribute))))
