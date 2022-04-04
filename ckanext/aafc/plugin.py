#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import os.path
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultDatasetForm
from ckan.logic import validators as logic_validators
from routes.mapper import SubMapper
import routes.mapper
from ckanext.aafc import validators
from ckanext.aafc import helpers
from time import gmtime, strftime
from ckanext.scheming import helpers as sh
import logging
import ckan.lib.base as base
import json
from ckan.lib.plugins import DefaultTranslation
from datetime import datetime

import ckan as ckan
import ckan.lib.helpers as h
import ckanext.aafc.blueprint as blueprint
import ckan.lib.formatters as formatters
import ckan.model as model
import dateutil.parser
import json as json
import geomet.wkt as wkt

from ckan.common import config, _, json, request, c


log = logging.getLogger(__name__)

class AafcPlugin(plugins.SingletonPlugin, DefaultDatasetForm , DefaultTranslation):
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IConfigurer) 
    plugins.implements(plugins.ITemplateHelpers)  
    plugins.implements(plugins.IValidators, inherit=True)
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.IPackageController)
    plugins.implements(plugins.ITranslation)
    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'aafc')

    def i18n_locales(self):
        return ['en','fr']

    def i18n_domain(self):
        return "ckanext-aafc" 
    # IValidators

    def get_validators(self):
        return {
            'canada_validate_generate_uuid':
                validators.canada_validate_generate_uuid,
            'canada_tags': validators.canada_tags,
            'geojson_validator': validators.geojson_validator,
            'email_validator': validators.email_validator,
            'canada_non_related_required':
                validators.canada_non_related_required,
            'if_empty_set_to':
                validators.if_empty_set_to,
         }
            
    #ITemplateHelpers
    def get_helpers(self):
        return dict((h, getattr(helpers, h)) for h in [
            'get_license',
            'get_translated_t',
            'language_text_t',
            'gen_uid',
            'gen_odi',
            'get_ver',
            'get_release',
            'customized_sort',
            'get_url'
            ])

# IFacets

    def dataset_facets(self, facets_dict, package_type):
        ''' Update the facets_dict and return it. '''
        lang = "en"
        try:
            lang =  get_lang()[0]
        except:
            log.info(">>>>get_lang() failed")
        
        # Publication Type Facet
        bl_publication_type = {"en":"Publication Type", "fr":"Type de publication"}
        facets_dict['publication'] = bl_publication_type.get(lang,"Publication Type")
        
        # Dataset Visibility Facet
        facets_dict['private'] = _("Visibility")
        return facets_dict

    def group_facets(self, facets_dict, group_type, package_type):
        ''' Update the facets_dict and return it. '''
        return facets_dict

    def organization_facets(self, facets_dict, organization_type,
                            package_type):
        return self.dataset_facets(facets_dict, package_type)

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
        if not search_params.get('defType', ''):
            search_params['defType'] = 'edismax' # use edismax if query type unspecified
        if search_params.get('fq', 'owner_org'):
            search_params.pop('defType')
        log.info(">>>>###search_params:")
        log.info(str(search_params))

        return search_params

    def after_search(self, search_results, search_params):      
        dt = sh.scheming_get_preset("publication_type")
        if dt is not None:
            options = sh.scheming_field_choices(dt)
        facets = search_results.get('search_facets')
        if not facets:
            return search_results
        for key, facet in facets.items():
            if key == 'publication':
                for item in facet['items']:
                    field_value = item['name']
                    label = sh.scheming_choices_label(options,field_value)
                    item['display_name'] = label
            if key == 'private':
                for item in facet['items']:
                    field_value = item['name']
                    if field_value == 'false':
                        item['display_name'] = _("Public")
                    elif field_value == 'true':
                        item['display_name'] = _("Private")
            if key == 'license_id':
                lang = "en"
                try:
                    lang =  get_lang()[0]
                except:
                    log.info(">>>>get_lang() failed")
                for item in facet['items']:
                    field_value = item['name']
                    lic_data = helpers.get_license(field_value)
                    title_fr = lic_data.title_fra
                    if lang == "fr":
                        item['display_name'] = title_fr 

                log.info(">>>>key license_id,language: %s"%lang)
        keys  = search_results.get('search_facets').keys()
        
        return search_results

    def after_show(self, context, data_dict):
        return data_dict


    def before_index(self, data_dict):

        data_dict['data_steward_email'] = data_dict.get('data_steward_email', '')
        data_dict['subject'] = json.loads(data_dict.get('subject', '[]'))

        titles = json.loads(data_dict.get('title_translated', '{}'))
        data_dict['title_string'] = titles.get('en', '').lower()

        output_file = "/tmp/b4index_" + strftime("%Y-%m-%d_%H_%M_%S", gmtime()) + ".json"
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


    def before_map(self, route_map):
        log.info(">>>>before_map called")
        return route_map

    def after_map(self, route_map):
        return route_map

    def get_blueprint(self):
        return blueprint.get_blueprints()

