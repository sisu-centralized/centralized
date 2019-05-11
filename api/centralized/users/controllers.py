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

from psycopg2.extras import RealDictCursor

import json
from flask import Response, request, current_app, session
from flask import Blueprint
from centralized.common.decorators import requires_auth, requires_company_admin
from centralized.common.helpers import get_db, gen_random_password, reset_password, update_admin_password, demote_user_from_admin, promote_user_to_admin, demote_user_from_companyadmin, promote_user_to_companyadmin #, request_password_reset, reset_password, promote_user_to_admin, demote_user_from_admin, gen_random_password


import pprint
pp = pprint.PrettyPrinter(indent=4)

users = Blueprint('users', __name__)

@users.route('/test')
def users_test():
    return Response('test ok.', mimetype='text/plain')

@users.route("/list", methods=['GET'])
@requires_auth
def users_list():
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    query = "SELECT id, login, first_name, contact_email, ou.person_active AS active, CAST((CASE WHEN admin_passwd_hash IS NULL THEN 'f' ELSE 't' END) AS BOOLEAN) AS is_admin, ou.is_company_admin FROM Person JOIN organization_user AS ou ON ou.person_id = Person.id WHERE ou.organization_id=%s ORDER BY login;"
    cur.execute(query, [session['ORGANIZATION_ID']])
    current_app.logger.info("Organization id by session {}".format(session['ORGANIZATION_ID']))
    return Response(json.dumps(cur.fetchall(), indent=2), mimetype='application/json')


# Enable user
@users.route("", methods=['POST'])
@requires_auth
def enable_user():
    current_app.logger.warning('/api/user %s', request.data.decode())

    data = json.loads(request.data.decode())
    user_id = data['user_id']

    current_app.logger.warning('Received request for /api/user with user_id: %s', user_id)

    query = "update organization_user set person_active='t' where organization_id=%s AND person_id=%s"
    current_app.logger.debug(query)
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [session['ORGANIZATION_ID'], user_id])
    get_db().commit()

    return Response("Done.", mimetype='text/plain')


@users.route("/getsessioninfo", methods=['GET'])
@requires_auth
def getsessioninfo():
    sessioninfo_published = {}
    sessioninfo_published['is_admin'] = session['is_admin']
    sessioninfo_published['is_company_admin'] = session['is_company_admin']
    return Response(json.dumps(sessioninfo_published), mimetype='application/json')




# Disable user
@users.route("", methods=['DELETE'])
@requires_auth
def disable_user():
    current_app.logger.warning('/api/user %s', request.data.decode())

    data = json.loads(request.data.decode())
    user_id = data['user_id']

    current_app.logger.warning('Received request for /api/user with user_id: %s', user_id)

    query = "update organization_user set person_active='f' where organization_id=%s AND person_id=%s"
    current_app.logger.debug(query)
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [session['ORGANIZATION_ID'], user_id])
    get_db().commit()

    return Response("Done.", mimetype='text/plain')


# @users.route("/api/groupusers", methods=['GET']) # List user logins that belong to a group or it's subgroups
# @requires_auth
# def users_in_group_and_subgroups():
#     query = ("SELECT p.login FROM person AS p "
#             "JOIN person_persongroup AS p_pg ON p.id = p_pg.person_id "
#             "JOIN persongroup AS pg ON pg.id = p_pg.persongroup_id "
#             "WHERE p_pg.persongroup_id IN (SELECT id from persongroup where organization_id = %s AND tree <@ 'all.engineers')")
#     cur = get_db().cursor(cursor_factory=RealDictCursor)
#     cur.execute(query, [ORGANIZATION_ID])
#     return Response(json.dumps(cur.fetchall(), indent=2), mimetype='application/json')


@users.route("/password/update/<newpassword>", methods=['POST'])
@requires_auth
def password_update(newpassword):

    if update_admin_password(session['login'], newpassword):
        session['logged'] = False
        return Response("Done.", mimetype='text/plain')

    return Response("An issue happened.", mimetype='text/plain')


@users.route("/password/reset/<login>", methods=['POST'])
@requires_auth
@requires_company_admin
def reset_user_password(login):
    random_password = gen_random_password()
    current_app.logger.warning('reset_user_password called by {} for user {}'.format(session['login'], login))

    if reset_password(login, random_password):
        return Response("Done.", mimetype='text/plain')

    return Response("An issue happened.", mimetype='text/plain')


@users.route("/promote/<login>", methods=['POST'])
@requires_auth
@requires_company_admin
def promote_user(login):
    if promote_user_to_admin(login):
        return Response("Done.", mimetype='text/plain')

    return Response("An issue happened.", mimetype='text/plain')


@users.route("/demote/<login>", methods=['POST'])
@requires_auth
@requires_company_admin
def demote_user(login):

    if demote_user_from_admin(login):
        return Response("Done.", mimetype='text/plain')

    return Response("An issue happened.", mimetype='text/plain')


# Promota to company admin
@users.route("/promotetoca/<login>", methods=['POST'])
@requires_auth
@requires_company_admin
def promote_user_toca(login):
    if promote_user_to_companyadmin(login):
        return Response("Done.", mimetype='text/plain')

    return Response("An issue happened.", mimetype='text/plain')

# Demote from company admin
@users.route("/demotefromca/<login>", methods=['POST'])
@requires_auth
@requires_company_admin
def demote_user_fromca(login):

    if demote_user_from_companyadmin(login):
        return Response("Done.", mimetype='text/plain')

    return Response("An issue happened.", mimetype='text/plain')
