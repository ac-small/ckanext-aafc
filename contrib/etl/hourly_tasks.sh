#!/bin/bash

# This script is to automate hourly processes:
#     Activate the virtual env
#     Update the tracking information
#     Rebuild search index
#     Send out email notifications
# This script is to be executed on an hourly basis via a crontab.
# Crontab is created on startup through docker-ckan start_ckan / start_ckan_dev scripts.
# Example: @hourly source hourly_tasks.sh

cd /srv/app/bin
source activate

echo "Running Tracking Update ... "
paster --plugin=ckan tracking update --config /srv/app/production.ini
echo "Tracking Update Successful!"
echo "Rebuilding Search Index ... "
paster --plugin=ckan search-index rebuild --config /srv/app/production.ini
echo "Search Index Successfully rebuilt!"
echo "Sending Emails ..."
paster --plugin=ckan post --config=/srv/app/production.ini /api/action/send_email_notifications
echo "Successfully Sent Emails!"

deactivate