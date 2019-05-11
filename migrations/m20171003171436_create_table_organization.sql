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


CREATE OR REPLACE FUNCTION update_modified_column()
    RETURNS TRIGGER AS
'
BEGIN
    NEW.modified = now();
    RETURN NEW;
END;
' language 'plpgsql';

CREATE TYPE provider_type AS ENUM('github', 'bitbucket', 'gitlab');

CREATE TABLE Organization (
    id              serial primary key,
    name            TEXT NOT NULL UNIQUE,
    contact_name    TEXT NOT NULL,
    contact_email   TEXT NOT NULL,
    source          provider_type NOT NULL,
    created         TIMESTAMP WITH TIME ZONE DEFAULT now(),
    modified        TIMESTAMP WITH TIME ZONE DEFAULT now(),
    users_updated   TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TRIGGER update_organization_mod_time BEFORE UPDATE ON Organization FOR EACH ROW EXECUTE PROCEDURE update_modified_column();



