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


CREATE TABLE Server (
    id              bigserial primary key,
    uuid            TEXT UNIQUE,
    hostname        TEXT,
    created         TIMESTAMP WITH TIME ZONE DEFAULT now(),
    modified        TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE TRIGGER update_server_mod_time BEFORE UPDATE ON Server FOR EACH ROW EXECUTE PROCEDURE update_modified_column();


CREATE TABLE organization_server (
    organization_id INT NOT NULL REFERENCES Organization(id) ON DELETE CASCADE,
    server_id       INT NOT NULL REFERENCES Server(id)       ON DELETE CASCADE,
    server_active   BOOLEAN DEFAULT FALSE,
    updated         TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (organization_id, server_id)
);



