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

FROM ubuntu:16.04

RUN apt-get update && apt-get install -y python3 python3-psycopg2 python3-pip \
    uwsgi-plugin-python3 python3-flask postgresql-client \
    libkrb5-dev libldap2-dev libsasl2-dev libssl-dev libffi-dev cron


# Migrations specifics
RUN pip3 install "Click==6.7"
RUN pip3 install mschematool
ADD migrations/ /opt/migrations/
ADD dockerfiles/api/config /opt/

# API Specifics
#RUN apt-get install -y uwsgi-plugin-python3 python3-flask postgresql-client
RUN pip3 install flask-sessionstore
ADD api/ /opt/centralized/api/
ADD dockerfiles/api/centralized.ini /opt/centralized/api/
RUN chmod -R 777 /opt/*

# Connectors.
#RUN apt-get install -y libkrb5-dev libldap2-dev libsasl2-dev libssl-dev libffi-dev cron
RUN pip3 install PyGithub sshpubkeys cookiejar
ADD connectors /opt/connectors/

EXPOSE 3333/tcp

WORKDIR /opt/centralized/api
ADD dockerfiles/api/init_api.sh /opt/
ADD dockerfiles/api/init_connector.sh /opt/
RUN chmod a+x /opt/init_*

ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /opt/
RUN chmod a+x /opt/wait-for-it.sh
ENTRYPOINT /opt/init_api.sh



