#! /usr/bin/env python
# -*- coding: ISO-8859-15 -*-

# $Id$


import sys
import os
import time

def createBillingCodes(number) :
    """Creates a number of billing codes."""
    sys.stdout.write("Adding %i billing codes...\n" % number)
    billingcodes = [ "test-billingcode-%05i" % i for i in range(number) ]
    argsfile = open("arguments.list", "w")
    argsfile.write('--add\n--reset\n--description\n"a billing code"\n')
    for bname in billingcodes :
        argsfile.write("%s\n" % bname)
    argsfile.close()    
    before = time.time()
    os.system('pkbcodes --arguments arguments.list') 
    after = time.time()
    sys.stdout.write("\nTime elapsed : %.2f seconds\n\n" % (after - before))

def deleteBillingCodes() :
    """Deletes all test billing codes."""
    sys.stdout.write("Deleting billing codes...\n")
    before = time.time()
    os.system('pkbcodes --delete "test-billingcode-*"') 
    after = time.time()
    sys.stdout.write("\nTime elapsed : %.2f seconds\n\n" % (after - before))
    
def createPrinters(number) :
    """Creates a number of printers."""
    sys.stdout.write("Adding %i printers...\n" % number)
    printernames = [ "test-printer-%05i" % i for i in range(number) ]
    argsfile = open("arguments.list", "w")
    argsfile.write('--add\n--charge\n0.05\n--maxjobsize\n5\n--passthrough\n--description\n"a printer"\n')
    for pname in printernames :
        argsfile.write("%s\n" % pname)
    argsfile.close()    
    before = time.time()
    os.system('pkprinters --arguments arguments.list') 
    after = time.time()
    sys.stdout.write("\nTime elapsed : %.2f seconds\n\n" % (after - before))

def deletePrinters() :
    """Deletes all test printers."""
    sys.stdout.write("Deleting printers...\n")
    before = time.time()
    os.system('pkprinters --delete "test-printer-*"') 
    after = time.time()
    sys.stdout.write("\nTime elapsed : %.2f seconds\n\n" % (after - before))
    
def createUsers(number) :
    """Creates a number of users."""
    sys.stdout.write("Adding %i users...\n" % number)
    usernames = [ "test-user-%05i" % i for i in range(number) ]
    argsfile = open("arguments.list", "w")
    argsfile.write('--add\n--limitby\nbalance\n--balance\n50.0\n')
    for uname in usernames :
        argsfile.write("%s\n" % uname)
    argsfile.close()    
    before = time.time()
    os.system('edpykota --arguments arguments.list') 
    after = time.time()
    sys.stdout.write("\nTime elapsed : %.2f seconds\n\n" % (after - before))

def deleteUsers() :
    """Deletes all test users."""
    sys.stdout.write("Deleting users...\n")
    before = time.time()
    os.system('edpykota --delete "test-user-*"') 
    after = time.time()
    sys.stdout.write("\nTime elapsed : %.2f seconds\n\n" % (after - before))
    
if __name__ == "__main__" :    
    if len(sys.argv) == 1 :
        sys.stderr.write("usage :  %s  NbBillingCodes  NbPrinters  NbUsers\n" % sys.argv[0])
    else :    
        nbbillingcodes = int(sys.argv[1])
        nbprinters = int(sys.argv[2])
        nbusers = int(sys.argv[3])
        if nbbillingcodes :
            createBillingCodes(nbbillingcodes)
        if nbprinters :
            createPrinters(nbprinters)
        if nbusers :    
            createUsers(nbusers)
        if nbbillingcodes :    
            deleteBillingCodes()
        if nbusers :    
            deleteUsers()           # NB : either this one or the one below
        if nbprinters :    
            deletePrinters()        # also delete user print quota entries.
        os.remove("arguments.list")
        
