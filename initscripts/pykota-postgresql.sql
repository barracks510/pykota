--
-- PyKota - Print Quotas for CUPS
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
-- Revision 1.12  2003/04/14 20:01:02  jalet
-- Typo
--
-- Revision 1.11  2003/04/14 19:58:59  jalet
-- New database schema for users' account balance
--
-- Revision 1.10  2003/04/10 21:47:20  jalet
-- Job history added. Upgrade script neutralized for now !
--
-- Revision 1.9  2003/04/09 20:11:29  jalet
-- Added a field to save the action taken for this job (Allow, Deny)
--
-- Revision 1.8  2003/04/09 20:09:34  jalet
-- New table to keep job history
--
-- Revision 1.7  2003/04/08 20:38:08  jalet
-- The last job Id is saved now for each printer, this will probably
-- allow other accounting methods in the future.
--
-- Revision 1.6  2003/03/29 13:45:27  jalet
-- GPL paragraphs were incorrectly (from memory) copied into the sources.
-- Two README files were added.
-- Upgrade script for PostgreSQL pre 1.01 schema was added.
--
-- Revision 1.5  2003/03/12 19:06:08  jalet
-- Initial support for groups added.
--
-- Revision 1.4  2003/02/27 08:40:14  jalet
-- DATETIME is not supported anymore in PostgreSQL 7.3 it seems, but
-- TIMESTAMP is.
--
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
                   username TEXT UNIQUE NOT NULL,
                   balance FLOAT DEFAULT 0.0,
                   lifetimepaid FLOAT DEFAULT 0.0,
                   limitby TEXT DEFAULT 'quota');
                   
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
                      priceperpage FLOAT DEFAULT 0.0,
                      priceperjob FLOAT DEFAULT 0.0);
                    
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
                        datelimit TIMESTAMP);
                        
--
-- Create the job history table
--
CREATE TABLE jobhistory(id SERIAL PRIMARY KEY NOT NULL,
                        jobid TEXT,
                        userid INT4 REFERENCES users(id),
                        printerid INT4 REFERENCES printers(id),
                        pagecounter INT4 DEFAULT 0,
                        jobsize INT4,
                        action TEXT,
                        jobdate TIMESTAMP DEFAULT now());
                        
--
-- Create the print quota table for groups
--
CREATE TABLE grouppquota(id SERIAL PRIMARY KEY NOT NULL,
                         groupid INT4 REFERENCES groups(id),
                         printerid INT4 REFERENCES printers(id),
                         softlimit INT4,
                         hardlimit INT4,
                         datelimit TIMESTAMP);
                        
--                         
-- Create the groups/members relationship
--
CREATE TABLE groupsmembers(groupid INT4 REFERENCES groups(id),
                           userid INT4 REFERENCES users(id),
                           PRIMARY KEY (groupid, userid));

--                        
-- Set some ACLs                        
--
REVOKE ALL ON users, groups, printers, userpquota, grouppquota, groupsmembers, jobhistory FROM public;                        
GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON users, groups, printers, userpquota, grouppquota, groupsmembers, jobhistory TO pykotaadmin;
GRANT SELECT, UPDATE ON users_id_seq, groups_id_seq, printers_id_seq, userpquota_id_seq, grouppquota_id_seq, jobhistory_id_seq TO pykotaadmin;
GRANT SELECT, UPDATE ON printers, userpquota, grouppquota TO pykotauser;
GRANT SELECT ON users, groups, groupsmembers TO pykotauser;
GRANT SELECT, INSERT, UPDATE ON jobhistory TO pykotauser;
GRANT SELECT, UPDATE ON jobhistory_id_seq TO pykotauser;

