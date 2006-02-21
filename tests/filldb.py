#! /usr/bin/env python
# -*- coding: ISO-8859-15 -*-

# $Id$


import sys
import os
import time

def showTiming(number, before) :
    """Displays timing information."""
    elapsed = time.time() - before
    persecond = int(float(number) / elapsed)
    sys.stdout.write("\nTime elapsed : %.2f seconds (%i entries per second)\n\n" % (elapsed, persecond))
    
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
    showTiming(number, before)
    return billingcodes

def deleteBillingCodes(billingcodes) :
    """Deletes all test billing codes."""
    sys.stdout.write("Deleting billing codes...\n")
    argsfile = open("arguments.list", "w")
    argsfile.write('--delete\n')
    for bname in billingcodes :
        argsfile.write("%s\n" % bname)
    argsfile.close()    
    before = time.time()
    os.system('pkbcodes --arguments arguments.list') 
    showTiming(len(billingcodes), before)
    
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
    showTiming(number, before)
    return printernames

def deletePrinters(printernames) :
    """Deletes all test printers."""
    sys.stdout.write("Deleting printers...\n")
    argsfile = open("arguments.list", "w")
    argsfile.write('--delete\n')
    for pname in printernames :
        argsfile.write("%s\n" % pname)
    argsfile.close()    
    before = time.time()
    os.system('pkprinters --arguments arguments.list') 
    showTiming(len(printernames), before)
    
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
    os.system('pkusers --arguments arguments.list') 
    showTiming(number, before)
    return usernames

def deleteUsers(usernames) :
    """Deletes all test users."""
    sys.stdout.write("Deleting users...\n")
    argsfile = open("arguments.list", "w")
    argsfile.write('--delete\n')
    for uname in usernames :
        argsfile.write("%s\n" % uname)
    argsfile.close()    
    before = time.time()
    os.system('pkusers --arguments arguments.list') 
    showTiming(len(usernames), before)
    
def createUserPQuotas(usernames, printernames) :
    """Creates a number of user print quota entries."""
    number = len(usernames) * len(printernames)
    sys.stdout.write("Adding %i user print quota entries...\n" % number)
    argsfile = open("arguments.list", "w")
    argsfile.write('--add\n--softlimit\n100\n--hardlimit\n110\n--reset\n--hardreset\n--printer\n')
    argsfile.write("%s\n" % ",".join(printernames))
    for uname in usernames :
        argsfile.write("%s\n" % uname)
    argsfile.close()    
    before = time.time()
    os.system('edpykota --arguments arguments.list') 
    showTiming(number, before)

def deleteUserPQuotas(usernames, printernames) :
    """Deletes all test user print quota entries."""
    number = len(usernames) * len(printernames)
    sys.stdout.write("Deleting user print quota entries...\n")
    argsfile = open("arguments.list", "w")
    argsfile.write('--delete\n--printer\n')
    argsfile.write("%s\n" % ",".join(printernames))
    for uname in usernames :
        argsfile.write("%s\n" % uname)
    argsfile.close()    
    before = time.time()
    os.system('edpykota --arguments arguments.list') 
    showTiming(len(usernames), before)
    
if __name__ == "__main__" :    
    if len(sys.argv) == 1 :
        sys.stderr.write("usage :  %s  NbBillingCodes  NbPrinters  NbUsers\n" % sys.argv[0])
    else :    
        nbbillingcodes = int(sys.argv[1])
        nbprinters = int(sys.argv[2])
        nbusers = int(sys.argv[3])
        if nbbillingcodes :
            bcodes = createBillingCodes(nbbillingcodes)
        if nbprinters :
            printers = createPrinters(nbprinters)
        if nbusers :    
            users = createUsers(nbusers)
            
        if users and printers :    
            createUserPQuotas(users, printers)
            deleteUserPQuotas(users, printers)
            
        if bcodes :    
            deleteBillingCodes(bcodes)
        if users :    
            deleteUsers(users)           # NB : either this one or the one below
        if printers :    
            deletePrinters(printers)     # also delete user print quota entries.
        os.remove("arguments.list")
        
