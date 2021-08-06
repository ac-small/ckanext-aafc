#/bin/bash

# Sends email notifications when a user has a change to their dashboard.
# See https://docs.ckan.org/en/2.8/maintaining/email-notifications.html
# This script should be executed from a crontab on an hourly basis.

set -o allexport
source $PWD/docker/projects/ckanext-aafc/contrib/etl/.env
set +o allexport

curl -s -H "Authorization: $registry_api_key" -d {} http://localhost:5000/api/action/send_email_notifications
