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

import sys
import os
from terminaltables import AsciiTable
import json
import pprint
import traceback
import base64

#http_client.HTTPConnection.debuglevel = 1

conf = {}
config_file="{}/.centralized_admin.json".format(os.getenv("HOME"))
if not os.path.isfile(config_file):
    print("{} not created, please refer to the documentation.".format(config_file), file=sys.stderr)
    sys.exit(1)


with open(config_file) as f:
    conf = json.load(f)


username = conf['username']
password = conf['password']
baseurl = conf['url']
ca = base64.b64decode(conf['ca']).decode('utf-8')

# Handle CA

crt_path = '{}/.centralized_ca.crt'.format(os.getenv("HOME"))
if not os.path.isfile(crt_path):
    f = open( crt_path, 'w' )
    f.write( ca )
    f.close()

os.environ['REQUESTS_CA_BUNDLE'] = crt_path

import requests

# Transforms arrays of dicts containing column : value
# to list of values, first element of the list holding columns.
def json2list(ary):
    retval = []
    columns_to_init = True

    for i in ary:
        if columns_to_init:
            cols = []
            for column in i.keys():
                cols.append(column)
            cols.sort()
            retval.append(cols)        
            columns_to_init = False

        row = []
        for col in retval[0]:
            row.append(i[col])
        retval.append(row)
            
    return retval
                
def check_code(r):
    if r.status_code == 400:
        print("Wrong request, bad parameters.")
        print(r.text)
        sys.exit(1)
    if r.status_code == 401:
        print("Wrong credentials, please ensure your config is correct, otherwise, contact centralized.")
        sys.exit(1)
    if r.status_code >= 402:
        print("Unknown error, please contact centralized")
        print("Received HTTP status code {}.".format(r.status_code))
        print(r.text)
        print(r.status_code)
        sys.exit(1)


