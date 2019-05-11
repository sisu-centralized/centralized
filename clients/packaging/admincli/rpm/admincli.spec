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
Name:   centralizedadmin
Version:    0 
Release:    1
Summary:    centralized.pw admin tool

Group:      Applications/System
BuildArch:  noarch
License:    GPLv3
Source0:    %{name}-%{version}.%{release}.tar.gz
#https://github.com/sisu-centralized
Url:        http://www.centralized.pw
#BuildRoot:  %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)


%description
Centralized is a way for devops teams to use their repository credentials to allow server access.
More at http://www.centralized.pw and https://github.com/sisu-centralized


%prep
echo $RPM_BUILD_ROOT

%setup -q


%build
%install
install --directory $RPM_BUILD_ROOT/usr/local/bin
install -m 0755 centralized_admin.py $RPM_BUILD_ROOT/usr/local/bin/

%clean
rm -rf $RPM_BUILD_ROOT


%files
/usr/local/bin/centralized_admin.py


%changelog
* Sat May 4 2019 Pierre Ancelot  0.1
  - Initial rpm release

