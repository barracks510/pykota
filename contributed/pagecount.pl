#!/usr/bin/perl -U
#
# PyKota : Print Quotas for CUPS and LPRng
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
#
############################################################
#                                                          #
# This script is 100% copyright (c) 2003 René Lund Jensen  #
#                                                          #
# He contributed it to the PyKota project on Dec. 4th 2003 #
# and licensed it under the terms of the GNU GPL.          #
#                                                          #
# MANY THANKS TO HIM                                       #
#                                                          #
############################################################
#
#
# $Id$
#
# $Log$
# Revision 1.2  2004/01/08 14:10:32  jalet
# Copyright year changed.
#
# Revision 1.1  2003/12/27 16:57:42  uid67467
# Added Perl script which does PJL accounting, contributed by René Lund Jensen
#
# Revision 1.1  2003/12/06 09:03:43  jalet
# Added Perl script to retrieve printer's internal page counter via PJL,
# contributed by René Lund Jensen.
#
#
#

use Socket;
use IO::Socket;

if (@ARGV < 2){
    print "usage: pagecount.pl servername port\n";
}

$printer = @ARGV[0];
$port    = @ARGV[1];

$ssh = osocket($printer, $port);
if ($ssh){
    $page = pagecount($ssh);
    print $page."\n";
    $ssh-close();
    exit(0);
}else {
    exit(1);
}

sub pagecount {
    my $sh = @_[0];    # Get sockethandle
    # send pagequery to sockethandle
    send($sh, "\033%-12345X\@PJL INFO PAGECOUNT\r\n",0);
    # Read response from sockethandle
    recv($sh,$RESPONSE,0xFFFFF,0);
    (my $junk,$pc) = split (/\r\n/s,$RESPONSE); # Find the pagecount
    $pc =~ s/(PAGECOUNT=)?([0-9]+)/$2/g;
    return $pc;                                 # Return pagecount
}


sub osocket {

 # Connecting to @_[0] = @arg[1] = $printer
 # On port @_[1] = 9100 JetDirect port
 # Using TCP protocol
    my $sh= new IO::Socket::INET(PeerAddr => @_[0],
                                 PeerPort => @_[1], 
                                 Proto => 'tcp');
    if (!defined($sh)) {        # Did we open the socket?
        return undef;           # No! return undef
    } else {                    # Yes!
        $sh->sockopt(SO_KEEPALIVE,1);   # Set socket option SO_KEEPALIVE
        return $sh;             # return sockethandle
    }
}
