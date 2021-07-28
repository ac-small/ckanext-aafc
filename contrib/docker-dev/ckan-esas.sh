#!/bin/bash
# Usage: on | off | <partyID>

CMD=$1
PATH=/app/ckan/venv/bin:$PATH; export PATH
INI=/app/ckan/config/dev.ini
CONF=/etc/apache2/conf.d/ckan.conf

if [ "$CMD" = "on" ] ; then
	if [ `grep -c aafcesas $INI` -lt 1 ] ; then
		sed -E -i -e 's/envvars/ envvars aafcesas /g' $INI
	fi
elif [ "$CMD" = "off" ] ; then
	if [ `grep -c aafcesas $INI` -gt 0 ] ; then
		sed -E -i -e 's/aafcesas/ /g' $INI
	fi
else
	sed -i -e 's/.*partyId.*/RequestHeader append partyId '\"${CMD}\"'/g' $CONF
	sed -i -e 's/.*Legalgivennames.*/RequestHeader append Legalgivennames \"Test '${CMD}\"'/g' $CONF
	sed -i -e 's/.*email.*/RequestHeader append email \"partyid-'${CMD}'@canada.ca\"/g' $CONF
fi

# bash /app/ckan/admin/ckan.sh restart &
