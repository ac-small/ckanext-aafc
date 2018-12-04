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

from ckanext.aafc import tbs_validators
#from ckanext.aafc import logic
#from ckanext.aafc import auth
from ckanext.aafc import tbs_helpers
#from ckanext.aafc import activity as act
#from ckanext.aafc.extendedactivity.plugins import IActivity

import json

class AafcPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'aafc')
