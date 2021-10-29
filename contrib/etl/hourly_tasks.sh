#!/bin/bash

# This script is to automate hourly processes:
#     Activate the virtual env
#     Update the tracking information
#     Rebuild search index
#     Send out email notifications
# This script is to be executed on an hourly basis via a crontab.
# Crontab is created on startup through docker-ckan start_ckan / start_ckan_dev scripts.
# Example: 0 * * * * /path/to/script/hourly_tasks.sh

CKAN_CONFIG=/srv/app/production.ini

echo "Running Tracking Update ... "
. /srv/app/bin/activate && /srv/app/bin/paster --plugin=ckan tracking update --config=$CKAN_CONFIG
echo "Rebuilding Search Index ... "
. /srv/app/bin/activate && /srv/app/bin/paster --plugin=ckan search-index rebuild -r --config=$CKAN_CONFIG
echo "Sending Emails ..."
. /srv/app/bin/activate && /srv/app/bin/paster --plugin=ckan post -c $CKAN_CONFIG /api/action/send_email_notifications
