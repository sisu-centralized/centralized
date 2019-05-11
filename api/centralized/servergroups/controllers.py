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

servergroups = Blueprint('servergroups', __name__)


# ---------------------------------------------------------------------------------------
# Servergroups

@servergroups.route("/list", methods=['GET'])
@requires_auth
def servergroups_list():
    query = "SELECT id, name, tree FROM servergroup WHERE organization_id = %s"
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [session['ORGANIZATION_ID']])
    return Response(json.dumps(cur.fetchall(), indent=2), mimetype='application/json')

# Getting a servergroup
@servergroups.route("", methods=['GET'])
@requires_auth
def servergroup():
    servergroup_id = request.args.get('id')
    query = "SELECT id, name, tree FROM persongroup WHERE id = %s AND organization_id = %s"
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [servergroup_id, session['ORGANIZATION_ID']])
    return Response(json.dumps(cur.fetchall(), indent=2), mimetype='application/json')

# Create a servergroup
@servergroups.route("", methods=['POST'])
@requires_auth
def create_servergroup():
    current_app.logger.warning('/api/servergroup %s', request.data.decode())

    pp.pprint(request.headers)

    data = request.get_json()
    print(data)
    parentgroup = data['parentgroup']
    name = data['name']

    if not checkgroupname(name):
        return Response("Invalid group name: Must match '^[A-Za-z0-9_]+$' with a limit of 256 characters", status=400, mimetype='text/plain')

    current_app.logger.warning('Received request for /api/servergroup with parentgroup: %s name: %s', parentgroup, name)

    query = "INSERT INTO ServerGroup(organization_id, name, tree) VALUES(%s, %s, text2ltree(concat_ws('.', (SELECT tree FROM ServerGroup WHERE organization_id = %s AND id = %s), %s))) RETURNING id"
    current_app.logger.debug(query)
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    current_app.logger.warning(cur.mogrify(query, [session['ORGANIZATION_ID'], name, session['ORGANIZATION_ID'], parentgroup, name]))

    cur.execute(query, [session['ORGANIZATION_ID'], name, session['ORGANIZATION_ID'], parentgroup, name])
    get_db().commit()
    resulting_id = cur.fetchone()['id']

    return Response(json.dumps(resulting_id, indent=2), mimetype='application/json')

# Update a servergroup
@servergroups.route("", methods=['PUT'])
@requires_auth
def update_servergroup():
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



# Deleting a usergroup
@servergroups.route("", methods=['DELETE'])
@requires_auth
def delete_usergroup():


    # Prohibits deletion of "all".
    # Prohibits deletion of group having subgroups.
    # Prohibits deletion of group part of a role.
    pp.pprint(request.data.decode())

    data = json.loads(request.data.decode())
    sg_id = data['sg_id']

    cur = get_db().cursor(cursor_factory=RealDictCursor)

    # Has subgroups?
    query = " SELECT COUNT(*) AS in_tree, (SELECT COUNT(*) AS attached_roles FROM roles WHERE servergroup_id=%s) FROM servergroup WHERE organization_id = %s AND tree <@ (select tree FROM servergroup WHERE organization_id = %s AND id = %s);"
    cur.execute(query, [sg_id, session['ORGANIZATION_ID'], session['ORGANIZATION_ID'], sg_id])
    res = cur.fetchone()

    if res['in_tree'] > 1:
        return Response("Error, this group has subgroups", status=400, mimetype='text/plain')

    if res['attached_roles'] > 0:
        return Response("Error, this group is attached to a role, cannot delete it, please detach it first.", status=400, mimetype='text/plain')

    # Delete if not "all".
    query = "DELETE FROM servergroup WHERE organization_id = %s AND tree != 'all' AND id=%s"
    cur.execute(query, [session['ORGANIZATION_ID'], sg_id])

    get_db().commit()
    return Response("Done", mimetype='text/plain')

