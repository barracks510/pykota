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
-- Revision 1.9  2004/05/13 11:15:29  jalet
-- Added hostname field in job history
--
-- Revision 1.8  2004/01/08 14:10:32  jalet
-- Copyright year changed.
--
-- Revision 1.7  2003/12/27 16:49:25  uid67467
-- Should be ok now.
--
-- Revision 1.6  2003/11/23 19:01:36  jalet
-- Job price added to history
--
-- Revision 1.5  2003/11/21 14:28:45  jalet
-- More complete job history.
--
-- Revision 1.4  2003/07/16 21:53:07  jalet
-- Really big modifications wrt new configuration file's location and content.
--
-- Revision 1.3  2003/07/09 20:17:07  jalet
-- Email field added to PostgreSQL schema
--
-- Revision 1.2  2003/06/10 16:37:54  jalet
-- Deletion of the second user which is not needed anymore.
-- Added a debug configuration field in /etc/pykota.conf
-- All queries can now be sent to the logger in debug mode, this will
-- greatly help improve performance when time for this will come.
--
-- Revision 1.1  2003/06/05 07:12:31  jalet
-- Reorganization of directories
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
CREATE USER pykotaadmin;
CREATE USER pykotauser;

-- 
-- Now connect to the new database
-- 
\connect pykota

--
-- Create the users table
--
CREATE TABLE users(id SERIAL PRIMARY KEY NOT NULL,
                   username TEXT UNIQUE NOT NULL,
                   email TEXT, 
                   balance FLOAT DEFAULT 0.0,
                   lifetimepaid FLOAT DEFAULT 0.0,
                   limitby TEXT DEFAULT 'quota');
                   
--
-- Create the groups table
--
CREATE TABLE groups(id SERIAL PRIMARY KEY NOT NULL,
                    groupname TEXT UNIQUE NOT NULL,
                    limitby TEXT DEFAULT 'quota');
                    
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
CREATE UNIQUE INDEX userpquota_up_id_ix ON userpquota (userid, printerid);
                        
--
-- Create the job history table
--
CREATE TABLE jobhistory(id SERIAL PRIMARY KEY NOT NULL,
                        jobid TEXT,
                        userid INT4,
                        printerid INT4,
                        hostname TEXT,
                        pagecounter INT4 DEFAULT 0,
                        jobsize INT4,
                        jobprice FLOAT,
                        action TEXT,
                        filename TEXT,
                        title TEXT,
                        copies INT4,
                        options TEXT,
                        jobdate TIMESTAMP DEFAULT now(),
                        CONSTRAINT checkUserPQuota FOREIGN KEY (userid, printerid) REFERENCES userpquota(userid, printerid));
CREATE INDEX jobhistory_p_id_ix ON jobhistory (printerid);
CREATE INDEX jobhistory_pd_id_ix ON jobhistory (printerid, jobdate);
                        
--
-- Create the print quota table for groups
--
CREATE TABLE grouppquota(id SERIAL PRIMARY KEY NOT NULL,
                         groupid INT4 REFERENCES groups(id),
                         printerid INT4 REFERENCES printers(id),
                         softlimit INT4,
                         hardlimit INT4,
                         datelimit TIMESTAMP);
CREATE UNIQUE INDEX grouppquota_up_id_ix ON grouppquota (groupid, printerid);
                        
--                         
-- Create the groups/members relationship
--
CREATE TABLE groupsmembers(groupid INT4 REFERENCES groups(id),
                           userid INT4 REFERENCES users(id),
                           PRIMARY KEY (groupid, userid));
                           
--                         
-- Create the printer groups relationship
--
CREATE TABLE printergroupsmembers(groupid INT4 REFERENCES printers(id),
                           printerid INT4 REFERENCES printers(id),
                           PRIMARY KEY (groupid, printerid));

--                        
-- Set some ACLs                        
--
REVOKE ALL ON users, groups, printers, userpquota, grouppquota, groupsmembers, printergroupsmembers, jobhistory FROM public;                        
REVOKE ALL ON users_id_seq, groups_id_seq, printers_id_seq, userpquota_id_seq, grouppquota_id_seq, jobhistory_id_seq FROM public;

GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON users, groups, printers, userpquota, grouppquota, groupsmembers, printergroupsmembers, jobhistory TO pykotaadmin;
GRANT SELECT, UPDATE ON users_id_seq, groups_id_seq, printers_id_seq, userpquota_id_seq, grouppquota_id_seq, jobhistory_id_seq TO pykotaadmin;
GRANT SELECT ON users, groups, printers, userpquota, grouppquota, groupsmembers, printergroupsmembers, jobhistory TO pykotauser;

