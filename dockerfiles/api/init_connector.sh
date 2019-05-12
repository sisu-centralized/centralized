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

echo "Starting connector."

if [ ! -f /etc/centralized/inited.connectors ]; then

    CONNECTOR_CFGFILE=/etc/centralized/config.json
cat >$CONNECTOR_CFGFILE <<EOL
{
    "username": "$CONNECTOR_USERNAME",
    "password": "$CONNECTOR_PASSWORD",
    "organization": "$ORG_NAME",
    "email": "$ORG_EMAIL"
}
EOL

    touch /etc/centralized/inited.connectors
fi

sed -r "s/DATABASENAME/$POSTGRES_DB/"       -i /opt/config
sed -r "s/USERNAME/$POSTGRES_USER/"     -i /opt/config
sed -r "s/PASSWORD/$POSTGRES_PASSWORD/" -i /opt/config

min=$(shuf -i0-9 -n1)
minutes="0$min,1$min,2$min,3$min,4$min,5$min"

echo "$minutes *  * * *  root /usr/bin/python3 /opt/connectors/connector_$CONNECTOR_TYPE/connector_$CONNECTOR_TYPE.py" > /etc/cron.d/connector
echo "Connector init done (Minutes: $minutes)."

/usr/sbin/cron -f -L 8

