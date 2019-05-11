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
from flask import request, Response
from flask_sessionstore import Session

import pprint
import logging
from logging.handlers import RotatingFileHandler

from centralized.users.controllers import users
from centralized.usergroups.controllers import usergroups
from centralized.user_usergroup.controllers import user_usergroups
from centralized.servers.controllers import servers
from centralized.servergroups.controllers import servergroups
from centralized.server_servergroup.controllers import server_servergroups
from centralized.ugsg.controllers import ugsgs
from centralized.login.controllers import auth

pp = pprint.PrettyPrinter(indent=4)



app = Flask(__name__)
handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

SESSION_TYPE = 'filesystem'
app.config['SESSION_TYPE'] = 'filesystem'
app.config.from_object(__name__)
Session(app)

API_VERSION='1.0'

app.url_map.strict_slashes = False

app.logger.info('Starting centralized.')
app.register_blueprint(users,           url_prefix='/api/{}/user'.format(API_VERSION))
app.register_blueprint(usergroups,      url_prefix='/api/{}/usergroup'.format(API_VERSION))
app.register_blueprint(servers,         url_prefix='/api/{}/server'.format(API_VERSION))
app.register_blueprint(servergroups,    url_prefix='/api/{}/servergroup'.format(API_VERSION))
app.register_blueprint(ugsgs,           url_prefix='/api/{}/ugsg'.format(API_VERSION))
app.register_blueprint(auth,            url_prefix='/api/{}/auth'.format(API_VERSION))
app.register_blueprint(user_usergroups,      url_prefix='/api/{}/user_usergroups'.format(API_VERSION))
app.register_blueprint(server_servergroups,  url_prefix='/api/{}/server_servergroups'.format(API_VERSION))


@app.route("/api/{}/".format(API_VERSION))
def hello():
    app.logger.warning('api called A warning occurred (%d apples)', 42)
    session['key'] = 'value'
    return Response("<h1 style='color:blue'>Hello There!</h1>", mimetype='text/html')

@app.route("/api/{}/test/setsession".format(API_VERSION))
def test_setsession():
    session['key'] = 'value'
    return Response("<h1 style='color:blue'>Session should be set</h1>", mimetype='text/html')

@app.route("/api/{}/test/getsession".format(API_VERSION))
def test_getsession():
    return Response("Session 'key' is {}".format(session.get('key', 'not set')), mimetype='text/plain')

