--
-- PyKota - Print Quotas for CUPS and LPRng
--
-- (c) 2003 Jerome Alet <alet@librelogiciel.com>
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
ALTER TABLE jobhistory ADD COLUMN filename TEXT;
ALTER TABLE jobhistory ADD COLUMN title TEXT;
ALTER TABLE jobhistory ADD COLUMN copies INT4;
ALTER TABLE jobhistory ADD COLUMN options TEXT;

--                         
-- Now add some indexes
--
CREATE UNIQUE INDEX userpquota_up_id_ix ON userpquota (userid, printerid);
CREATE INDEX jobhistory_p_id_ix ON jobhistory (printerid);
CREATE INDEX jobhistory_pd_id_ix ON jobhistory (printerid, jobdate);
CREATE UNIQUE INDEX grouppquota_up_id_ix ON grouppquota (groupid, printerid);

