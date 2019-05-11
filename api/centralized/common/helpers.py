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

import re
import random
import string
import json
import psycopg2

from flask import Flask, session
from psycopg2.extras import RealDictCursor
from centralized.common.python_smtp import send_email

import logging
from logging.handlers import RotatingFileHandler

from importlib.machinery import SourceFileLoader

import pprint
from flask import g
pp = pprint.PrettyPrinter(indent=4)


app = Flask(__name__)
handler = RotatingFileHandler('api.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)


app.logger.info('Starting centralized.')

def get_db():
    """Opens a new database connection if there is none yet for the current application context. """
    if not hasattr(g, 'pg_db'):
        dbconfig = SourceFileLoader("config", "/opt/config").load_module()
        dbstr = dbconfig.DATABASES['default']['dsn']
        g.pg_db = psycopg2.connect(dbstr)
    return g.pg_db

def checkgroupname(name):
    # No more than 256 characters
    # A-Za-z0-9_
    if len(name) > 256:
        return False
    return re.match('^[A-Za-z0-9_]+$', name)


def gen_random_password():
    char_set = string.ascii_uppercase + string.digits
    return ''.join(random.sample(char_set * 6, 6))


def update_admin_password(login, newpassword):
    """
    Updates the admin password for the user.
    This doesn't allow to set the password the first time.
    :param login:
    :param newpassword:
    :return: True if changed, False otherwise.
    """
    query = "UPDATE Person SET admin_passwd_hash=crypt(%s, gen_salt('md5')) FROM organization_user AS ou WHERE ou.person_id = Person.id AND ou.organization_id=%s AND login=%s"
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [newpassword, session['ORGANIZATION_ID'], login])
    get_db().commit()

    if cur.rowcount == 1:
        session['logged'] = False
        return True
    return False


# Done by admin.
def reset_password(login, newpassword):
    query = "UPDATE Person SET admin_passwd_hash=crypt(%s, gen_salt('md5')) FROM organization_user AS ou WHERE admin_passwd_hash IS NOT NULL AND ou.person_id = Person.id AND ou.organization_id=%s AND login=%s RETURNING contact_email"
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [newpassword, session['ORGANIZATION_ID'], login])
    get_db().commit()
    try:
        if cur.rowcount == 1:
            result = cur.fetchone()
            email = result['contact_email']
            send_email([ email ], newpassword)
            return True
    except TypeError:
        return False

# Done by superadmin
def promote_user_to_admin(login):
    query = "UPDATE Person SET admin_passwd_hash='bogusvalue' FROM organization_user AS ou WHERE ou.person_id = Person.id AND ou.organization_id=%s AND login=%s"

    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [session['ORGANIZATION_ID'], login])
    get_db().commit()
    if cur.rowcount == 1:
        reset_password(login, gen_random_password())
        return True
    return False

# Done by superadmin
def demote_user_from_admin(login):
    query = "UPDATE Person SET admin_passwd_hash=NULL FROM organization_user AS ou WHERE ou.person_id = Person.id AND ou.organization_id=%s AND login=%s"
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [session['ORGANIZATION_ID'], login])
    get_db().commit()
    return cur.rowcount == 1


def promote_user_to_companyadmin(login):
    query = "UPDATE organization_user AS ou SET is_company_admin='t' FROM Person WHERE ou.person_id = Person.id AND ou.organization_id=%s AND login=%s"

    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [session['ORGANIZATION_ID'], login])
    get_db().commit()
    return cur.rowcount == 1


# Done by superadmin
def demote_user_from_companyadmin(login):
    query = "UPDATE organization_user AS ou SET is_company_admin='f' FROM Person WHERE ou.person_id = Person.id AND ou.organization_id=%s AND login=%s"
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [session['ORGANIZATION_ID'], login])
    get_db().commit()
    return cur.rowcount == 1



