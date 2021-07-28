#!/bin/bash

/app/ckan/default/bin/paster --plugin=ckan search-index rebuild --config=/app/ckan/config/development.ini
