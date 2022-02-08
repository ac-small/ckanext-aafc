#!/bin/env bash
INI_FILE=/app/ckan/config/dev.ini

. /app/ckan/venv/bin/activate; cd /app/ckan/venv/src/

# git clone -b python3 https://github.com/asc-csa/ckanext-asc-csa-scheming && git clone https://github.com/ckan/ckanext-fluent.git && git clone https://github.com/asc-csa/ckanext-asc-csa
git clone -b v2_9-compat https://github.com/aafc-ckan/ckanext-aafc && pushd ckanext-aafc && python setup.py develop && popd
git clone -b v2_9 https://gitlab.com/aafc/ckanext-scheming.git && pushd ckanext-scheming && python setup.py develop && popd

sed -i '/ckan.plugins/ s/$/ aafc/' $INI_FILE
sed -i '/ckan.plugins/ s/$/ scheming_datasets/' $INI_FILE

chown -R ckan:ckan /app/ckan/venv/src
#pushd /app/ckan/admin/; kill -9 $(ps -ef|grep "ckan run" | awk '{print $2}');
#su - ckan -c "cd /app/ckan/venv/src/ckan;. /app/ckan/venv/bin/activate; export CKAN_INI=/app/ckan/config/dev.ini && ckan run&"
#popd
