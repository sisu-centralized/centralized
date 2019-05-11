--
--    This file is part of Centralized.
--
--    Centralized is free software: you can redistribute it and/or modify
--    it under the terms of the GNU General Public License as published by
--    the Free Software Foundation, either version 3 of the License, or
--    (at your option) any later version.
--
--    Centralized is distributed in the hope that it will be useful,
--    but WITHOUT ANY WARRANTY; without even the implied warranty of
--    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
--    GNU General Public License for more details.
--
--    You should have received a copy of the GNU General Public License
--    along with Centralized.  If not, see <https://www.gnu.org/licenses/>.
--

CREATE TABLE persongroup(
    id bigserial PRIMARY KEY,
    organization_id  INT NOT NULL REFERENCES Organization(id) ON DELETE CASCADE,
    name TEXT, tree ltree
);
ALTER SEQUENCE persongroup_id_seq RESTART WITH 10000; -- First GID will be 10000.

-- paloma=# select * from persongroup;
--  id | organization_id |     name     |       tree       
-- ----+-----------------+--------------+------------------
--   1 |               1 | All          | 0
--   2 |               1 | Engineers    | all.engineers
--   3 |               1 | Accountants  | all.accountants
--   4 |               1 | Managers     | all.managers
--   5 |               1 | UI Engineers | all.engineers.ui

CREATE TABLE person_persongroup(
    id bigserial,
    person_id INT NOT NULL REFERENCES Person(id) ON DELETE CASCADE,
    persongroup_id INT NOT NULL REFERENCES persongroup(id) ON DELETE CASCADE
);
-- paloma=# select * from person_persongroup;
--  id | person_id | persongroup_id 
-- ----+-----------+----------------
--   5 |        22 |              2
--   6 |        72 |              2
--   7 |        23 |              3
--   8 |        28 |              5


-- Users belonging to group and groups in group, etc...
-- SELECT p.login FROM person AS p JOIN person_persongroup AS p_pg ON p.id = p_pg.person_id JOIN persongroup AS pg ON pg.id = p_pg.persongroup_id WHERE p_pg.persongroup_id IN (SELECT id from persongroup where tree <@ 'all.engineers.ui');


