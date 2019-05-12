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
import sshpubkeys
from github import Github
from pprint import pprint
from importlib.machinery import SourceFileLoader

config_file = "/etc/centralized/config.json"

with open(config_file) as f:
    conf = json.load(f)

username = conf['username']
password = conf['password']
organization = conf['organization']

PUBKEYS = "pubkeys"

user_list = {}


class Source:
    Github = 0
    Bitbucket = 1
    Gitlab = 2

# man adduser.conf shows NAME_REGEX default value should be a match for ^[a-z][-a-z0-9]*$
# is the github account valid?
def valid_login(name):
    match = re.match(r'^[a-z][-a-z0-9]*$', name)
    return match is not None


def init_user(user, name, email):
    if user in user_list:
        return

    user_list[user] = {}
    user_list[user][PUBKEYS] = {}
    user_list[user]['name'] = name
    user_list[user]['email'] = email

def get_github_users():

    g = Github(username, password)
    for member in g.get_organization(organization).get_members():
        login = member.login.lower()
        name = member.name
        email = member.email

        init_user(login, name, email)

        if member.get_keys().totalCount < 1:
            print("Skipping {}. User doesn't have an SSH key associated with his github account.. ".format(login))
            continue

        if not valid_login(login):
            print("Skipping {}, GitHub account is considered invalid.".format(login))
            continue

        for userkey in member.get_keys():
            key = sshpubkeys.SSHKey(userkey.key)
            fingerprint = key.hash_md5()
            user_list[login][PUBKEYS][fingerprint] = userkey.key


def inject():
    dbconfig = SourceFileLoader("config", "/opt/config").load_module()
    dbstr = dbconfig.DATABASES['default']['dsn']

    conn = psycopg2.connect(dbstr)
    cur = conn.cursor()
    cur.execute("UPDATE organization SET users_updated=now() where name=%s RETURNING users_updated", [organization])
    users_updated = cur.fetchone()[0]
    cur.execute("SELECT id FROM organization WHERE name=%s", [organization])
    organization_id = cur.fetchone()[0]

    # Building query strings here to not have to do it at every iteration below.
    QUERY_UPSERT_PERSON = "INSERT INTO person(login, first_name, contact_email, source) VALUES(%s, %s, %s, %s) ON CONFLICT(login) DO UPDATE SET first_name=EXCLUDED.first_name, contact_email=EXCLUDED.contact_email, modified=now() RETURNING id"
    QUERY_UPSERT_ORGANIZATION_USER = ("INSERT INTO organization_user(organization_id, person_id, person_active, updated) "
                                      "VALUES(%s, %s, %s, now()) "
                                      "ON CONFLICT(organization_id, person_id) "
                                      "DO UPDATE SET updated=now() WHERE organization_user.organization_id=%s AND organization_user.person_id=%s"
                                      )
    QUERY_UPSERT_PUBKEY = "INSERT INTO pubkey(person_id, pubkey, pubkey_md5hash) VALUES(%s, %s, %s) ON CONFLICT(pubkey_md5hash) DO UPDATE SET updated=now()"

    for login in user_list:

        cur.execute(QUERY_UPSERT_PERSON, [login, user_list[login]['name'], user_list[login]['email'], Source.Github])
        person_id = cur.fetchone()[0]

        cur.execute(QUERY_UPSERT_ORGANIZATION_USER, [organization_id, person_id, True, organization_id, person_id])

        for keyfp in user_list[login][PUBKEYS]:
            cur.execute(QUERY_UPSERT_PUBKEY, [person_id, user_list[login][PUBKEYS][keyfp], keyfp])

            print(keyfp)
            pprint(user_list[login][PUBKEYS][keyfp])

    cur.execute("UPDATE organization_user AS ou SET person_active=%s FROM person AS p WHERE p.id = ou.person_id AND ou.updated < %s AND p.login != %s", [False, users_updated, os.environ['FIRSTADMIN']])
    cur.execute("DELETE FROM pubkey WHERE updated < %s", [users_updated])
    conn.commit()
    cur.close()
    conn.close()


def main():
    get_github_users()
    inject()

if __name__ == "__main__":
    main()




