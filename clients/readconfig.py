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

import os
import sys
import configparser
import base64

class Config:

    def __init__(self):

        configdir = '/etc/centralized'
        configfile = '{}/config.ini'.format(configdir)

        self.checkrights(configdir, '0700', '0o40700')
        self.check_ownership(configdir)

        self.checkrights(configfile, '0600', '0o100600')
        self.check_ownership(configfile)


        self.cfg = configparser.ConfigParser()
        self.cfg.read(configfile)


    def die(self, error):
        print(error, file=sys.stderr)
        sys.exit(1)

    def check_ownership(self, path):
        if os.stat(path).st_uid != 0 or os.stat(path).st_gid != 0:
            self.die("Improper ownership for {}, shall be root:root".format(path))

    def checkrights(self, path, advertised_desired_rights, rights):
        pathrights = oct(os.stat(path).st_mode)
        if pathrights != rights:
            self.die("Improper rights for {}, shall be {} ({}), current: {}".format(path, advertised_desired_rights, rights, pathrights))

    def load_ca(self):
        ca = base64.b64decode(self.cfg['main']['ca']).decode('utf-8')

        # Handle CA
        crt_path = '/etc/centralized/.centralized_ca.crt'
        if not os.path.isfile(crt_path):
            f = open( crt_path, 'w' )
            f.write( ca )
            f.close()

        os.environ['REQUESTS_CA_BUNDLE'] = crt_path



    def getconfig(self):
        return self.cfg

