#! /bin/sh
# $Id$
echo WARNING : This is dangerous !
echo WARNING : You may loose your PyKota Quota Storage contents.
echo WARNING : If unsure press Ctrl+C NOW TO STOP, else press ENTER TO PROCEED
read
echo -n Update begins...
pg_dump -D -N -U postgres -f pykotadb-full.dump pykota >update.messages 2>update.errors
pg_dump -a -D -N -U postgres -f pykotadb.dump pykota >>update.messages 2>>update.errors
dropdb pykota >>update.messages 2>>update.errors
dropuser pykotaadmin >>update.messages 2>>update.errors
dropuser pykotauser >>update.messages 2>>update.errors
psql -U postgres template1 -f pykota-postgresql.sql >>update.messages 2>>update.errors
psql -U postgres pykota -f pykotadb.dump >>update.messages 2>>update.errors
echo
echo Done !
echo Check the files update.messages and update.errors to see if all is OK.
echo NOTICE messages are normal and expected. In case other message types
echo are found in update.errors, please file a bug report and restore
echo your database from pykotadb-full.dump
