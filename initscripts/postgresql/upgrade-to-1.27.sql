--
-- PyKota - Print Quotas for CUPS
--
-- (c) 2003-2010 Jerome Alet <alet@librelogiciel.com>
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <http://www.gnu.org/licenses/>.
--
-- $Id$
--
--
--
-- This script has to be used if you already
-- have a pre-1.27alpha13 version of PyKota to upgrade
-- your database schema.
--
-- YOU DON'T NEED TO USE IT IF YOU'VE JUST INSTALLED PYKOTA
--

--
-- Modify the old database schema
--
ALTER TABLE grouppquota DROP COLUMN maxjobsize;

--
-- Now updates existing datas
--
-- Just to be sure
BEGIN;
UPDATE printers SET maxjobsize=NULL WHERE maxjobsize=0;
COMMIT;

