#!/bin/sh
# Run this to generate all the initial makefiles, etc.

srcdir=`dirname $0`
test -z "$srcdir" && srcdir=.

ORIGDIR=`pwd`
cd $srcdir

 PROJECT=pykota

 CONFIGURE=configure.in

 TEST_TYPE=-f
 
 DIE=0


 for autoconf in autoconf autoconf-2.57 autoconf-2.56 autoconf-2.55 autoconf-2.54 autoconf-2.53 autoconf-2.52 ; do
 	if "$autoconf" --version < /dev/null > /dev/null 2>&1 ; then
 		version=`"$autoconf" --version | head -1 | awk '{print $NF}'`
 		acmajor=`echo "$version" | cut -f1 -d.`
 		acminor=`echo "$version" | cut -f2 -d.`
 		if test "$acmajor" -gt 3 ; then
 			break
 		fi
 		if test "$acmajor" -ge 2 ; then
 			if test "$acminor" -ge 50 ; then
 				break
 			fi
 		fi
 	fi
 done
 if ! "$autoconf" --version < /dev/null > /dev/null 2>&1 ; then

 	echo

 	echo "You must have autoconf 2.52 installed to compile $PROJECT."

 	echo "Install the appropriate package for your distribution,"

 	echo "or get the source tarball at ftp://ftp.gnu.org/pub/gnu/"

 	DIE=1

 fi
 autoheader=`echo "$autoconf" | sed s,autoconf,autoheader,g`

 have_automake=false

 for automakev in 1.7 1.6 ; do

 	if automake-$automakev --version < /dev/null > /dev/null 2>&1 ; then

 		have_automake=true

 		break;
 	fi
 done

 if $have_automake ; then : ; else
 	echo

 	echo "You must have automake 1.6 installed to compile $PROJECT."
 	echo "Get ftp://ftp.gnu.org/pub/gnu/automake/automake-1.6.tar.gz"

 	echo "(or a newer version if it is available)"
 	DIE=1
 fi
 
 if test "$DIE" -eq 1; then
 	exit 1
 fi
 
 if test -z "$AUTOGEN_SUBDIR_MODE"; then
         if test -z "$*"; then
                 echo "I am going to run ./configure with no arguments - if you wish "
                 echo "to pass any to it, please specify them on the $0 command line."
         fi
 fi
 
 case $CC in
 *xlc | *xlc\ * | *lcc | *lcc\ *) am_opt=--include-deps;;
 esac

 if grep "^AM_[A-Z0-9_]\{1,\}_GETTEXT" "$CONFIGURE" >/dev/null; then
  if grep "sed.*POTFILES" "$CONFIGURE" >/dev/null; then
    GETTEXTIZE=""
  else
    if grep "^AM_GLIB_GNU_GETTEXT" "$CONFIGURE" >/dev/null; then
      GETTEXTIZE="glib-gettextize"
      GETTEXTIZE_URL="ftp://ftp.gtk.org/pub/gtk/v2.0/glib-2.0.0.tar.gz"
    else
      GETTEXTIZE="gettextize"
      GETTEXTIZE_URL="ftp://alpha.gnu.org/gnu/gettext-0.10.35.tar.gz"
    fi
                                                                                                                                                                                   
    $GETTEXTIZE --version < /dev/null > /dev/null 2>&1
    if test $? -ne 0; then
      echo
      echo "**Error**: You must have \`$GETTEXTIZE' installed to compile $PKG_NAME."
      echo "Get $GETTEXTIZE_URL"
      echo "(or a newer version if it is available)"
      DIE=1
    fi
  fi
fi


 touch config.h.in

 echo "running autopoint --force --copy"
 autopoint --force 

 echo "running aclocal-$automakev $ACLOCAL_FLAGS"
 aclocal-$automakev $ACLOCAL_FLAGS

 echo "running $autoheader"
 $autoheader

 echo "running automake-$automakev -a -c $am_opt --foreign"
 automake-$automakev -a -c $am_opt --foreign

 echo "$autoconf"
 $autoconf

 cd $ORIGDIR
 
 if test -z "$AUTOGEN_SUBDIR_MODE"; then
    $srcdir/configure --enable-maintainer-mode "$@"

 	chmod -Rf u+w $srcdir

    echo 
    echo "Now type 'make' to compile $PROJECT."

 fi

