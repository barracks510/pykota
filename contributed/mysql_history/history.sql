-- phpMyAdmin SQL Dump
-- version 2.6.0
-- http://www.phpmyadmin.net
-- 
-- Host: localhost
-- Generation Time: Jan 10, 2006 at 02:24 PM
-- Server version: 3.23.58
-- PHP Version: 4.3.2
-- 
-- Database: `pykota`
-- 

-- --------------------------------------------------------

-- 
-- Table structure for table `history`
-- 

CREATE TABLE IF NOT EXISTS history (
  id int(4) unsigned NOT NULL auto_increment,
  jobid text NOT NULL,
  username text NOT NULL,
  printername text NOT NULL,
  pgroups text NOT NULL,
  jobsize int(4) NOT NULL default '0',
  jobprice float NOT NULL default '0',
  action text NOT NULL,
  title text NOT NULL,
  copies int(4) NOT NULL default '0',
  options text NOT NULL,
  printeroriginatinghostname text NOT NULL,
  md5sum text NOT NULL,
  precomputedjobsize int(4) NOT NULL default '0',
  precomputedjobprice float NOT NULL default '0',
  jobdate timestamp(14) NOT NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

-- 
-- Dumping data for table `history`
-- 

INSERT INTO history VALUES (1, '23971', 'hyclak', 'print325', 'math-laser', 1, 0, 'ALLOW', 'mysql_history.py', 1, '', 'localhost', 'f5775c4bad32c999074e2eb5d8374aac', 1, 0, '20060110142024');
