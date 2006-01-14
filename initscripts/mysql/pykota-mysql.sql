--
-- PyKota - Print Quotas for CUPS and LPRng
--
-- (c) 2003, 2004, 2005, 2006 Jerome Alet <alet@librelogiciel.com>
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
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
--
-- $Id$
--
--

--
-- PyKota Database creation script for MySQL
--
-- Launch this as MySQL administrator with \.
--


--
-- Create the print quota database
--

--
-- Create the print quota database users
-- 
-- TODO : CREATE USER pykotaadmin;
-- TODO : CREATE USER pykotauser;

-- 
-- Now connect to the new database
-- 
\u pykota

--
-- Create the users table
--
CREATE TABLE users(id INT4 PRIMARY KEY NOT NULL AUTO_INCREMENT,
                   username VARCHAR(255) UNIQUE NOT NULL,
                   email TEXT, 
                   balance FLOAT DEFAULT 0.0,
                   lifetimepaid FLOAT DEFAULT 0.0,
                   limitby VARCHAR(30) DEFAULT 'quota');
                   
--
-- Create the groups table
--
CREATE TABLE groups(id INT4 PRIMARY KEY NOT NULL AUTO_INCREMENT,
                    groupname VARCHAR(255) UNIQUE NOT NULL,
                    limitby VARCHAR(30) DEFAULT 'quota');
                    
--
-- Create the printers table
--
CREATE TABLE printers(id INT4 PRIMARY KEY NOT NULL AUTO_INCREMENT,
                      printername VARCHAR(255) UNIQUE NOT NULL,
                      description TEXT,
                      priceperpage FLOAT DEFAULT 0.0,
                      priceperjob FLOAT DEFAULT 0.0);
                    
--
-- Create the print quota table for users
--
CREATE TABLE userpquota(id INT4 PRIMARY KEY NOT NULL AUTO_INCREMENT,
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
CREATE TABLE jobhistory(id INT4 PRIMARY KEY NOT NULL AUTO_INCREMENT,
                        jobid TEXT,
                        userid INT4,
                        printerid INT4,
                        pagecounter INT4 DEFAULT 0,
                        jobsizebytes INT8,
                        jobsize INT4,
                        jobprice FLOAT,
                        action TEXT,
                        filename TEXT,
                        title TEXT,
                        copies INT4,
                        options TEXT,
                        hostname VARCHAR(255),
                        jobdate TIMESTAMP,
                        CONSTRAINT checkUserPQuota FOREIGN KEY (userid, printerid) 
                                                           REFERENCES userpquota(userid, printerid));
CREATE INDEX jobhistory_p_id_ix ON jobhistory (printerid);
CREATE INDEX jobhistory_pd_id_ix ON jobhistory (printerid, jobdate);
CREATE INDEX jobhistory_hostname_ix ON jobhistory (hostname);
                        
--
-- Create the print quota table for groups
--
CREATE TABLE grouppquota(id INT4 PRIMARY KEY NOT NULL AUTO_INCREMENT,
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
-- Create the table for payments
-- 
CREATE TABLE payments (id INT4 PRIMARY KEY NOT NULL AUTO_INCREMENT,
                       userid INT4 REFERENCES users(id),
                       amount FLOAT,
                       date TIMESTAMP DEFAULT now());
CREATE INDEX payments_date_ix ON payments (date);

--                        
-- Set some ACLs                        
--
-- TODO : REVOKE ALL ON users, groups, printers, userpquota, grouppquota, groupsmembers, printergroupsmembers, jobhistory, payments FROM public;                        
-- TODO : REVOKE ALL ON users_id_seq, groups_id_seq, printers_id_seq, userpquota_id_seq, grouppquota_id_seq, jobhistory_id_seq, payments_id_seq FROM public;

-- TODO : GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON users, groups, printers, userpquota, grouppquota, groupsmembers, printergroupsmembers, jobhistory, payments TO pykotaadmin;
-- TODO : GRANT SELECT, UPDATE ON users_id_seq, groups_id_seq, printers_id_seq, userpquota_id_seq, grouppquota_id_seq, jobhistory_id_seq, payments_id_seq TO pykotaadmin;
-- TODO : GRANT SELECT ON users, groups, printers, userpquota, grouppquota, groupsmembers, printergroupsmembers, jobhistory, payments TO pykotauser;

