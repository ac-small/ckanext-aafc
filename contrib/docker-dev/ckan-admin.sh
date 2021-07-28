#!/bin/bash

. /app/ckan/venv/bin/activate
cd /app/ckan/venv/src/ckan/
expect ./ckan-admin.exp
