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

--DO
--$do$
--BEGIN
--   IF EXISTS (SELECT 1 FROM pg_database WHERE datname = 'centralized') THEN
--      RAISE NOTICE 'Database already exists, continuing.'; 
--   ELSE
--      PERFORM dblink_exec('dbname=' || current_database()
--                        , "CREATE DATABASE centralized ENCODING 'UTF8' LC_COLLATE = 'en_US.utf-8' LC_CTYPE = 'en_US.utf-8' TEMPLATE template0;");
--      -- TEMPLATE template0;");
--      -- LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8' TEMPLATE template0;");
--   END IF;
--END
--$do$;

-- CREATE DATABASE centralized ENCODING 'UTF8' LC_COLLATE = 'en_US.utf-8' LC_CTYPE = 'en_US.utf-8' TEMPLATE template0;
CREATE EXTENSION IF NOT EXISTS ltree;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

