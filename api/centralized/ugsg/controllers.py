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
from flask import Response, current_app, request, session
from flask import Blueprint
from centralized.common.decorators import requires_auth
from centralized.common.helpers import get_db


import pprint
pp = pprint.PrettyPrinter(indent=4)

ugsgs = Blueprint('ugsgs', __name__)

# ---------------------------------------------------------------------------------------
# UsergroupServergroup relationships

# Get ugsgs list
@ugsgs.route("/list", methods=['GET'])
@requires_auth
def ugsg_list():
    query = "SELECT roles.id, pg.name AS usergroup, pg.tree AS usergroup_tree, sg.name AS servergroup, sg.tree AS servergroup_tree, sudoline, ssh, unmanaged_groups FROM roles JOIN persongroup AS pg ON roles.persongroup_id = pg.id JOIN servergroup AS sg ON roles.servergroup_id = sg.id WHERE roles.organization_id=%s"
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute(query, [session['ORGANIZATION_ID']])
    return Response(json.dumps(cur.fetchall(), indent=2), mimetype='application/json')


# Get ugsg
@ugsgs.route("/", methods=['GET'])
@requires_auth
def ugsg():
    return Response("Not implemented", mimetype='text/plain')


# Create ugsg
@ugsgs.route("/", methods=['POST'])
@requires_auth
def create_ugsg():
    data = json.loads(request.data.decode())

    ug_id = data['ug_id']
    sg_id = data['sg_id']
    sudoline = data['sudoline']
    ugroups = data['ugroups']
    cur = get_db().cursor(cursor_factory=RealDictCursor)

    QUERY_UPSERT_SERVER = "INSERT INTO roles(organization_id, persongroup_id, servergroup_id, sudoline, unmanaged_groups) VALUES(%s, %s, %s, %s, %s) RETURNING id"
    cur.execute(QUERY_UPSERT_SERVER, [session['ORGANIZATION_ID'], ug_id, sg_id, sudoline, ugroups])

    get_db().commit()
    resulting_id = cur.fetchone()['id']

    return Response(json.dumps(resulting_id, indent=2), mimetype='application/json')

# Update ugsg
@ugsgs.route("/", methods=['PUT'])
@requires_auth
def update_ugsg():
    return Response("Not implemented", mimetype='text/plain')

# Delete ugsg
@ugsgs.route("/", methods=['DELETE'])
@requires_auth
def delete_ugsg():
    data = json.loads(request.data.decode())
    cur = get_db().cursor(cursor_factory=RealDictCursor)

    roleid = data['id']
    QUERY_DELETE = "DELETE FROM roles WHERE id = %s AND organization_id = %s"
    cur.execute(QUERY_DELETE, [roleid, session['ORGANIZATION_ID']])

    get_db().commit()


    return Response("Done.", mimetype='text/plain')


# SELECT * FROM roles WHERE servergroup_id = (SELECT servergroup_id FROM server AS s JOIN server_servergroup AS ssg ON s.id = ssg.server_id WHERE s.uuid='8883a511-40e7-4481-b053-64b1e07a7782');

@ugsgs.route("/creds", methods=['GET'])
def getcreds():
    uuid = request.args.get('uuid')

    query = ( "select p.login, p.id, p.first_name, p.last_name, p.contact_email, r.ssh, r.sudoline, r.id AS roleid, pubkey.pubkey, pubkey.pubkey_md5hash, ou.person_active, pg1.name AS groupname, unmanaged_groups "
        "from persongroup AS pg1 "
            "INNER JOIN person_persongroup AS ppg ON ppg.persongroup_id = pg1.id "
            "INNER JOIN person AS p ON p.id = ppg.person_id "
            "INNER JOIN pubkey ON p.id = pubkey.person_id "
            "INNER JOIN organization_user AS ou ON ou.person_id = p.id, "
        "roles AS r "
            "INNER JOIN persongroup AS pg2 ON pg2.id = r.persongroup_id "
        "WHERE pg1.tree <@ pg2.tree "
            "AND ou.person_active = 't' "
            "AND servergroup_id IN "
                "(select id from servergroup "
                    "WHERE tree @> "
                    "(SELECT array_agg(sg.tree) "
                        "FROM server "
                        "INNER JOIN server_servergroup AS ssg ON server.id = ssg.server_id "
                        "INNER JOIN servergroup AS sg ON sg.id = ssg.servergroup_id "
                        "WHERE uuid=%s))" )

    cur = get_db().cursor(cursor_factory=RealDictCursor)

    current_app.logger.warning(cur.mogrify(query, [uuid]))

    cur.execute(query, [uuid])
    return Response(json.dumps(cur.fetchall(), indent=2), mimetype='application/json')


