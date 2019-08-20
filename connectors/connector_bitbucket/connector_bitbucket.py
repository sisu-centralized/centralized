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
import sshpubkeys
import requests
from pybitbucket.bitbucket import Client
from pybitbucket.auth import BasicAuthenticator
from pybitbucket.team import Team, TeamRole
from pybitbucket.user import User
import json

import sys
sys.path.append("/opt/connectors/common")
from connector_common import Connector, Source, PUBKEYS


class BitbucketConn(Connector):
    v1url = 'https://api.bitbucket.org/2.0'

    def get_bitbucket_users(self):

        uname = self.conf['username']
        appwd = self.conf['password']
        email = self.conf['email']

        auth = BasicAuthenticator(uname, appwd, email)

        bitbucket = Client(auth)
        teams = Team.find_teams_for_role(role="admin", client=bitbucket)

        for t in teams:
            for m in t.members():
                pprint(m)
                login = m['nickname']
                name =  m['display_name']
                email = ''

                self.init_user(login, name, email)

                r = requests.get("{}/users/{}/ssh-keys".format(BitbucketConn.v1url, login), auth=(uname, appwd))
                if r.status_code == 200:
                    key_response = r.json()
                    for keyvalue in key_response['values']:
                        key = sshpubkeys.SSHKey(keyvalue['key'])
                        fingerprint = key.hash_md5()
                        self.user_list[login][PUBKEYS][fingerprint] = keyvalue['key']
                else:
                    print(r.status_code)

def main():
    gc = BitbucketConn()
    gc.get_bitbucket_users()
    gc.inject(Source.Bitbucket)

if __name__ == "__main__":
    main()

