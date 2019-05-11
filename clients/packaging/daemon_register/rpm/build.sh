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


mkdir -p rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS,tmp}
pushd rpmbuild/SOURCES
mkdir centralizeddaemon-0
cp ../../../../../readconfig.py centralizeddaemon-0/
cp ../../../../../centralized_daemon.py centralizeddaemon-0/
cp ../../../../../centralized_register_server.py centralizeddaemon-0/

tar -cvf centralizeddaemon-0.2.tar.gz centralizeddaemon-0
popd
docker run -it --rm -v $PWD:/mnt -e ORIG_UID=$UID centos bash /mnt/dobuild.sh



