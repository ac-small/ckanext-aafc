#!/bin/bash

PATH=/app/ckan/venv/bin:$PATH; export PATH
CMD=$1

if  [ "$CMD" = "stop" ] || [ "$CMD" = "restart" ] ; then
  /usr/sbin/httpd -k stop
  kill `ps -ef|grep redis-server|grep -w 8082|awk '{print $2}'`
  kill `ps -ef|grep paster |grep dev.ini|awk '{print $2}'`
  su - ckan -c "/app/ckan/solr/bin/solr stop"
  kill `ps -ef|grep solr |awk '{print $2}'`
  su - postgres -c "pg_ctl -D /app/ckan/pgdata stop"
fi

if [ "$CMD" == "stop" ] ; then exit; fi

# Create admin user
ADMIN_SCRIPT=/app/ckan/admin/ckan-admin.sh

# Start
chown -R ckan:ckan /app/ckan/log /app/ckan/venv
rm -rf /run/httpd/*
rm -f /app/ckan/pgdata/postmaster.pid /tmp/.*PGSQL*.lock
/usr/sbin/httpd
su - postgres -c "pg_ctl -D /app/ckan/pgdata start"
while : ; do if [ `ps -ef|grep -c postgres` -gt 3 ] ; then break ; fi ; sleep 1; done
su - ckan -c "/app/ckan/redis/bin/redis-server --port 8082 &"
su - ckan -c "/app/ckan/solr/bin/solr start"
su - ckan -c "cd /app/ckan/venv/src/ckan;. /app/ckan/venv/bin/activate; paster serve /app/ckan/config/dev.ini &"


sleep 30

if [ -f "$ADMIN_SCRIPT" ] ; then
  cd `dirname $ADMIN_SCRIPT`
  bash `basename $ADMIN_SCRIPT`
  mv $ADMIN_SCRIPT $ADMIN_SCRIPT-done
fi
#rm -f /app/ckan/venv/src/ckan/ckan-admin.exp

if [ "$2" != "dev" ] ; then tail -f /dev/null; fi
