--
-- PyKota - Print Quotas for CUPS
--
-- (c) 2003 Jerome Alet <alet@librelogiciel.com>
-- You're welcome to redistribute this software under the
-- terms of the GNU General Public Licence version 2.0
-- or, at your option, any higher version.
--
-- You can read the complete GNU GPL in the file COPYING
-- which should come along with this software, or visit
-- the Free Software Foundation's WEB site http://www.fsf.org
--
-- $Id$
--
-- $Log$
-- Revision 1.3  2003/02/26 20:34:22  jalet
-- Default value for printer page counter set to 0
--
-- Revision 1.2  2003/02/08 22:12:09  jalet
-- Life time counter for users and groups added.
--
-- Revision 1.1  2003/02/05 21:28:17  jalet
-- Initial import into CVS
--
--
--

--
-- PyKota Database creation script for PostgreSQL
--
-- Launch this as PostgreSQL administrator with \i
--


--
-- Create the print quota database
--
CREATE DATABASE pykota;

--
-- Create the print quota database users
-- 
CREATE USER pykotauser;
CREATE USER pykotaadmin;

-- 
-- Now connect to the new database
-- 
\connect pykota

--
-- Create the users table
--
CREATE TABLE users(id SERIAL PRIMARY KEY NOT NULL,
                   username TEXT UNIQUE NOT NULL);
                   
--
-- Create the groups table
--
CREATE TABLE groups(id SERIAL PRIMARY KEY NOT NULL,
                    groupname TEXT UNIQUE NOT NULL);
                    
--
-- Create the printers table
--
CREATE TABLE printers(id SERIAL PRIMARY KEY NOT NULL,
                      printername TEXT UNIQUE NOT NULL,
                      lastusername TEXT,
                      pagecounter INT4 DEFAULT 0);
                    
--
-- Create the print quota table for users
--
CREATE TABLE userpquota(id SERIAL PRIMARY KEY NOT NULL,
                        userid INT4 REFERENCES users(id),
                        printerid INT4 REFERENCES printers(id),
                        lifepagecounter INT4 DEFAULT 0,
                        pagecounter INT4 DEFAULT 0,
                        softlimit INT4,
                        hardlimit INT4,
                        datelimit DATETIME);
                        
--
-- Create the print quota table for groups
--
CREATE TABLE grouppquota(id SERIAL PRIMARY KEY NOT NULL,
                         groupid INT4 REFERENCES groups(id),
                         printerid INT4 REFERENCES printers(id),
                         lifepagecounter INT4 DEFAULT 0,
                         pagecounter INT4 DEFAULT 0,
                         softlimit INT4,
                         hardlimit INT4,
                         datelimit DATETIME);
                        
--                        
-- Set some ACLs                        
--
REVOKE ALL ON users, groups, printers, userpquota, grouppquota FROM public;                        
GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON users, groups, printers, userpquota, grouppquota TO pykotaadmin;
GRANT SELECT, UPDATE ON users_id_seq, groups_id_seq, printers_id_seq, userpquota_id_seq, grouppquota_id_seq TO pykotaadmin;
GRANT SELECT, UPDATE ON printers, userpquota, grouppquota TO pykotauser;
GRANT SELECT ON users, groups TO pykotauser;

