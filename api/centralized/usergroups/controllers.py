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
from centralized.common.helpers import get_db, checkgroupname


import pprint
pp = pprint.PrettyPrinter(indent=4)

usergroups = Blueprint('usergroups', __name__)


# ---------------------------------------------------------------------------------------
# Usergroups

# Listing usergroups
@usergroups.route("/list", methods=['GET'])
@requires_auth
def usergroups_list():
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    uid = request.args.get('uid', 0, type=int)
    current_app.logger.warning("/api/usergroup/list?uid={}".format(uid))
    if uid != 0:
        query = "SELECT pg.id, name, tree FROM persongroup AS pg JOIN person_persongroup AS ppg ON pg.id = ppg.persongroup_id WHERE organization_id = %s AND ppg.person_id=%s"
        cur.execute(query, [session['ORGANIZATION_ID'], uid])
    else:
        query = "select id, name, tree from persongroup where organization_id = %s"
        cur.execute(query, [session['ORGANIZATION_ID']])
    return Response(json.dumps(cur.fetchall(), indent=2), mimetype='application/json')

# Getting info about a usergroup
@usergroups.route("/", methods=['GET'])
@requires_auth
def usergroup():
    persongroup_id = request.args.get('id')
    query = "SELECT id, name, tree FROM persongroup WHERE id = %s AND organization_id = %s"
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [persongroup_id, session['ORGANIZATION_ID']])
    return Response(json.dumps(cur.fetchall(), indent=2), mimetype='application/json')

# Creating a usergroup
@usergroups.route("", methods=['POST'])
@requires_auth
def create_usergroup():
    current_app.logger.warning('/api/usergroup %s', request.data.decode())

    data = json.loads(request.data.decode())
    parentgroup = data['parentgroup']
    name = data['name']

    current_app.logger.warning('Received request for /api/usergroup with parentgroup: %s name: %s', parentgroup, name)

    if not checkgroupname(name):
        return Response("Invalid group name: Must match '^[A-Za-z0-9_]+$' with a limit of 256 characters", status=400, mimetype='text/plain')


    query = "INSERT INTO PersonGroup(organization_id, name, tree) VALUES(%s, %s, text2ltree(concat_ws('.', (SELECT tree FROM PersonGroup WHERE organization_id = %s AND id = %s), %s))) RETURNING id"
    current_app.logger.debug(query)
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [session['ORGANIZATION_ID'], name, session['ORGANIZATION_ID'], parentgroup, name])
    get_db().commit()
    resulting_id = cur.fetchone()['id']

    return Response(json.dumps(resulting_id, indent=2), mimetype='application/json')

# Changing a usergroup
# Could be done in two statements: https://stackoverflow.com/questions/7923237/return-pre-update-column-values-using-sql-only-postgresql-version
@usergroups.route("", methods=['PUT'])
@requires_auth
def update_usergroup():

    pp.pprint(request.data.decode())

    data = json.loads(request.data.decode())
    name = data['name']
    id = data['id']

    cur = get_db().cursor(cursor_factory=RealDictCursor)

    # Get the tree before it's modified.
    query = "SELECT tree FROM PersonGroup where organization_id=%s AND id=%s"
    cur.execute(query, [session['ORGANIZATION_ID'], id])
    oldparentgroup = cur.fetchone()['tree']

    # Modify the PersonGroup entry name + tree
    query = "UPDATE PersonGroup SET name=%s, tree=subpath(tree, 0, nlevel(tree) -1) || %s WHERE id=%s AND organization_id=%s RETURNING tree"
    cur.execute(query, [name, name, id, session['ORGANIZATION_ID']])
    newparentgroup = cur.fetchone()['tree']

    # Update PersonGroup children
    query = "UPDATE PersonGroup SET tree=%s || subpath(tree, nlevel(%s)) WHERE organization_id=%s AND tree <@ %s AND tree != %s"
    cur.execute(query, [newparentgroup, oldparentgroup, session['ORGANIZATION_ID'], oldparentgroup, oldparentgroup])

    get_db().commit()
    return Response("Done", mimetype='text/plain')


# Deleting a usergroup
@usergroups.route("", methods=['DELETE'])
@requires_auth
def delete_usergroup():


    # Prohibits deletion of "all".
    # Prohibits deletion of group having subgroups.
    # Prohibits deletion of group part of a role.
    pp.pprint(request.data.decode())

    data = json.loads(request.data.decode())
    ug_id = data['ug_id']

    cur = get_db().cursor(cursor_factory=RealDictCursor)

    # Has subgroups?
    query = " SELECT COUNT(*) AS in_tree, (SELECT COUNT(*) AS attached_roles FROM roles WHERE persongroup_id=%s) FROM persongroup WHERE organization_id = %s AND tree <@ (select tree FROM persongroup WHERE organization_id = %s AND id = %s);"
    cur.execute(query, [ug_id, session['ORGANIZATION_ID'], session['ORGANIZATION_ID'], ug_id])
    res = cur.fetchone()

    if res['in_tree'] > 1:
        return Response("Error, this group has subgroups", status=400, mimetype='text/plain')

    if res['attached_roles'] > 0:
        return Response("Error, this group is attached to a role, cannot delete it, please detach it first.", status=400, mimetype='text/plain')

    # Delete if not "all".
    query = "DELETE FROM persongroup WHERE organization_id = %s AND tree != 'all' AND id=%s"
    cur.execute(query, [session['ORGANIZATION_ID'], ug_id])

    get_db().commit()
    return Response("Done", mimetype='text/plain')