class WetTheme(plugins.SingletonPlugin):
    """
    Plugin for public-facing version of data.gc.ca site, aka the "portal"
    This plugin requires the DataGCCAForms plugin
    """
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config):

        # add our templates - note that the Web Experience Toolkit distribution
        # files should be installed in the public folder
        plugins.toolkit.add_template_directory(config, 'templates/wet_boew')
        plugins.toolkit.add_public_directory(config, 'public')

        # monkey patch helpers.py pagination method
        h.Page.pager = _wet_pager
        h.SI_number_span = _SI_number_span_close

    def get_helpers(self):
      return {'link_to_user': self.link_to_user,
              'gravatar_show': self.gravatar_show,
              'get_datapreview': self.get_datapreview,
              'iso_to_goctime': self.iso_to_goctime,
              'geojson_to_wkt': self.geojson_to_wkt,
              'url_for_wet': self.url_for_wet,
              'url_for_wet_theme': self.url_for_wet_theme,
              'wet_theme': self.wet_theme,
              'wet_jquery_offline': self.wet_jquery_offline,
              'get_map_type': self.get_map_type
            }


    def link_to_user(self, user, maxlength=0):
        """ Return the HTML snippet that returns a link to a user.  """

        # Do not link to pseudo accounts
        if user in [model.PSEUDO_USER__LOGGED_IN, model.PSEUDO_USER__VISITOR]:
            return user
        if not isinstance(user, model.User):
            user_name = unicode(user)
            user = model.User.get(user_name)
            if not user:
                return user_name

        if user:
            _name = user.name if model.User.VALID_NAME.match(user.name) else user.id
            displayname = user.display_name
            if maxlength and len(user.display_name) > maxlength:
                displayname = displayname[:maxlength] + '...'
            return html.tags.link_to(displayname,
                           h.url_for(controller='user', action='read', id=_name))

    def gravatar_show(self):
        return toolkit.asbool(config.get(GRAVATAR_SHOW_OPTION, GRAVATAR_SHOW_DEFAULT))

    def get_datapreview(self, res_id):

        #import pdb; pdb.set_trace()
        dsq_results = ckan.logic.get_action('datastore_search')({}, {'resource_id': res_id, 'limit' : 100})
        return h.snippet('package/wet_datatable.html', ds_fields=dsq_results['fields'], ds_records=dsq_results['records'])

    def iso_to_goctime(self, isodatestr):
        dateobj = dateutil.parser.parse(isodatestr)
        return dateobj.strftime('%Y-%m-%d')

    def geojson_to_wkt(self, gjson_str):
        ## Ths GeoJSON string should look something like:
        ##  u'{"type": "Polygon", "coordinates": [[[-54, 46], [-54, 47], [-52, 47], [-52, 46], [-54, 46]]]}']
        ## Convert this JSON into an object, and load it into a Shapely object. The Shapely library can
        ## then output the geometry in Well-Known-Text format

        try:
            gjson = json.loads(gjson_str)
            try:
                gjson = _add_extra_longitude_points(gjson)
            except:
                # this is bad, but all we're trying to do is improve
                # certain shapes and if that fails showing the original
                # is good enough
                pass
            shape = gjson
        except ValueError:
            return None # avoid 500 error on bad geojson in DB

        wkt_str = wkt.dumps(shape)
        return wkt_str

    def url_for_wet(self, *args, **kw):
        file = args[0] or ''
        theme = kw.get('theme', False)

        if not WET_URL:
            return h.url_for_static_or_external(
                (self.wet_theme() if theme else 'wet-boew') + file
            )

        return WET_URL + '/' + (self.wet_theme() if theme else 'wet-boew') + file



    def url_for_wet_theme(self, *args):
        file = args[0] or ''
        return self.url_for_wet(file, theme = True)

    def wet_theme(self):
        return 'theme-wet-boew'

    def wet_jquery_offline(self):
        return toolkit.asbool(config.get(WET_JQUERY_OFFLINE_OPTION, WET_JQUERY_OFFLINE_DEFAULT))

    def get_map_type(self):
        return str(config.get(GEO_MAP_TYPE_OPTION, GEO_MAP_TYPE_DEFAULT))

