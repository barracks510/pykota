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
-- Revision 1.2  2003/07/16 21:53:07  jalet
-- Really big modifications wrt new configuration file's location and content.
--
-- Revision 1.1  2003/07/09 20:17:07  jalet
-- Email field added to PostgreSQL schema
--
--
--
-- This script has to be used if you already
-- have a pre-1.14 version of PyKota to upgrade
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
ALTER TABLE users ADD COLUMN email TEXT;
CREATE USER pykotauser;
REVOKE ALL ON users, groups, printers, userpquota, grouppquota, groupsmembers, jobhistory FROM pykotauser;
REVOKE ALL ON users_id_seq, groups_id_seq, printers_id_seq, userpquota_id_seq, grouppquota_id_seq, jobhistory_id_seq FROM pykotauser;
GRANT SELECT ON users, groups, printers, userpquota, grouppquota, groupsmembers, jobhistory TO pykotauser;
