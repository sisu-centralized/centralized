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

server_servergroups = Blueprint('server_servergroup', __name__)


# ---------------------------------------------------------------------------------------
# Servergroups

@server_servergroups.route("/list", methods=['GET'])
@requires_auth
def servergroup_server_list():
    query = "select ssg.id AS ssg_id, s.uuid AS s_uuid, s.hostname AS s_hostname, sg.name AS SG_name, sg.tree AS sg_tree FROM server_servergroup AS ssg JOIN server AS s ON s.id = ssg.server_id JOIN servergroup AS sg ON sg.id = ssg.servergroup_id WHERE sg.organization_id = %s"
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [session['ORGANIZATION_ID']])
    return Response(json.dumps(cur.fetchall(), indent=2), mimetype='application/json')

# Getting a servergroup
@server_servergroups.route("", methods=['GET'])
@requires_auth
def servergroup_server():
    servergroup_id = request.args.get('id')
    query = "select ssg.id AS ssg_id, s.uuid AS s_uuid, s.hostname AS s_hostname, sg.name AS SG_name, sg.tree AS sg_tree FROM server_servergroup AS ssg JOIN server AS s ON s.id = ssg.id JOIN servergroup AS sg ON sg.id = ssg.servergroup_id WHERE ssg.id = %s AND sg.organization_id = %s"
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [servergroup_id, session['ORGANIZATION_ID']])
    return Response(json.dumps(cur.fetchall(), indent=2), mimetype='application/json')

# Create a server_servergroup link
@server_servergroups.route("", methods=['POST'])
@requires_auth
def create_servergroup_server():
    current_app.logger.warning('/api/servergroup %s', request.data.decode())

    pp.pprint(request.headers)
    data = request.get_json()
    print(data)
    servergroup_id = data['servergroup_id']
    uuid = data['uuid']

    current_app.logger.warning('Received request for /api/server_servergroup with servergroup_id: %s uuid: %s', servergroup_id, uuid)
    query = ( "INSERT INTO server_servergroup(server_id, servergroup_id) "
              "VALUES((SELECT id FROM Server JOIN organization_server ON Server.id = organization_server.server_id WHERE Server.uuid=%s AND organization_server.organization_id=%s), "
              "(SELECT id FROM servergroup where organization_id=%s AND id=%s)) RETURNING id"
              )
    print(query)
    current_app.logger.debug(query)
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [uuid, session['ORGANIZATION_ID'], session['ORGANIZATION_ID'], servergroup_id])
    get_db().commit()
    resulting_id = cur.fetchone()['id']

    return Response(json.dumps(resulting_id, indent=2), mimetype='application/json')

# Update a servergroup
@server_servergroups.route("", methods=['PUT'])
@requires_auth
def update_servergroup_server():
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



# Delete server_servergroup
@server_servergroups.route("", methods=['DELETE'])
@requires_auth
def delete_servergroup_server():
    current_app.logger.warning('/api/server_servergroup %s', request.data.decode())
    pp.pprint(request.headers)

    data = json.loads(request.data.decode())
    ssg_id = data['ssg_id']

    cur = get_db().cursor(cursor_factory=RealDictCursor)

    # Get the tree before it's modified.
    query = "DELETE FROM server_servergroup AS ssg USING servergroup AS sg WHERE sg.id = ssg.servergroup_id AND sg.organization_id=%s AND ssg.id = %s"
    cur.execute(query, [session['ORGANIZATION_ID'], ssg_id])
    get_db().commit()

    return Response("Done", mimetype='text/plain')

