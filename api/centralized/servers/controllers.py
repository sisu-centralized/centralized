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
from psycopg2 import IntegrityError
from flask import Response, request, session
from flask import Blueprint
from centralized.common.decorators import requires_auth
from centralized.common.helpers import get_db


import pprint
pp = pprint.PrettyPrinter(indent=4)

servers = Blueprint('servers', __name__)

# ---------------------------------------------------------------------------------------
# Servers


@servers.route("/list", methods=['GET'])
@requires_auth
def servers_list():
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    query = ("SELECT uuid, hostname FROM server JOIN organization_server AS os ON os.server_id = server.id WHERE os.organization_id = %s")
    cur.execute(query, [session['ORGANIZATION_ID']])
    return Response(json.dumps(cur.fetchall(), indent=2), mimetype='application/json')


@servers.route("/register", methods=['POST'])
def register_server():
    data = json.loads(request.data.decode())
    cur = get_db().cursor()

    QUERY_UPSERT_SERVER = "INSERT INTO server(uuid, hostname) VALUES(%s, %s) ON CONFLICT(uuid) DO UPDATE SET modified=now() RETURNING id"
    cur.execute(QUERY_UPSERT_SERVER, [data['uuid'], data['hostname']])
    server_id = cur.fetchone()[0]


    # TODO: fix to use ON CONFLICT on both organization_id and server_id
    cur.execute("SELECT COUNT(*) FROM organization_server WHERE organization_id=(SELECT id from organization where uuid=%s) AND server_id=%s", [data['organization_uuid'], server_id])
    count = cur.fetchone()[0]

    if count == 0:
        print("Inserting relationship.")

        QUERY_INSERT_SERVER = "INSERT INTO organization_server(organization_id, server_id, server_active) VALUES((SELECT id from organization where uuid=%s), %s, %s)"
        try:
            cur.execute(QUERY_INSERT_SERVER, [data['organization_uuid'], server_id, True])
        except IntegrityError:
            return Response("An error has occured. Please check your organization UUID is correct or contact centralized.")

    get_db().commit()
    return Response("{} {} {}".format(data['organization_uuid'], server_id, count), mimetype='text/plain')



# Delete server
@servers.route("/", methods=['DELETE'])
@requires_auth
def delete_server():
    return Response("Not implemented", mimetype='text/plain')

