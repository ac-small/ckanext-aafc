#!/bin/bash

# Script to run scheduled task scripts
# Update using appropriate server, port, mail sender and recipient

cd /home/rootadmin/docker/projects/ckanext-aafc/contrib/etl

python publish_to_og.py
python synch_with_og.py
python update_empty_records.py
python send_email.py
