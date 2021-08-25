#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path
from pylons.i18n import _
from pylons.i18n.translation import get_lang
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultDatasetForm
from ckan.logic import validators as logic_validators
from routes.mapper import SubMapper
from paste.reloader import watch_file
import ckanapi
from ckan.lib.base import c
import routes.mapper
from ckanext.aafc import validators
from ckanext.aafc import helpers
from time import gmtime, strftime
from ckanext.scheming import helpers as sh
import logging
import ckanapi_exporter.exporter as exporter
import ckan.lib.base as base
import json
from ckan.lib.plugins import DefaultTranslation
from datetime import datetime

import ckan as ckan
import ckan.lib.helpers as h
import ckan.lib.formatters as formatters
import ckan.model as model
import webhelpers.html as html
import dateutil.parser
import json as json
import geomet.wkt as wkt

from webhelpers.html import HTML, literal
from webhelpers.html.tags import link_to
from pylons import config
from pylons import response
from pylons.i18n import gettext


log = logging.getLogger(__name__)

class AafcPlugin(plugins.SingletonPlugin, DefaultDatasetForm , DefaultTranslation):
    plugins.implements(plugins.IRoutes)
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
        log.info(">>>>i18n_locales():")
        return ['en','fr']

    def i18n_domain(self):
        log.info(">>>>i18n_domain:")
        log.info("name:{name}".format(name=self.name))
        dir = self.i18n_directory() 
        log.info("i18n dir:{idir}".format(idir=dir))
        return "ckanext-aafc" 
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
        lang = "en"
        try:
            lang =  get_lang()[0]
        except:
            log.info(">>>>get_lang() failed")
            pass
        # Sector Facet
        bl_sector = {"en":"Sector", "fr":"Secteur"}
        #TODO: should use il8n, fix it when it's ready
        #facets_dict['aafc_sector'] = plugins.toolkit._('Sector')
        facets_dict['aafc_sector'] = bl_sector.get(lang,"Sector")
        
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
        log.info(">>>>###search_params:")
        log.info(str(search_params))

	return search_params

    def convert_fq_param(self, str_fq):
        '''
        convert the received fq paramter string into the format that python need.
        i.e.
        1.first or only fq key value pair as fq
        2.All others will be put into a fq_list
        :param str_fq:
        :return: a list of 2 items: first is fq, the 2nd is the list of fq_list, could be empty
        '''
        str_fq = str_fq.replace('ESRI ', 'ESRI_')
        fq_l = str_fq.split(' ')
        len_fq = len(fq_l)
        #print(len_fq)
        #print(str(json.dumps(fq_l)))
        fq_l = [ fq.replace('ESRI_', 'ESRI ') for fq in fq_l ]


        if (len_fq > 0):
            fq0 = fq_l[0]
        fq_after = []
        if len_fq > 1:
            fq_after = fq_l[1:]

        return fq0,fq_after
    
    def process_q(self, qterm):
        '''
        process q term
        :param qterm:
        :return: a pair of values with keyword and new string
        '''

        if 'ESRI' in qterm:
           qterm = qterm.replace("ESRI ","ESRI_")
        res= re.compile(r'''\s*([\w]+:\s*[\w|"|/]+)\s*''').split(qterm)
        newq = ""
        other_filter = []
        keywords = []
        for i in res:
           if len(i) == 0:
             continue
           if ":" in i:
               #res = re.compile(r"\s*canada_keywords:\s*\"([^\"]+)\"").findall(i)
               #if len(res) != 0:
               #    #build keywords
               #    keywords.append(res[0]) #There will be only 1. just reuse old code of "findall"
               #else:
               #    other_filter.append(i)
               other_filter.append(i)
           else:
               newq = i
        new_qterm = newq
        return keywords,new_qterm, other_filter

    def after_search(self, search_results, search_params):
        pr = sh.scheming_get_preset("aafc_sector")
        choices = sh.scheming_field_choices(pr)
        
        dt = sh.scheming_get_preset("publication_type")
        options = sh.scheming_field_choices(dt)
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
            if key == 'aafc_sector':
            #log.info(">>>###key:" + key)
                for item in facet['items']:
                    field_value = item['name']				
                    label = sh.scheming_choices_label(choices,field_value)
                    item['display_name'] = label
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


    def before_map(self, route_map):
        with routes.mapper.SubMapper(route_map,
                controller='ckanext.aafc.plugin:ExportController') as m:
            m.connect('export', '/export',
                    action='export')
        return route_map

    def after_map(self, route_map):
        return route_map


class ExportController(base.BaseController):

    def export(self):
        '''
        Use ckanapi-exporter to export records into a csv file.
        Columns exported are specified in the /export/export.columns.json file.
        Exported files are labelled with current datetime.
        '''
        csv_content = exporter.export('http://localhost:5000', '../ckanext-aafc/ckanext/aafc/export/export_columns.json', str(c.userobj.apikey) , "{'include_private':'True'}")
        time = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = ("AAFC-Data-Catalogue-Export " + time + ".csv")
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers["Content-Disposition"] = "attachment; filename=" + filename
        return csv_content


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
