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

from flask import Flask, session

from functools import wraps
from flask import request, Response, current_app
from psycopg2.extras import RealDictCursor
from centralized.common.helpers import get_db

import pprint
pp = pprint.PrettyPrinter(indent=4)


# https://www.postgresql.org/docs/8.3/static/pgcrypto.html
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    query = "select organization_id, admin_passwd_hash = crypt(%s, admin_passwd_hash) AS password_ok, login, is_company_admin, CAST((CASE WHEN admin_passwd_hash IS NULL THEN 'f' ELSE 't' END) AS BOOLEAN) AS is_admin FROM person JOIN organization_user AS ou ON person.id = ou.person_id where ou.person_active='t' AND login=%s"
    print("Query: {} {} {}".format(query, password, username))
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [password, username])

    result = cur.fetchone()
    pp.pprint(result)
    if result['password_ok']:
        session['ORGANIZATION_ID'] = result['organization_id']
        session['login'] = result['login']
        session['is_admin'] = result['is_admin']
        session['is_company_admin'] = result['is_company_admin']
        return True
    return False



def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        current_app.logger.warning("Content of session before checking if already auth'ed: {}".format(pp.pformat(session)))

        current_app.logger.warning(session.get('logged'))

        if 'logged' in session:
            current_app.logger.warning("logged in session")

        if 'logged' in session and session['logged']:
            current_app.logger.warning("session['logged'] is True")


        if 'logged' in session and session['logged']:
            current_app.logger.warning("Already logged, no need to auth again")
            return f(*args, **kwargs)

        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()

        current_app.logger.warning("Login success, setting session value.")
        session['logged'] = True
        return f(*args, **kwargs)
    return decorated



def only_company_admin():
    """Sends a 400 response, only company admin can do that."""
    return Response(
    'This command is only allowed to company admins.', 400)


def requires_company_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        current_app.logger.warning("Entering decorated for requires_company_admin decorator")

        if not session['is_company_admin']:
            return only_company_admin()

        current_app.logger.warning("The user {} is detected as a company admin, proceeding.".format(session['login']))
        return f(*args, **kwargs)
    return decorated
