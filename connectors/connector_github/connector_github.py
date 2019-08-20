# Written and tested with Python 3.5.2
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

import sshpubkeys
from github import Github
from pprint import pprint
import sys
sys.path.append("/opt/connectors/common")
from connector_common import Connector, Source, PUBKEYS


class GithubConn(Connector):

    def get_github_users(self):
        username = self.conf['username']
        password = self.conf['password']

        g = Github(username, password)
        for member in g.get_organization(self.organization).get_members():
            login = member.login.lower()
            name = member.name
            email = member.email

            self.init_user(login, name, email)

            if member.get_keys().totalCount < 1:
                print("Skipping {}. User doesn't have an SSH key associated with his github account.. ".format(login))
                continue

            if not self.valid_login(login):
                print("Skipping {}, GitHub account is considered invalid.".format(login))
                continue

            for userkey in member.get_keys():
                key = sshpubkeys.SSHKey(userkey.key)
                fingerprint = key.hash_md5()
                self.user_list[login][PUBKEYS][fingerprint] = userkey.key


def main():
    gc = GithubConn()
    gc.get_github_users()
    gc.inject(Source.Github)

if __name__ == "__main__":
    main()




