#! /bin/sh
# $Id$
echo WARNING : This is dangerous !
echo WARNING : You may loose your PyKota Quota Storage contents.
echo WARNING : If unsure press Ctrl+C NOW TO STOP, else press ENTER TO PROCEED
read

echo This script does not work at all yet !
echo Please be patient so that I can write a safe upgrade script
echo of completely drop your existing database to start anew
echo with this version of PyKota.

#echo -n Update begins...
#pg_dump -D -N -U postgres -f pykotadb-full.dump pykota >upgrade.messages 2>upgrade.errors
#pg_dump -a -D -N -U postgres -f pykotadb.dump pykota >>upgrade.messages 2>>upgrade.errors
#dropdb pykota >>upgrade.messages 2>>upgrade.errors
#dropuser pykotaadmin >>upgrade.messages 2>>upgrade.errors
#dropuser pykotauser >>upgrade.messages 2>>upgrade.errors
#psql -U postgres template1 -f pykota-postgresql.sql >>upgrade.messages 2>>upgrade.errors
#psql -U postgres pykota -f pykotadb.dump >>upgrade.messages 2>>upgrade.errors
#echo
#echo Done !
#echo Check the files upgrade.messages and upgrade.errors to see if all is OK.
#echo NOTICE messages are normal and expected. In case other message types
#echo are found in upgrade.errors, please file a bug report and restore
#echo your database from pykotadb-full.dump
