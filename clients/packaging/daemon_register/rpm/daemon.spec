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
Name:   centralizeddaemon
Version:    0 
Release:    2
Summary:    centralized.pw daemon

Group:      Applications/System
BuildArch:  noarch
License:    GPLv3
Source0:    %{name}-%{version}.%{release}.tar.gz
Url:        http://www.centralized.pw

%description
Centralized is a way for devops teams to use their repository credentials to allow server access.
More at http://www.centralized.pw and https://github.com/sisu-centralized


%prep
echo $RPM_BUILD_ROOT

%setup -q


%build
%install
install --directory $RPM_BUILD_ROOT/etc/centralized
install --directory $RPM_BUILD_ROOT/usr/local/bin
install -m 0755 readconfig.py                  $RPM_BUILD_ROOT/usr/local/bin/
install -m 0755 centralized_daemon.py          $RPM_BUILD_ROOT/usr/local/bin/
install -m 0755 centralized_register_server.py $RPM_BUILD_ROOT/usr/local/bin/

%post
mkdir -p /etc/centralized
chmod 0700 /etc/centralized
grep centralized_daemon /etc/crontab >/dev/null || echo '*/10 *  * * *   root    /usr/bin/env python3 /usr/local/bin/centralized_daemon.py' >> /etc/crontab

%postun
sed 's/.*centralized_daemon.*//' -i /etc/crontab

%clean
rm -rf $RPM_BUILD_ROOT


%files
/usr/local/bin/readconfig.py
/usr/local/bin/centralized_daemon.py
/usr/local/bin/centralized_register_server.py


%changelog
* Sat May 7 2019 Pierre Ancelot  0.2
  - Initial rpm release

