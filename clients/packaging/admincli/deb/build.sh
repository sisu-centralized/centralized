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

[ -d centralizedadmin ] && rm -rf centralizedadmin
rm *.deb

mkdir -p centralizedadmin/DEBIAN
mkdir -p centralizedadmin/usr/local/bin
install -m 0755 -o root -g root control  centralizedadmin/DEBIAN/
install -m 0755 -o root -g root debian/changelog  centralizedadmin/DEBIAN/
pushd ../../..
install -m 0755 centralized_admin.py           packaging/admincli/deb/centralizedadmin/usr/local/bin/
popd

dpkg-deb --root-owner-group --build centralizedadmin
mv centralizedadmin.deb $(awk '/^Package:/ { print $2 }' control)_$(dpkg-parsechangelog --show-field version)_$(dpkg-architecture -qDEB_BUILD_ARCH).deb

