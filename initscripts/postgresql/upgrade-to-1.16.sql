--
-- PyKota - Print Quotas for CUPS and LPRng
--
-- (c) 2003-2004 Jerome Alet <alet@librelogiciel.com>
-- This program is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
-- 
-- You should have received a copy of the GNU General Public License
-- along with this program; if not, write to the Free Software
-- Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
--
-- $Id$
--
-- $Log$
-- Revision 1.4  2004/01/08 14:10:32  jalet
-- Copyright year changed.
--
-- Revision 1.3  2003/12/27 16:49:25  uid67467
-- Should be ok now.
--
-- Revision 1.2  2003/11/23 19:01:36  jalet
-- Job price added to history
--
-- Revision 1.1  2003/11/21 14:29:14  jalet
-- Forgot to add this file...
--
--
--
-- This script has to be used if you already
-- have a pre-1.16 version of PyKota to upgrade
-- your database schema. 
--
-- YOU DON'T NEED TO USE IT IF YOU'VE JUST INSTALLED PYKOTA
--
                        
--                         
-- WARNING : YOU NEED A RECENT VERSION OF POSTGRESQL FOR THE ALTER COLUMN STATEMENT TO WORK !
--

--                         
-- Modify the old database schema
--
ALTER TABLE jobhistory ADD COLUMN jobprice FLOAT;
ALTER TABLE jobhistory ADD COLUMN filename TEXT;
ALTER TABLE jobhistory ADD COLUMN title TEXT;
ALTER TABLE jobhistory ADD COLUMN copies INT4;
ALTER TABLE jobhistory ADD COLUMN options TEXT;

--
-- Remove bad integrity rules
-- and replace them with a new one
--
ALTER TABLE jobhistory DROP CONSTRAINT "$1";
ALTER TABLE jobhistory DROP CONSTRAINT "$2";
ALTER TABLE jobhistory ADD CONSTRAINT checkUserPQuota FOREIGN KEY (userid, printerid) REFERENCES userpquota (userid, printerid);

-- 
-- Add new tables
--
--                         
-- Create the printer groups relationship
--
CREATE TABLE printergroupsmembers(groupid INT4 REFERENCES printers(id),
                           printerid INT4 REFERENCES printers(id),
                           PRIMARY KEY (groupid, printerid));

--                         
-- Now add some indexes
--
CREATE UNIQUE INDEX userpquota_up_id_ix ON userpquota (userid, printerid);
CREATE INDEX jobhistory_p_id_ix ON jobhistory (printerid);
CREATE INDEX jobhistory_pd_id_ix ON jobhistory (printerid, jobdate);
CREATE UNIQUE INDEX grouppquota_up_id_ix ON grouppquota (groupid, printerid);

-- 
-- And now sets some ACLs
-- 
REVOKE ALL ON printergroupsmembers FROM public;                        
GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON printergroupsmembers TO pykotaadmin;
GRANT SELECT ON printergroupsmembers TO pykotauser;

