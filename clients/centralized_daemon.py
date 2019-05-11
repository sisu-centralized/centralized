# -*- coding: utf-8 -*-
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
import requests
import json
import pwd
import grp
import logging
import logging.handlers
import fileinput
import pprint
from readconfig import Config
import sys
import copy

config = Config()
conf = config.getconfig()

url = conf['main']['url']

confdir = "/etc/centralized"

class Groups:
    
    def __init__(self):
        self.groups = {}
        self.groupusers = {}
        self.localgroupsfile = "{}/localgroups".format(confdir)

        if os.path.isfile(self.localgroupsfile):
            with open(self.localgroupsfile) as f:
                for groupname in f:
                    groupname = groupname.rstrip()
                    self.groups[groupname] = False # False means ensure it is not in the system.

                    localgroup = grp.getgrnam(groupname)

                    if groupname not in self.groupusers:
                        self.groupusers[groupname] = {}

                    for localgroupuser in localgroup.gr_mem:
                        self.groupusers[groupname][localgroupuser] = False

    def savelocalgroupfile(self):
        with open(self.localgroupsfile, 'w') as f:
            for group in self.groups:
                f.write("{}\n".format(group))


    def addgroup(self, groupname):
        self.groups[groupname] = True # Ensure it is present in the system


    def adduser_to_group(self, groupname, login):
        if groupname not in self.groupusers:
            self.groupusers[groupname] = {}

        self.groupusers[groupname][login] = True # Ensure it's present.


    def apply_groupchanges(self):
        # Group should exist or not, do what's required.
        for groupname in self.groups:

            try:
                group = grp.getgrnam(groupname)

                if not self.groups[groupname]: # Does exist locally but we don't want it.
                    cmd = "delgroup {}".format(groupname)
                    os.system(cmd)
            except KeyError:
                if self.groups[groupname]: # Doesn't exist locally but we want it.
                    cmd = "addgroup {}".format(groupname)
                    os.system(cmd)

        self.savelocalgroupfile()

    def ensure_user_ingroup(self):
        for groupname in self.groupusers:
            if self.groupusers[groupname]:
                for login in self.groupusers[groupname]:
                    if self.groupusers[groupname][login]:
                        cmd = "adduser {} {}".format(login, groupname)
                        os.system(cmd)
                    else:
                        cmd = "deluser {} {}".format(login, groupname)
                        os.system(cmd)


class UnmanagedGroups:
    def __init__(self):
        self.localugroupsfile = "{}/local_unmanaged_groups".format(confdir)
        self.load()


    def ugroup_for_user(self, user, ugroup):

        if user not in self.users:
            self.users[user] = {}

        self.users[user][ugroup] = True


    def load(self):
        if os.path.isfile(self.localugroupsfile):
            with open(self.localugroupsfile) as json_file:
                self.users = json.load(json_file)
        else:
            self.users = {}


    def save(self):
        with open(self.localugroupsfile, 'w') as fp:
            json.dump(self.users, fp)


    def apply_ugroupchanges(self):
        users_copy = copy.deepcopy(self.users)

        for user in self.users:
            for ugroup in self.users[user]:
                try:
                    grp.getgrnam(ugroup)
                    if self.users[user][ugroup]:
                        cmd = "adduser {} {}".format(user, ugroup)
                        os.system(cmd)
                        users_copy[user][ugroup] = False # Preparing for serialization

                    else:
                        cmd = "deluser {} {}".format(user, ugroup)
                        os.system(cmd)
                        users_copy[user].pop(ugroup, None) # removing for serialization
                except KeyError:
                    log.info("Skipping membership of user {} to unmanaged group {}. Group doesn't exist".format(self.login, ugroup))
        self.users = users_copy
        self.save()