def _wet_pager(self, *args, **kwargs):
    ## a custom pagination method, because CKAN doesn't expose the pagination to the templates,
    ## and instead hardcodes the pagination html in helpers.py

    kwargs.update(
        format=u"<ul class='pagination'>$link_previous ~2~ $link_next</ul>",
        symbol_previous=gettext('Previous').decode('utf-8'), symbol_next=gettext('Next').decode('utf-8'),
        curpage_attr={'class': 'active'}
    )

    return super(h.Page, self).pager(*args, **kwargs)

def _SI_number_span_close(number):
    ''' outputs a span with the number in SI unit eg 14700 -> 14.7k '''
    number = int(number)
    if number < 1000:
        output = literal('<span>')
    else:
        output = literal('<span title="' + formatters.localised_number(number) + '">')
    return output + formatters.localised_SI_number(number) + literal('</span>')

def _add_extra_longitude_points(gjson):
    """
    Assume that sides of a polygon with the same latitude should
    be rendered as curves following that latitude instead of
    straight lines on the final map projection
    """
    import math
    fuzz = 0.00001
    if gjson[u'type'] != u'Polygon':
        return gjson
    coords = gjson[u'coordinates'][0]
    plng, plat = coords[0]
    out = [[plng, plat]]
    for lng, lat in coords[1:]:
        if plat - fuzz < lat < plat + fuzz:
            parts = int(abs(lng-plng))
            if parts > 300:
                # something wrong with the data, give up
                return gjson
            for i in range(parts)[1:]:
                out.append([(i*lng + (parts-i)*plng)/parts, lat])
        out.append([lng, lat])
        plng, plat = lng, lat
    return {u'coordinates': [out], u'type': u'Polygon'}

class GCIntranetTheme(WetTheme):

    plugins.implements(plugins.IConfigurer)

    def update_config(self, config):
        plugins.toolkit.add_template_directory(config, 'templates/theme_gc_intranet')
        return super(GCIntranetTheme, self).update_config(config)

    def wet_theme(self):
        return 'theme-gc-intranet'

# Monkey Patched to inlude the 'list-group-item' class
# TODO: Clean up and convert to proper HTML templates
def build_nav_main(*args):
    ''' build a set of menu items.

    args: tuples of (menu type, title) eg ('login', _('Login'))
    outputs <li><a href="...">title</a></li>
    '''
    output = ''
    for item in args:
        menu_item, title = item[:2]
        if len(item) == 3 and not h.check_access(item[2]):
            continue
        output += h._make_menu_item(menu_item, title, class_='list-group-item')
    return output
