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
from centralized.common.decorators import requires_auth
from centralized.common.helpers import get_db


import pprint
pp = pprint.PrettyPrinter(indent=4)

user_usergroups = Blueprint('user_usergroups', __name__)


# ---------------------------------------------------------------------------------------
# Servergroups

# centralized_test=# select * from person;
#  id | login | first_name | last_name | contact_email | source | created | modified
# ----+-------+------------+-----------+---------------+--------+---------+----------
# (0 rows)
#
# centralized_test=# select * from persongroup;
#  id | organization_id | name | tree
# ----+-----------------+------+------
#   1 |               1 | All  | all
# (1 row)
#
# centralized_test=# select * from person_persongroup;
#  id | person_id | persongroup_id
# ----+-----------+----------------
# (0 rows)






@user_usergroups.route("/list", methods=['GET'])
@requires_auth
def user_usergroups_list():
    query = "SELECT ppg.id AS id, p.id AS user_id, p.login, pg.name AS groupname, pg.tree AS grouptree FROM person_persongroup AS ppg JOIN person AS p ON ppg.person_id = p.id JOIN persongroup AS pg ON pg.id = ppg.persongroup_id WHERE pg.organization_id = %s"
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [session['ORGANIZATION_ID']])
    return Response(json.dumps(cur.fetchall(), indent=2), mimetype='application/json')

# Getting a servergroup
@user_usergroups.route("", methods=['GET'])
@requires_auth
def user_usergroup():
    user_usergroup_id = request.args.get('id')
    query = " SELECT * FROM person_persongroup AS ppg JOIN organization_user AS ou ON ppg.person_id = ou.person_id WHERE ou.organization_id=1 AND ppg.id=1;"

    query = "SELECT id, name, tree FROM persongroup WHERE id = %s AND organization_id = %s"
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [user_usergroup_id, session['ORGANIZATION_ID']])
    return Response(json.dumps(cur.fetchall(), indent=2), mimetype='application/json')

# Create a user_usergroup link
@user_usergroups.route("", methods=['POST'])
@requires_auth
def create_user_usergroup():
    current_app.logger.warning('/api/servergroup %s', request.data.decode())

    pp.pprint(request.headers)
    data = request.get_json()
    print(data)
    usergroup_id = data['usergroup_id']
    login = data['login']

    current_app.logger.warning('Received request for /api/user_usergroup with usergroup_id: %s login: %s', usergroup_id, login)
    query = ( "INSERT INTO person_persongroup(person_id, persongroup_id) "
              "VALUES((SELECT id FROM Person JOIN organization_user ON Person.id = organization_user.person_id WHERE Person.login=%s AND organization_user.organization_id=%s), "
              "(SELECT id FROM persongroup where organization_id=%s AND id=%s)) RETURNING id"
              )
    current_app.logger.debug(query)
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [login, session['ORGANIZATION_ID'], session['ORGANIZATION_ID'], usergroup_id])
    get_db().commit()
    resulting_id = cur.fetchone()['id']

    return Response(json.dumps(resulting_id, indent=2), mimetype='application/json')

# Update a user_usergroup
@user_usergroups.route("", methods=['PUT'])
@requires_auth
def update_user_usergroup():
    current_app.logger.warning('/api/servergroup %s', request.data.decode())
    pp.pprint(request.headers)
    data = json.loads(request.data.decode())
    #data = request.get_json()


    print('------')
    pp.pprint(data)
    print('------')

    name = data['name']
    id = data['id']

    cur = get_db().cursor(cursor_factory=RealDictCursor)

    # Get the tree before it's modified.
    query = "SELECT tree FROM ServerGroup where organization_id=%s AND id=%s"
    cur.execute(query, [session['ORGANIZATION_ID'], id])
    oldparentgroup = cur.fetchone()['tree']

    # Modify the PersonGroup entry name + tree
    query = "UPDATE ServerGroup SET name=%s, tree=subpath(tree, 0, nlevel(tree) -1) || %s WHERE id=%s AND organization_id=%s RETURNING tree"
    cur.execute(query, [name, name, id, session['ORGANIZATION_ID']])
    newparentgroup = cur.fetchone()['tree']

    # Update PersonGroup children
    query = "UPDATE ServerGroup SET tree=%s || subpath(tree, nlevel(%s)) WHERE organization_id=%s AND tree <@ %s AND tree != %s"
    cur.execute(query, [newparentgroup, oldparentgroup, session['ORGANIZATION_ID'], oldparentgroup, oldparentgroup])

    get_db().commit()
    return Response("Done", mimetype='text/plain')



# Delete user_usergroup
@user_usergroups.route("", methods=['DELETE'])
@requires_auth
def delete_user_usergroup():
    current_app.logger.warning('/api/user_usergroup %s', request.data.decode())
    pp.pprint(request.headers)

    data = json.loads(request.data.decode())
    uug_id = data['uug_id']

    cur = get_db().cursor(cursor_factory=RealDictCursor)

    # Get the tree before it's modified.
    query = "DELETE FROM person_persongroup AS ppg USING persongroup AS pg WHERE pg.id = ppg.persongroup_id AND pg.organization_id=%s AND ppg.id = %s"
    cur.execute(query, [session['ORGANIZATION_ID'], uug_id])
    get_db().commit()

    return Response("Done", mimetype='text/plain')