class User:
    def __init__(self, user, g, ug):
        self.uid = user['id']
        self.login = user['login']
        self.pubkey = user['pubkey']
        self.active = user['person_active']
        self.groupname = user['groupname']
        self.sudoline = user['sudoline']
        self.roleid = user['roleid']
        self.ssh = user['ssh']
        self.home = ""

        if self.active:
            g.addgroup(self.groupname)
            g.adduser_to_group(self.groupname, self.login)

        log.info("User: {}/{}".format(self.login, self.uid))

        if self.user_exists():
            self.user_loadsysteminfo()

        unmanaged_groups = user['unmanaged_groups']
        if len(unmanaged_groups) > 0:
            ugroups = unmanaged_groups.split(',')
            for ugroup in ugroups:
                ug.ugroup_for_user(self.login, ugroup)




    def user_loadsysteminfo(self):
        self.home = self.user_get_home()
        self.keys_dir = "{}/.ssh".format(self.home)
        self.authorized = "{}/authorized_keys".format(self.keys_dir)
        self.gid = grp.getgrnam(self.login).gr_gid


    def user_get_home(self):
        passwd_entry = pwd.getpwuid(self.uid)
        pprint.pprint(passwd_entry.pw_dir)
        return passwd_entry.pw_dir


    # Behaviour can be modified in /etc/adduser.conf
    def user_create(self):
        #options = "--no-create-home"
        options = ""
        cmd = "adduser --shell /bin/bash --uid {} --gecos 'Added by centralized.pw' --disabled-password {} {}".format(self.uid, options, self.login)
        os.system(cmd)
        self.user_loadsysteminfo()
        self.home = self.user_get_home()


    def user_enable(self):
        if self.ssh == 0:
            return
        #rights = 0700 # Python2
        rights = 0o700

        if not os.path.isdir(self.keys_dir):
            os.mkdir(self.keys_dir, rights)
        with open(os.open(self.authorized, os.O_CREAT | os.O_WRONLY, 0o700), 'w+') as fh:
            fh.write("{}\n".format(self.pubkey))

        os.chown(self.authorized, self.uid, self.gid)
        os.chown(self.keys_dir, self.uid, self.gid)


    def user_disable(self):
        if os.path.exists(self.authorized):
            os.remove(self.authorized)


    def user_update(self):
        if self.active and self.ssh == 1:
            self.user_enable()
        else:
            self.user_disable()


    def user_exists(self):
        by_login = os.system("id {}".format(self.login))
        by_uid   = os.system("id {}".format(self.uid))
        return by_login == 0 and by_uid == 0



    def create_sudoline(self):
        return "%{} {} # ROLEID{}".format(self.groupname, self.sudoline, self.roleid)


class Sudo:
    def __init__(self):
        path = "/etc/sudoers.d/centralized"
        self.hash = {}
        try:
            self.sudoersfile = open(path, "w")
        except FileNotFoundError:
            log.info("{} cannot be opened, no sudo line will be written.")

    def writeline(self, line):
        self.hash[line] = ""

    def close(self):
        try:
            for key in self.hash:
                self.sudoersfile.write("{}\n".format(key))
            self.sudoersfile.close()
        except AttributeError:
            log.debug("No attribute sudoersfile, no writting/closing.")


def main():
    log.setLevel(logging.DEBUG)

    handler = logging.handlers.SysLogHandler(address = '/dev/log')
    formatter = logging.Formatter('%(module)s.%(funcName)s: %(message)s')
    handler.setFormatter(formatter)

    log.addHandler(handler)

    log.info("Starting execution:")
    uuid_path = "/.uuid_centralized"
    if not os.path.isfile(uuid_path):
        print("Server not registered (or {} was deleted)".format(uuid_path))
        sys.exit(1)

    uuid = open(uuid_path).readline() #.rstrip()

    r = requests.get("{}/ugsg/creds?uuid={}".format(url, uuid))

    lst = json.loads(r.text)
    log.debug(pprint.pformat(lst, indent=4))


    #rights = 0700 # Python2
    rights = 0o700
    if not os.path.isdir(confdir):
        os.mkdir(confdir, rights)

    s = Sudo()
    g = Groups()
    ug = UnmanagedGroups()

    for user in lst:
        u = User(user, g, ug)
        if u.user_exists(): # user exists, let's see if it need to be updated.
            u.user_update()
        else:
            if u.active:
                u.user_create()
                u.user_enable()

        s.writeline(u.create_sudoline())

    g.apply_groupchanges()
    g.ensure_user_ingroup()
    ug.apply_ugroupchanges()
    s.close()
    log.info("Ending execution:")

if __name__ == "__main__":
    log = logging.getLogger(__name__)
    main()




