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

