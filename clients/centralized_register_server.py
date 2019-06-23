#!/usr/bin/env python3
# vim:fileencoding=utf-8
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

import os
from requests.auth import HTTPBasicAuth
import json
import sys
from readconfig import Config

if len(sys.argv) < 2:
    print("An hostname must be supplied.", file=sys.stderr)
    sys.exit(1)

hostname = sys.argv[1]

config = Config()
conf = config.getconfig()

config.load_ca()

import requests

baseurl = conf['main']['url']
uuid_path = "/.uuid_centralized"

organization_uuid = conf['main']['organization_uuid']
uuid = ""

if not os.path.exists(uuid_path):
    with open(uuid_path, 'w') as u:
        with open('/proc/sys/kernel/random/uuid', 'r') as procfile:
            uuid = procfile.read().replace('\n', '')
        u.write(uuid)
    os.chmod(uuid_path, 0o444)

with open(uuid_path, 'r') as u:
    uuid = u.read().replace('\n', '')

payload = {}
payload["hostname"] = hostname
payload["uuid"] = uuid
payload["organization_uuid"] = organization_uuid

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

r = requests.post("{}/server/register".format(baseurl), data=json.dumps(payload)) #, auth=(username, password)) #, headers=headers)
print(r.text)


