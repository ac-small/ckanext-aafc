#!/bin/bash
# Usage: $0 [<tag-or-branch>]

LL_TAG=master
if [ "$1" != "" ] ; then
  LL_TAG=$1
fi
 
PATH=/app/ckan/venv/bin:$PATH; export PATH

. /app/ckan/venv/bin/activate
pip install -e "git+https://gitlab.com/aafc/ckanext-scheming.git#egg=ckanext-scheming" && \
pip install -e git+https://gitlab.com/aafc/lli-ckan.git@${LL_TAG}#egg=livinglabs && \
pip install -e git+https://gitlab.com/aafc/ckanext-aafcesas.git#egg=ckanext-aafcesas && \
date

#/app/ckan/admin/ckan.sh restart
kill `ps -ef|grep paster |grep dev.ini|awk '{print $2}'`
su - ckan -c "cd /app/ckan/venv/src/ckan;. /app/ckan/venv/bin/activate; paster serve /app/ckan/config/dev.ini &"

