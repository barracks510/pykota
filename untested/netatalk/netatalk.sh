#! /bin/sh
#
# $Id$
#
# The following was adapted from a post found on usenet, 
# it works with my Apple LaserWriter 16/600 PS.
# As always, YMMV.
# 
/usr/bin/pap -p "MyPrinter:LaserWriter" pagecount.ps 2>/dev/null | grep -v status | grep -v Connect

