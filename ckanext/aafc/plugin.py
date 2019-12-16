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
from time import gmtime, strftime
from ckanext.scheming import helpers as sh
import logging
from flask import render_template
from flask import Blueprint
import json

log = logging.getLogger(__name__)

def helper_info():
    """
    A function that render a page when the route to '/info'
    """
    return render_template('home/about.html')    


class AafcPlugin(plugins.SingletonPlugin, DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer) 
    plugins.implements(plugins.ITemplateHelpers)  
    plugins.implements(plugins.IValidators, inherit=True)
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.IPackageController)
    plugins.implements(plugins.IBlueprint)
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
            'geojson_validator': validators.geojson_validator,
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
            
    #ITemplateHelpers
    def get_helpers(self):
        return dict((h, getattr(helpers, h)) for h in [
#            'user_organizations',
#            'openness_score',
#            'remove_duplicates',
#            'get_license',
#            'normalize_strip_accents',
#            'portal_url',
#            'googleanalytics_id',
#            'loop11_key',
#            'drupal_session_present',
#            'fgp_url',
#            'contact_information',
#            'show_subject_facet',
#            'show_fgp_facets',
#            'show_openinfo_facets',
#            'gravatar',
#            'linked_gravatar',
#            'linked_user',
#            'json_loads',
#            'catalogue_last_update_date',
#            'dataset_rating',
#            'dataset_comments',
            'get_translated_t',
            'language_text_t',
            'gen_uid',
            'gen_odi',
            'get_ver',
            'get_release',
            'get_url'
            ])

# IFacets

    def dataset_facets(self, facets_dict, package_type):
        ''' Update the facets_dict and return it. '''

        #facets_dict.update({
        #    'organization': _('Organization'),
        #    'res_format': _('Format'),
        #    'aafc_sector': _('Sector'),
        #    'res_type': _('Resource Type'),
        #    })
        facets_dict['aafc_sector'] = plugins.toolkit._('Sector')
        return facets_dict

    def group_facets(self, facets_dict, group_type, package_type):
        ''' Update the facets_dict and return it. '''
        return facets_dict

    def organization_facets(self, facets_dict, organization_type,
                            package_type):
        return self.dataset_facets(facets_dict, package_type)
# IBluprint
    def get_blueprint(self):
        # Create Blueprint for plugin
        blueprint = Blueprint(self.name, self.__module__)
        # Add plugin url rules to Blueprint object
        rules = [
            (u'/info', u'info', helper_info),
        ]
        for rule in rules:
            blueprint.add_url_rule(*rule)

        return blueprint

# IPackageController
    def read(self, entity):
        pass

    def create(self, entity):
        pass

    def edit(self, entity):
        pass

    def authz_add_role(self, object_role):
        pass

    def authz_remove_role(self, object_role):
        pass

    def delete(self, entity):
        pass

    def before_search(self, search_params):
	return search_params

    def after_search(self, search_results, search_params):
        pr = sh.scheming_get_preset("aafc_sector")
        choices = sh.scheming_field_choices(pr)
        #for result in search_results.get('results', []):
            #for extra in result.get('extras', []):
            #    if extra.get('key') in ['sector' ]:
            #        result[extra['key']] = "xxx" #extra['value']
        facets = search_results.get('search_facets')
        if not facets:
            return search_results
        for key, facet in facets.items():
            if key == 'tags':
               #log.info(">>>pop :" + key)
               #facets.pop('tags')
               #c.facet_titles.pop(key)
               continue
            if key != 'aafc_sector':
                continue
            #log.info(">>>###key:" + key)
            for item in facet['items']:
                field_value = item['name']				
                label = sh.scheming_choices_label(choices,field_value)
                item['display_name'] = label
        keys  = search_results.get('search_facets').keys()
        #log.info(">>>kesy before return  :" + str(keys))
        try:
            c.facet_titles.pop('tags')
        except (AttributeError, RuntimeError):
            pass
        
	return search_results

    def after_show(self, context, data_dict):
        return data_dict


    def before_index(self, data_dict):
        output_file = "/tmp/b4index_" + strftime("%Y-%m-%d_%H_%M_%S", gmtime()) + ".json"
        #with open(output_file,"w") as fout:
        #   output_str = json.dumps(data_dict)
        #   fout.write(output_str)
        return data_dict


    def before_view(self, pkg_dict):
        return pkg_dict

    def after_delete(self, context, data_dict):
        return data_dict

    def after_show(self, context, data_dict):
        return data_dict

    def update_facet_titles(self, facet_titles):
        return facet_titles

    def after_update(self, context, data_dict):
	return data_dict


    def after_create(self, context, data_dict):
        return data_dict
