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

# This script runs inside of the centos docker container.
# Please check build.sh for the entrypoint.

useradd builder -u $ORIG_UID -s /bin/bash -p '*'
chown $ORIG_UID:$ORIG_UID /mnt
ln -sd /mnt/rpmbuild /home/builder/rpmbuild
yum install -y rpm-build rpmdevtools
su - builder -c '(cd /mnt && rpmbuild -ba daemon.spec)'


