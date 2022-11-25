#!/bin/bash

# This script is to automate hourly processes:
#     Activate the virtual env
#     Update the tracking information
#     Rebuild search index
#     Send out email notifications
# This script is to be executed on an hourly basis via a crontab.
# Crontab is created on startup through docker-ckan start_ckan / start_ckan_dev scripts.
# Example: 0 * * * * /path/to/script/hourly_tasks.sh

CKAN_CONFIG=/srv/app/ckan.ini

echo "Running Tracking Update ... "
. /srv/app/bin/activate && ckan -c $CKAN_CONFIG tracking update
echo "Rebuilding Search Index ... "
. /srv/app/bin/activate && ckan -c $CKAN_CONFIG search-index rebuild -r
echo "Sending Emails ..."
curl -H "Authorization: $API_KEY" -X POST http://localhost:5000/api/action/send_email_notifications