class Conn:
    def __init__(self):
        self.s = requests.Session()
        self.s.auth=(username, password)

        r = self.s.post("{}/auth/login".format(baseurl))
        check_code(r)

    def render(self, r):
        lst = json.loads(r)
        if len(lst) == 0:
            print("None")
        else:
            table = AsciiTable(json2list(lst))
            print(table.table)


    def users_list(self):
        r = self.s.get("{}/user/list".format(baseurl))
        check_code(r)
        self.render(r.text)

    def user_groups(self, user_id):
        r = self.s.get("{}/usergroup/list?uid={}".format(baseurl, user_id))
        check_code(r)
        self.render(r.text)



    def user_enable(self, user_id):
        payload = {}
        payload["user_id"] = user_id

        r = self.s.post("{}/user".format(baseurl), data=None, json=payload)
        check_code(r)
        print(r.text)
        return r.text # id of the created group

    def user_disable(self, user_id):
        payload = {}
        payload["user_id"] = user_id

        r = self.s.delete("{}/user".format(baseurl), data=None, json=payload)
        check_code(r)
        print(r.text)
        return r.text # id of the created group

    def admin_reset_password(self, login):
        payload = {}

        r = self.s.post("{}/user/password/reset/{}".format(baseurl, login), data=None, json=payload)
        check_code(r)
        print(r.text)
        return r.text # id of the created group

    def admin_promote(self, login):
        payload = {}

        r = self.s.post("{}/user/promote/{}".format(baseurl, login), data=None, json=payload)
        check_code(r)
        print(r.text)
        return r.text # id of the created group

    def admin_demote(self, login):
        payload = {}

        r = self.s.post("{}/user/demote/{}".format(baseurl, login), data=None, json=payload)
        check_code(r)
        print(r.text)
        return r.text # id of the created group

    def admin_promotetoca(self, login):
        payload = {}

        r = self.s.post("{}/user/promotetoca/{}".format(baseurl, login), data=None, json=payload)
        check_code(r)
        print(r.text)
        return r.text # id of the created group

    def admin_demotefromca(self, login):
        payload = {}

        r = self.s.post("{}/user/demotefromca/{}".format(baseurl, login), data=None, json=payload)
        check_code(r)
        print(r.text)
        return r.text # id of the created group

    def admin_change_password(self, newpassword):
        payload = {}

        r = self.s.post("{}/user/password/update/{}".format(baseurl, newpassword), data=None, json=payload)
        check_code(r)
        print(r.text)
        return r.text # id of the created group


    def usergroups_list(self):
        r = self.s.get("{}/usergroup/list".format(baseurl))
        check_code(r)
        self.render(r.text)

    def servergroups_list(self):
        r = self.s.get("{}/servergroup/list".format(baseurl))
        check_code(r)
        self.render(r.text)

    def servergroup_create(self, parent_group_id, name):
        payload = {}
        payload["parentgroup"] = parent_group_id
        payload["name"] = name

        r = self.s.post("{}/servergroup".format(baseurl), data=None, json=payload)
        check_code(r)
        print(r.text)
        return r.text # id of the created group

    def servergroup_delete(self, sg_id):
        payload = {}
        payload["sg_id"] = sg_id

        r = self.s.delete("{}/servergroup".format(baseurl), data=None, json=payload)
        check_code(r)
        return r.text # id of the created group

    def usergroup_create(self, parent_group_id, name):
        payload = {}
        payload["parentgroup"] = parent_group_id
        payload["name"] = name

        r = self.s.post("{}/usergroup".format(baseurl), data=None, json=payload)
        check_code(r)
        return r.text # id of the created group


    def usergroup_delete(self, ug_id):
        payload = {}
        payload["ug_id"] = ug_id

        r = self.s.delete("{}/usergroup".format(baseurl), data=None, json=payload)
        check_code(r)
        return r.text # id of the created group


    def user_usergroups_list(self):
        r = self.s.get("{}/user_usergroups/list".format(baseurl))
        check_code(r)
        self.render(r.text)

    def user_usergroups_create(self, usergroup_id, login):
        payload = {}
        payload["usergroup_id"] = usergroup_id
        payload["login"] = login

        r = self.s.post("{}/user_usergroups".format(baseurl), data=None, json=payload)
        check_code(r)
        return r.text # id of the created group

    def user_usergroups_delete(self, uug_id):
        payload = {}
        payload["uug_id"] = uug_id

        r = self.s.delete("{}/user_usergroups".format(baseurl), data=None, json=payload)
        check_code(r)
        return r.text # id of the created group


    def servers_list(self):
        r = self.s.get("{}/server/list".format(baseurl))
        check_code(r)
        self.render(r.text)

    def server_servergroups_list(self):
        r = self.s.get("{}/server_servergroups/list".format(baseurl))
        check_code(r)
        self.render(r.text)

    def server_servergroups_create(self, servergroup_id, uuid):
        payload = {}
        payload["servergroup_id"] = servergroup_id
        payload["uuid"] = uuid

        r = self.s.post("{}/server_servergroups".format(baseurl), data=None, json=payload)
        check_code(r)
        return r.text # id of the created group

    def server_servergroups_delete(self, ssg_id):
        payload = {}
        payload["ssg_id"] = ssg_id

        r = self.s.delete("{}/server_servergroups".format(baseurl), data=None, json=payload)
        check_code(r)
        return r.text # id of the created group


    def roles_list(self):
        r = self.s.get("{}/ugsg/list".format(baseurl))
        check_code(r)
        self.render(r.text)

    def roles_create(self, ug_id, sg_id, sudoline, ugroups):
        payload = {}
        payload["ug_id"] = ug_id
        payload["sg_id"] = sg_id
        payload["sudoline"] = sudoline
        payload["ugroups"] = ugroups

        r = self.s.post("{}/ugsg".format(baseurl), data=None, json=payload)
        check_code(r)
        print(r.text)
        return r.text # id of the created group

    def roles_delete(self, roleid):
        payload = {}
        payload["id"] = roleid

        r = self.s.delete("{}/ugsg".format(baseurl), data=None, json=payload)
        check_code(r)
        print(r.text)
        return r.text # id of the created group


    def logout(self):
        r = self.s.post("{}/auth/logout".format(baseurl))
        check_code(r)
        print(r.text)
        #self.render(r.text)




def global_help():
    prgname = sys.argv[0]
    #raise Exception

    print("")
    print("Centralized admin tool usage:")
    print("")
    print("Manage units")
    print("{} users               | Enable, Disable, get information about users.".format(prgname))
    print("{} admins              | Manage admin users.".format(prgname))
    print("{} servers             | List servers.".format(prgname))
    print("")
    print("Manage groups")
    print("{} usergroups          | Manage user groups".format(prgname))
    print("{} servergroups        | Manage server groups".format(prgname))
    print("")
    print("Manage relationships")
    print("{} user_usergroups     | Manage the relationship between users and usergroups.".format(prgname))
    print("{} server_servergroups | Manage the relationship between servers and servergroups.".format(prgname))
    print("")

    print("Manage authorization")
    print("{} roles               | Manage access a usergroup has on a servergroup.".format(prgname))
    print("")
#    print("{} logout (Closes session)".format(prgname))

