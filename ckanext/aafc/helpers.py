import json
from pylons import c, config
from pylons.i18n import _
from ckan.model import User, Package, Activity
import ckan.model as model
#import wcms
import datetime
import unicodedata

import ckanapi

from ckantoolkit import h
from ckanext.scheming.helpers import scheming_get_preset
from ckan.logic.validators import boolean_validator
import uuid
import os

ORG_MAY_PUBLISH_OPTION = 'canada.publish_datasets_organization_name'
ORG_MAY_PUBLISH_DEFAULT_NAME = 'tb-ct'
PORTAL_URL_OPTION = 'canada.portal_url'
PORTAL_URL_DEFAULT = 'http://data.statcan.gc.ca'
DATAPREVIEW_MAX = 500
FGP_URL_OPTION = 'fgp.service_endpoint'
FGP_URL_DEFAULT = 'http://localhost/'

AAFC_EXT_VER = '2.0.0'
OPEN_GOV_URL = 'N/A'


def get_translated_t(data_dict, field):
    '''
    customized version of core get_translated helper that also looks
    for machine translated values (e.g. en-t-fr and fr-t-en)

    Returns translated_text, is_machine_translated (True/False)
    '''

    language = h.lang()
    try:
        return data_dict[field+'_translated'][language], False
    except KeyError:
        if field+'_translated' in data_dict:
            for l in data_dict[field+'_translated']:
                if l.startswith(language + '-t-'):
                    return data_dict[field+'_translated'][l], True
        val = data_dict.get(field, '')
        return (_(val) if val and isinstance(val, basestring) else val), False


def language_text_t(text, prefer_lang=None):
    '''
    customized version of scheming_language_text helper that also looks
    for machine translated values (e.g. en-t-fr and fr-t-en)

    Returns translated_text, is_machine_translated (True/False)
    '''
    if not text:
        return u'', False

    assert text != {}
    if hasattr(text, 'get'):
        try:
            if prefer_lang is None:
                prefer_lang = h.lang()
        except TypeError:
            pass  # lang() call will fail when no user language available
        else:
            try:
                return text[prefer_lang], False
            except KeyError:
                for l in text:
                    if l.startswith(prefer_lang + '-t-'):
                        return text[l], True
                pass

        default_locale = config.get('ckan.locale_default', 'en')
        try:
            return text[default_locale], False
        except KeyError:
            pass

        l, v = sorted(text.items())[0]
        return v, False

    t = gettext(text)
    if isinstance(t, str):
        return t.decode('utf-8'), False
    return t, False


def may_publish_datasets(userobj=None):
    if not userobj:
        userobj = c.userobj
    if userobj.sysadmin:
        return True

    pub_org = config.get(ORG_MAY_PUBLISH_OPTION, ORG_MAY_PUBLISH_DEFAULT_NAME)
    for g in userobj.get_groups():
        if not g.is_organization:
            continue
        if g.name == pub_org:
            return True
    return False

def openness_score(pkg):
    score = 1
    fmt_choices = scheming_get_preset('canada_resource_format')['choices']
    resource_formats = set(r['format'] for r in pkg['resources'])
    for f in fmt_choices:
        if 'openness_score' not in f:
            continue
        if f['value'] not in resource_formats:
            continue
        score = max(score, f['openness_score'])

    for r in pkg['resources']:
        if 'data_includes_uris' in r.get('data_quality', []):
            score = max(4, score)
            if 'data_includes_links' in r.get('data_quality', []):
                score = max(5, score)
    return score


def user_organizations(user):
    u = User.get(user['name'])
    return u.get_groups(group_type = "organization")

def catalogue_last_update_date():
    return '' # FIXME: cache this value or add an index to the DB for query below
    q = model.Session.query(Activity.timestamp).filter(
        Activity.activity_type.endswith('package')).order_by(
        Activity.timestamp.desc()).first()
    return q[0].replace(microsecond=0).isoformat() if q else ''

def today():
    return datetime.datetime.now(EST()).strftime("%Y-%m-%d")
    
# Return the Date format that the WET datepicker requires to function properly
def date_format(date_string):
    if not date_string:
        return None
    try:
        return datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S"
            ).strftime("%Y-%m-%d")
    except ValueError:
        return date_string

class EST(datetime.tzinfo):
    def utcoffset(self, dt):
      return datetime.timedelta(hours=-5)

    def dst(self, dt):
        return datetime.timedelta(0)
        
def remove_duplicates(a_list):
    s = set()
    for i in a_list:
        s.add(i)
            
    return s


def dataset_comments(pkg_id):
    if config.get('ckanext.canada.drupal_url'):
        return '/' + h.lang() + '/external-entity/ckan-' + pkg_id + '?_wrapper_format=ajax'

def dataset_comments_obd(pkg_id):
    if config.get('ckanext.canada.drupal_url'):
        return '/' + h.lang() + '/external-entity/ckan_obd-' + pkg_id + '?_wrapper_format=ajax'


def get_license(license_id):
    return Package.get_license_register().get(license_id)


def normalize_strip_accents(s):
    """
    utility function to help with sorting our French strings
    """
    if isinstance(s, str):
        return s
    if not s:
        s = u''
    s = unicodedata.normalize('NFD', s)
    return s.encode('ascii', 'ignore').decode('ascii').lower()


#def dataset_rating(package_id):
#    return wcms.dataset_rating(package_id)

#def dataset_rating_obd(package_id):
#    return wcms.dataset_rating_obd(package_id)


#def portal_url():
#    return str(config.get(PORTAL_URL_OPTION, PORTAL_URL_DEFAULT))

#def googleanalytics_id():
#    return str(config.get('googleanalytics.id'))
    
