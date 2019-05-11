#!/usr/bin/env bash
#
#    This file is part of Centralized.
#
#    Centralized is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Centralized is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Centralized.  If not, see <https://www.gnu.org/licenses/>.
#

export LC_ALL=C.UTF-8
export LANG=C.UTF-8

sleep 5

#if [ ! -f /etc/centralized/config.inited ]; then
    sed -r "s/DATABASENAME/$POSTGRES_DB/"       -i /opt/config
    sed -r "s/USERNAME/$POSTGRES_USER/"     -i /opt/config
    sed -r "s/PASSWORD/$POSTGRES_PASSWORD/" -i /opt/config
    touch /etc/centralized/config.inited
#fi

# Run migrations
/usr/local/bin/mschematool --config /opt/config default init_db
/usr/local/bin/mschematool --config /opt/config default sync

# Init the organization
function run_pg_command() {
    echo PGPASSWORD=$POSTGRES_PASSWORD psql -d $POSTGRES_DB -h db -p 5432 -U $POSTGRES_USER -W -c "$1"
    PGPASSWORD=$POSTGRES_PASSWORD psql -d $POSTGRES_DB -h db -p 5432 -U $POSTGRES_USER -W -c "$1"
}

CA=$(base64 -w 0 /etc/centralized/ssl_cert.crt)

if [ ! -f /etc/centralized/api.inited ]; then
    ORG_ID=$(run_pg_command "INSERT INTO Organization(name, contact_name, contact_email, source, uuid) VALUES('$ORG_NAME', '$ORG_CONTACT', '$ORG_EMAIL', 'github', gen_random_uuid()) returning id;" | grep -A 1 '\-\-\-' | tail -n 1 | sed -r 's/\ *([0-9]+)\ */\1/g')
    run_pg_command "INSERT INTO persongroup(organization_id, name, tree) VALUES($ORG_ID, 'All', 'all');"
    run_pg_command "INSERT INTO servergroup(organization_id, name, tree) VALUES($ORG_ID, 'All', 'all');"

    ADMIN_PASSWORD=$(dd if=/dev/urandom of=/dev/stdout bs=1024 count=1 2>/dev/null | md5sum | cut -d" " -f1)

#    run_pg_command "INSERT INTO person set admin_passwd_hash = crypt('$ADMIN_PASSWORD', gen_salt('md5')) where login='$FIRSTADMIN';"
    run_pg_command "INSERT INTO Person(login, first_name, last_name, contact_email, source, admin_passwd_hash) VALUES('$FIRSTADMIN', 'FirstAdmin', 'Admin', 'not@here.com', 0, crypt('$ADMIN_PASSWORD', gen_salt('md5')))"
    run_pg_command "INSERT INTO organization_user(organization_id, person_id, person_active, is_company_admin, updated) VALUES(1, 10000, 'yes', 'yes', now());"
    echo "$FIRSTADMIN: $ADMIN_PASSWORD" > /tmp/centralized/admin_account.text
cat > /tmp/centralized/centralized_admin.json <<EOL
{
    "url": "https://auth.centralized.local/api/1.0",
    "username": "$FIRSTADMIN",
    "password": "$ADMIN_PASSWORD",
    "ca": "$CA"
}
EOL

    touch /etc/centralized/api.inited
fi

UUID=$(run_pg_command "SELECT uuid FROM Organization WHERE name='$ORG_NAME'" | grep -A 1 '\-\-\-' | tail -n 1 | tr -d ' ')
CA=$(base64 -w 0 /etc/centralized/ssl_cert.crt)

cat > /tmp/centralized/config.ini <<EOL
[main]

url = https://auth.centralized.local/api/1.0
organization_uuid = $UUID
ca = $CA
EOL

# Start the API
/usr/bin/uwsgi --ini centralized.ini --plugin python3


