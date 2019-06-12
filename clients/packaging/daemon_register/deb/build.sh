#!/usr/bin/env bash
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

set -x

[ -d centralizeddaemon ] && rm -rf centralizeddaemon
rm *.deb

set -e

mkdir -p centralizeddaemon/DEBIAN
mkdir -p centralizeddaemon/etc/centralized
mkdir -p centralizeddaemon/usr/local/bin
install -m 0755 control  centralizeddaemon/DEBIAN/
install -m 0755 debian/changelog  centralizeddaemon/DEBIAN/

#install -m 0755 -o root -g root postinst centralized/DEBIAN/
cp postinst centralizeddaemon/DEBIAN/
chmod +x centralizeddaemon/DEBIAN/postinst

cp postrm centralizeddaemon/DEBIAN/
chmod +x centralizeddaemon/DEBIAN/postrm

pushd ../../..
pwd
install -m 0755 readconfig.py                  packaging/daemon_register/deb/centralizeddaemon/usr/local/bin/
install -m 0755 centralized_daemon.py          packaging/daemon_register/deb/centralizeddaemon/usr/local/bin/
install -m 0755 centralized_register_server.py packaging/daemon_register/deb/centralizeddaemon/usr/local/bin/
popd

dpkg-deb --root-owner-group --build centralizeddaemon
#dpkg-deb --build centralized
mv centralizeddaemon.deb $(awk '/^Package:/ { print $2 }' control)_$(dpkg-parsechangelog --show-field version)_$(dpkg-architecture -qDEB_BUILD_ARCH).deb

