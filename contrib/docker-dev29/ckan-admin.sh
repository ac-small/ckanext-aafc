#!/bin/bash

. /app/ckan/venv/bin/activate
cd /app/ckan/venv/src/ckan/
export CKAN_INI=/app/ckan/config/dev.ini
expect ./ckan-admin.exp
