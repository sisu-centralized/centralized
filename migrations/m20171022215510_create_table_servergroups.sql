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

CREATE TABLE servergroup(
    id bigserial PRIMARY KEY,
    organization_id  INT NOT NULL REFERENCES Organization(id) ON DELETE CASCADE,
    name TEXT, tree ltree
);


CREATE TABLE server_servergroup(id bigserial, server_id INT, servergroup_id INT);


-- Users belonging to group and groups in group, etc...
-- SELECT p.login FROM person AS p JOIN person_persongroup AS p_pg ON p.id = p_pg.person_id JOIN persongroup AS pg ON pg.id = p_pg.persongroup_id WHERE p_pg.persongroup_id IN (SELECT id from persongroup where tree <@ 'all.engineers.ui');


