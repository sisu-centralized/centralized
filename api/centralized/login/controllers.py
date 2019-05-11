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

from flask import Response, session
from flask import Blueprint


import pprint
pp = pprint.PrettyPrinter(indent=4)

auth = Blueprint('auth', __name__)

# ---------------------------------------------------------------------------------------
# Login / Logout

# https://www.postgresql.org/docs/8.3/static/pgcrypto.html

@auth.route("/login", methods=['POST'])
def login():
    return Response("Not implemented", mimetype='text/plain')

@auth.route("/logout", methods=['POST'])
#@requires_auth
def logout():
    session['logged'] = False
    session['ORGANIZATION_ID'] = 0

    return Response("Logged out.", mimetype='text/plain')



