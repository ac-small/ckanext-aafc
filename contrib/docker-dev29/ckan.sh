#!/bin/bash

PATH=/app/ckan/venv/bin:$PATH; export PATH
CMD=$1

if  [ "$CMD" = "stop" ] || [ "$CMD" = "restart" ] ; then
  apachectl stop
  kill `ps -ef|grep redis-server|grep -w 8082|awk '{print $2}'`
  . /app/ckan/venv/bin/activate; export CKAN_INI=/app/ckan/config/dev.ini && kill -9 $(ps -ef|grep "ckan run" | awk '{print $2}')
  su - ckan -c "/app/ckan/solr/bin/solr stop"
  kill `ps -ef|grep solr |awk '{print $2}'`
  su - postgres -c "pg_ctl -D /app/ckan/pgdata stop"
fi

if [ "$CMD" == "stop" ] ; then exit; fi

# Start
chown -R ckan:ckan /app/ckan/log /app/ckan/data
rm -rf /run/httpd/*
rm -f /app/ckan/pgdata/postmaster.pid /tmp/.*PGSQL*.lock
apachectl start
su - postgres -c "pg_ctl -D /app/ckan/pgdata start"
while : ; do if [ `ps -ef|grep -c postgres` -gt 3 ] ; then break ; fi ; sleep 1; done
su - ckan -c "redis-server --port 8082 &"
find /app/ckan -name solr-8983.pid -exec rm -f {} \; ; su - ckan -c "/app/ckan/solr/bin/solr start"

# Create admin user
ADMIN_SCRIPT=/app/ckan/admin/ckan-admin.sh
if [ -f "$ADMIN_SCRIPT" ] ; then 
  cd `dirname $ADMIN_SCRIPT`
  bash `basename $ADMIN_SCRIPT` 2>&1 > ckan-admin.log
  mv $ADMIN_SCRIPT ${ADMIN_SCRIPT}.done
  bash appInstall.sh
fi

su - ckan -c "cd /app/ckan/venv/src/ckan;. /app/ckan/venv/bin/activate; export CKAN_INI=/app/ckan/config/dev.ini && ckan run&" 
/etc/init.d/ssh start

if [ "$2" != "dev" ] ; then tail -f /dev/null; fi
