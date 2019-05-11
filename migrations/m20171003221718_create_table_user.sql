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

-- usr.source:
--  github: 1
--  bitbucket: 2
--  gitlab: 3

CREATE TABLE Person (
    id              bigserial primary key,  -- Becomes the UID on the machines.
    login           TEXT UNIQUE,
    first_name      TEXT,
    last_name       TEXT,
    contact_email   TEXT,
    source          INT NOT NULL,
    created         TIMESTAMP WITH TIME ZONE DEFAULT now(),
    modified        TIMESTAMP WITH TIME ZONE DEFAULT now()
);
ALTER SEQUENCE person_id_seq RESTART WITH 10000; -- First UID will be 10000.
CREATE TRIGGER update_person_mod_time BEFORE UPDATE ON Person FOR EACH ROW EXECUTE PROCEDURE update_modified_column();

CREATE TABLE PubKey (
    id              bigserial,
    person_id       INT NOT NULL REFERENCES Person(id) ON DELETE CASCADE,
    pubkey          TEXT NOT NULL,
    pubkey_md5hash  TEXT UNIQUE,
    updated         TIMESTAMP WITH TIME ZONE DEFAULT now(),
    PRIMARY KEY (id, person_id)
);

CREATE TABLE organization_user (
    organization_id INT NOT NULL REFERENCES Organization(id) ON DELETE CASCADE,
    person_id       INT NOT NULL REFERENCES Person(id)       ON DELETE CASCADE,
    person_active   BOOLEAN DEFAULT FALSE,
    updated         TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (organization_id, person_id)
);