def context_help(context):
    prefix = ' '.join(sys.argv)
    if context == "users":
        print("{} list".format(prefix))
        print("{} groups <user id> (Lists groups the user belongs to)".format(prefix))
        print("{} enable <user id>".format(prefix))
        print("{} disable <user id>".format(prefix))

    if context == "admins":
        print("Descriptions starting with a <C> describe commands requiring to be company admin.")
        print("{} password_reset <login>        | <C> Generate a password for the user and send it by email. The email must be correct.".format(prefix))
        print("{} promote <login>               | <C> Make the user become admin.".format(prefix))
        print("{} demote <login>                | <C> Remove admin rights from a user.".format(prefix))
        print("{} promotetoca <login>           | <C> Make the user become company admin.".format(prefix))
        print("{} demotefromca <login>          | <C> Remove company admin rights from a user.".format(prefix))
        print("{} change_password <newpassword> | Change your password. This also will log you out.".format(prefix))

    if context == "usergroups":
        print("{} list".format(prefix))
        print("{} create <parent group id> <group name>".format(prefix))
        print("{} delete <user group id>".format(prefix))
    if context == "user_usergroups":
        print("{} list".format(prefix))
        print("{} create <user group id> <login>".format(prefix))
        print("{} delete <user usergroup id>".format(prefix))
    if context == "servers":
        print("{} list".format(prefix))
    if context == "servergroups":
        print("{} list".format(prefix))
        print("{} create <parent group id> <group name>".format(prefix))
        print("{} delete <server group id>".format(prefix))
    if context == "server_servergroups":
        print("{} list".format(prefix))
        print("{} create <server group id> <uuid>".format(prefix))
        print("{} delete <server servergroup id>".format(prefix))
    if context == "roles":
        print("{} list".format(prefix))
        print("{} create <user group id> <server group id> '<sudoline>' '<unmanaged groups>'".format(prefix))
        print("{} delete <role id>".format(prefix))

def main():
#    try:
    numarg = len(sys.argv)
    if numarg == 1:
        global_help()
        exit(0)

    firstarg = sys.argv[1]
    if numarg <= 2:
        context_help(firstarg)
        exit(0)

    conn = Conn()

    secondarg = sys.argv[2]
    if firstarg == "users":
        if secondarg == "list":
            conn.users_list()
        if secondarg == "groups":
            if len(sys.argv) == 4:
                conn.user_groups(sys.argv[3])
        if secondarg == "enable":
            if len(sys.argv) == 4:
                conn.user_enable(sys.argv[3])
        if secondarg == "disable":
            if len(sys.argv) == 4:
                conn.user_disable(sys.argv[3])

    elif firstarg == "admins":
        if secondarg == "password_reset":
            if len(sys.argv) == 4:
                conn.admin_reset_password(sys.argv[3])
        if secondarg == "promote":
            if len(sys.argv) == 4:
                conn.admin_promote(sys.argv[3])
        if secondarg == "demote":
            if len(sys.argv) == 4:
                conn.admin_demote(sys.argv[3])
        if secondarg == "promotetoca":
            if len(sys.argv) == 4:
                conn.admin_promotetoca(sys.argv[3])
        if secondarg == "demotefromca":
            if len(sys.argv) == 4:
                conn.admin_demotefromca(sys.argv[3])
        if secondarg == "change_password":
            if len(sys.argv) == 4:
                conn.admin_change_password(sys.argv[3])


    elif firstarg == "usergroups":
        if secondarg == "list":
            conn.usergroups_list()
        if secondarg == "create":
            if len(sys.argv) == 5:
                conn.usergroup_create(sys.argv[3], sys.argv[4])
        if secondarg == "delete":
            if len(sys.argv) == 4:
                conn.usergroup_delete(sys.argv[3])

    elif firstarg == "user_usergroups":
        if secondarg == "list":
            conn.user_usergroups_list()
        if secondarg == "create":
            if len(sys.argv) == 5:
                conn.user_usergroups_create(sys.argv[3], sys.argv[4])
        if secondarg == "delete":
            if len(sys.argv) == 4:
                conn.user_usergroups_delete(sys.argv[3])

    elif firstarg == "servers":
        if secondarg == "list":
            conn.servers_list()

    elif firstarg == "servergroups":
        if secondarg == "list":
            conn.servergroups_list()
        if secondarg == "create":
            if len(sys.argv) == 5:
                conn.servergroup_create(sys.argv[3], sys.argv[4])
        if secondarg == "delete":
            if len(sys.argv) == 4:
                conn.servergroup_delete(sys.argv[3])

    elif firstarg == "server_servergroups":
        if secondarg == "list":
            conn.server_servergroups_list()
        if secondarg == "create":
            if len(sys.argv) == 5:
                conn.server_servergroups_create(sys.argv[3], sys.argv[4])
        if secondarg == "delete":
            if len(sys.argv) == 4:
                conn.server_servergroups_delete(sys.argv[3])

    elif firstarg == "roles":
        if secondarg == "list":
            conn.roles_list()
        if secondarg == "create":
            if len(sys.argv) == 7:
                conn.roles_create(sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
        if secondarg == "delete":
            if len(sys.argv) == 4:
                conn.roles_delete(sys.argv[3])

    elif firstarg == "auth":
        if secondarg == "logout":
            conn.logout()

    else:
        global_help()


#    except Exception as e:
#        print(traceback.format_exception(None, e, e.__traceback__), file=sys.stderr, flush=True)
        
if __name__ == "__main__":
    main()


