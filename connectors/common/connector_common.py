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


import os
import re
import json
import psycopg2
from importlib.machinery import SourceFileLoader
from pprint import pprint


PUBKEYS = "pubkeys"


class Source:
    Github = 0
    Bitbucket = 1
    Gitlab = 2

class Connector:
    db_config_path = "/opt/config"
    config_file = "/etc/centralized/config.json"


    """
    self.user_list is an hash of logins, each login being an hash such as:
    Multiple logins, multiple pubkeys per logins are supported.

    self.user_list: {
        '<login>': {
            'email': '<email address>',
            'name':  '<name>',
            'pubkeys': {
                '<fingerprint>': 'ssh-rsa foobar'
            }
        }
    }

    """
    def __init__(self):
        self.user_list = {}
        config_file = "/etc/centralized/config.json"

        with open(config_file) as f:
            self.conf = json.load(f)

        self.organization = self.conf['organization']



    # man adduser.conf shows NAME_REGEX default value should be a match for ^[a-z][-a-z0-9]*$
    # is the github account valid?
    def valid_login(self, name):
        match = re.match(r'^[a-z][-a-z0-9]*$', name)
        return match is not None


    def init_user(self, user, name, email):
        if user in self.user_list:
            return

        self.user_list[user] = {}
        self.user_list[user][PUBKEYS] = {}
        self.user_list[user]['name'] = name
        self.user_list[user]['email'] = email


    def inject(self, source):
        print("Injection")
        pprint(self.user_list)
        dbconfig = SourceFileLoader("config", self.db_config_path).load_module()
        dbstr = dbconfig.DATABASES['default']['dsn']

        conn = psycopg2.connect(dbstr)
        cur = conn.cursor()
        cur.execute("UPDATE organization SET users_updated=now() where name=%s RETURNING users_updated", [self.organization])
        users_updated = cur.fetchone()[0]
        cur.execute("SELECT id FROM organization WHERE name=%s", [self.organization])
        organization_id = cur.fetchone()[0]

        # Building query strings here to not have to do it at every iteration below.
        QUERY_UPSERT_PERSON = "INSERT INTO person(login, first_name, contact_email, source) VALUES(%s, %s, %s, %s) ON CONFLICT(login) DO UPDATE SET first_name=EXCLUDED.first_name, contact_email=EXCLUDED.contact_email, modified=now() RETURNING id"
        QUERY_UPSERT_ORGANIZATION_USER = ("INSERT INTO organization_user(organization_id, person_id, person_active, updated) "
                                          "VALUES(%s, %s, %s, now()) "
                                          "ON CONFLICT(organization_id, person_id) "
                                          "DO UPDATE SET updated=now() WHERE organization_user.organization_id=%s AND organization_user.person_id=%s"
                                          )
        QUERY_UPSERT_PUBKEY = "INSERT INTO pubkey(person_id, pubkey, pubkey_md5hash) VALUES(%s, %s, %s) ON CONFLICT(pubkey_md5hash) DO UPDATE SET updated=now()"

        for login in self.user_list:

            cur.execute(QUERY_UPSERT_PERSON, [login, self.user_list[login]['name'], self.user_list[login]['email'], source])
            person_id = cur.fetchone()[0]

            cur.execute(QUERY_UPSERT_ORGANIZATION_USER, [organization_id, person_id, True, organization_id, person_id])

            for keyfp in self.user_list[login][PUBKEYS]:
                cur.execute(QUERY_UPSERT_PUBKEY, [person_id, self.user_list[login][PUBKEYS][keyfp], keyfp])

                print(keyfp)
#                pprint(self.user_list[login][PUBKEYS][keyfp])

        cur.execute("UPDATE organization_user AS ou SET person_active=%s FROM person AS p WHERE p.id = ou.person_id AND ou.updated < %s AND p.login != %s", [False, users_updated, os.environ['FIRSTADMIN']])
        cur.execute("DELETE FROM pubkey WHERE updated < %s", [users_updated])
        conn.commit()
        cur.close()
        conn.close()

