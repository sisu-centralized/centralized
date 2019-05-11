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

DIR=/etc/centralized
mkdir -p $DIR/connectors
mkdir -p $DIR/api

INITDONE="$DIR/initdone"

if [ ! -f "$INITDONE" ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/centralized/ssl_cert.key -out /etc/centralized/ssl_cert.crt -config /root/ssl_cert.conf \
    -subj "/C=FI/ST=Uusimaa/L=Helsinki/O=Centralized/OU=Devops Department/CN=auth.centralized.local"
    touch "$INITDONE"
fi

echo "Init done."

