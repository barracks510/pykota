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
-- Revision 1.2  2004/06/03 23:14:10  jalet
-- Now stores the job's size in bytes in the database.
-- Preliminary work on payments storage : database schemas are OK now,
-- but no code to store payments yet.
-- Removed schema picture, not relevant anymore.
--
-- Revision 1.1  2004/05/13 11:15:29  jalet
-- Added hostname field in job history
--
--
--
-- This script has to be used if you already
-- have a pre-1.19 version of PyKota to upgrade
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
ALTER TABLE jobhistory ADD COLUMN jobsizebytes INT8;
ALTER TABLE jobhistory ADD COLUMN hostname TEXT;
CREATE INDEX jobhistory_hostname_ix ON jobhistory (hostname);

CREATE TABLE payments (id SERIAL PRIMARY KEY NOT NULL,
                       userid INT4 REFERENCES users(id),
                       amount FLOAT,
                       date TIMESTAMP DEFAULT now());
CREATE INDEX payments_date_ix ON payments (date);

REVOKE ALL ON payments FROM public;                        
REVOKE ALL ON payments_id_seq FROM public;
GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON payments TO pykotaadmin;
GRANT SELECT, UPDATE ON payments_id_seq TO pykotaadmin;
GRANT SELECT ON payments TO pykotauser;
