#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path
from pylons.i18n import _
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultDatasetForm
from ckan.logic import validators as logic_validators
from routes.mapper import SubMapper
from paste.reloader import watch_file
#from ckantoolkit import h, chained_action, side_effect_free
import ckanapi
from ckan.lib.base import c

from ckanext.aafc import validators
#from ckanext.aafc import logic
#from ckanext.aafc import auth
from ckanext.aafc import helpers
#from ckanext.aafc import activity as act
#from ckanext.aafc.extendedactivity.plugins import IActivity

import json

class AafcPlugin(plugins.SingletonPlugin, DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    p.implements(p.IValidators, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'aafc')

    # IValidators

    def get_validators(self):
        return {
            'canada_validate_generate_uuid':
                validators.canada_validate_generate_uuid,
            'canada_tags': validators.canada_tags,
#            'geojson_validator': validators.geojson_validator,
            'email_validator': validators.email_validator,
#            'protect_portal_release_date':
#                validators.protect_portal_release_date,
#            'canada_copy_from_org_name':
#                validators.canada_copy_from_org_name,
            'canada_non_related_required':
                validators.canada_non_related_required,
            'if_empty_set_to':
                validators.if_empty_set_to,
            }