def loop11_key():
    return str(config.get('loop11.key', ''))

#def drupal_session_present(request):
#    for name in request.cookies.keys():
#        if name.startswith("SESS"):
#            return True
#    
#    return False
    
def parse_release_date_facet(facet_results):
    counts = facet_results['counts'][1::2]
    ranges = facet_results['counts'][0::2]
    facet_dict = dict()
    
    if len(counts) == 0:
        return dict()
    elif len(counts) == 1:
        if ranges[0] == facet_results['start']:
            facet_dict = {'published': {'count': counts[0], 'url_param': '[' + ranges[0] + ' TO ' + facet_results['end'] + ']'} }
        else:
            facet_dict = {'scheduled': {'count': counts[0], 'url_param': '[' + ranges[0] + ' TO ' + facet_results['end'] + ']'} }
    else:
        facet_dict = {'published': {'count': counts[0], 'url_param': '[' + ranges[0] + ' TO ' + ranges[1] + ']'} , 
                      'scheduled': {'count': counts[1], 'url_param': '[' + ranges[1] + ' TO ' + facet_results['end'] + ']'} }
    
    return facet_dict

def is_ready_to_publish(package):
    portal_release_date = package.get('portal_release_date')
    ready_to_publish = package['ready_to_publish']

    if ready_to_publish == 'true' and not portal_release_date:
        return True
    else:
        return False

#def get_datapreview_recombinant(resource_name, res_id):
#    from ckanext.recombinant.tables import get_chromo
#    chromo = get_chromo(resource_name)
#    default_preview_args = {}
#
#    lc = ckanapi.LocalCKAN(username=c.user)
#    results = lc.action.datastore_search(
#        resource_id=res_id,
#        limit=0,
#        )
#
#    priority = len(chromo['datastore_primary_key'])
#    pk_priority = 0
#    fields = []
#    for f in chromo['fields']:
#        out = {
#            'type': f['datastore_type'],
#            'id': f['datastore_id'],
#            'label': h.recombinant_language_text(f['label'])}
#        if out['id'] in chromo['datastore_primary_key']:
#            out['priority'] = pk_priority
#            pk_priority += 1
#        else:
#            out['priority'] = priority
#            priority += 1
#        fields.append(out)
#
#    return h.snippet('package/wet_datatable.html',
#        resource_name=resource_name,
#        resource_id=res_id,
#        ds_fields=fields)

def fgp_url():
    return str(config.get(FGP_URL_OPTION, FGP_URL_DEFAULT))

def contact_information(info):
    """
    produce label, value pairs from contact info
    """
    try:
        return json.loads(info)[h.lang()]
    except Exception:
        return {}

def show_subject_facet():
    '''
    Return True when the subject facet should be visible
    '''
    if any(f['active'] for f in h.get_facet_items_dict('subject')):
        return True
    return not show_fgp_facets()

def show_fgp_facets():
    '''
    Return True when the fgp facets and map cart should be visible
    '''
    for group in [
            'topic_category', 'spatial_representation_type', 'fgp_viewer']:
        if any(f['active'] for f in h.get_facet_items_dict(group)):
            return True
    for f in h.get_facet_items_dict('collection'):
        if f['name'] == 'fgp':
            return f['active']
    return False


def json_loads(value):
    return json.loads(value)

def gen_uid():
    new_id = uuid.uuid1()
    return new_id

def gen_odi():
    filename = "/tmp/count.dat"
    now = datetime.datetime.now()
    current_year = now.year
    count = 1
    odi = "ODI-%s-"%current_year
    
    #print(str(count))
    if not os.path.exists(filename):
        with open(filename, "w+") as f:
            f.write(str(count))
    
    with open(filename, "r+") as f:
        data = f.read()
        if data != None:
             count = data
        count_num = int(count)
        odi += "{:0>5d}".format(count_num)
        count_num += 1
        f.seek(0)
        f.write(str(count_num))
        f.truncate()
    


    return odi
    
def get_url():
    '''Return a reference for open government URL'''
    return OPEN_GOV_URL

def get_ver():
   '''Return a reference for version number'''
   return AAFC_EXT_VER

def get_release():
   '''Return a reference for registry release from config file'''
   return config.get('release.aafc.registry', '0.0')


def customized_sort(choices):
    '''
    use a fake language to escape native python sorting which doesn't 
    meet the requirement of ascent from client
    '''
    language = h.lang()
    len_choices = len(choices)
    if language == "en":
        return choices
    #list_new = choices
    #list_new.sort(key=lambda tup: tup[2])
    #print(list_other[:20])
    #choices = list_new
    choices.sort(key=lambda tup: tup[2])
    return choices

# FIXME: terrible hacks
def gravatar(*args, **kwargs):
    '''Brute force disable gravatar'''
    return ''
def linked_gravatar(*args, **kwargs):
    '''Brute force disable gravatar'''
    return ''

# FIXME: terrible, terrible hacks
def linked_user(user, maxlength=0, avatar=20):
    '''Brute force disable gravatar, mostly copied from ckan/lib/helpers'''
    from ckan import model
    if not isinstance(user, model.User):
        user_name = unicode(user)
        user = model.User.get(user_name)
        if not user:
            return user_name
    if user:
        name = user.name if model.User.VALID_NAME.match(user.name) else user.id
        displayname = user.display_name
        if displayname==config.get('ckan.site_id', '').strip():
            displayname = _('A system administrator')

        if maxlength and len(user.display_name) > maxlength:
            displayname = displayname[:maxlength] + '...'

        return h.literal(h.link_to(
                displayname,
                h.url_for(controller='user', action='read', id=name)
            )
        )
# FIXME: because ckan/lib/activity_streams is terrible
h.linked_user = linked_user
