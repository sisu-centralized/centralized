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

from pprint import pprint
import requests
from pybitbucket.bitbucket import Client
from pybitbucket.auth import BasicAuthenticator
from pybitbucket.team import Team, TeamRole
from pybitbucket.user import User
import json
import psycopg2

config_file = "/config.json"

with open(config_file) as f:
    conf = json.load(f)

uname = conf['username']
appwd = conf['password']
email = conf['email']

auth = BasicAuthenticator(
    uname,
    appwd,
    email)

v1url = 'https://api.bitbucket.org/1.0'


bitbucket = Client(auth)
teams = Team.find_teams_for_role(role="admin", client=bitbucket)

users = {}

for t in teams:
    for m in t.members():
        users[m.username] = ''


for user in users:
    print()
    print(user)
    r = requests.get("{}/users/{}/ssh-keys".format(v1url, user), auth=(uname, appwd))
    if r.status_code == 200:
        for key in r.json():
            print(key['key'])

