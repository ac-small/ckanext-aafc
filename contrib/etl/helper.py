import json
import os
import urllib
import urllib2
from datetime import datetime, timedelta
import yaml
from ckanapi import RemoteCKAN
import requests




def query_with_get( site, apicall, q_param, apikey = None):
    """
    Query remote site with get
    :param site:
    :param apicall:
    :param q_param:
    :param apikey:
    :return:
    """

    url1 = site + apicall
    req = urllib2.Request(url1 + q_param)
    if apikey != None:
        req.add_header('Authorization', apikey)
    # response = urllib.request.urlopen(req)
    # For Python 2.7
    response = None
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        # print("might not have the package in OG site yet")
        return None
    except:
        print("Error happening querying OG site")
        return None
    res = response.read()

    return res

def purge_dataset(package_ids, source = False):
    '''

    :param package_ids: list of package id
    :return:
    '''
    site = os.getenv("destination_url")
    api_key = os.getenv("destination_api_key")

    if source:
        site = os.getenv("source_url")
        api_key = os.getenv("source_api_key")
    session = requests.Session()
    session.verify = False

    rckan = RemoteCKAN(site, apikey=api_key,session=session)

    count = 0
    try:
        for package_id in package_ids:
            data_as_d = {"id": package_id}
            ret = rckan.call_action("dataset_purge", data_dict=data_as_d)
            print("count:%d"%count+ json.dumps(ret))
            count += 1
    except Exception as e:
        # if no data exists yet, return empty
        ret = []
    return ret


def load_json( file ):
    data =  None
    with open(file) as json_fp:
        data = json.load(json_fp)
    return data

        
    
# TODO: moved to here for now before delete it.
def post_to_site(site, action_string, data_as_dict, apikey):
    """

    :param site:
    :param action_string: like "api/3/action/package_update" , or "api/3/action/package_create"
    :param data_as_dict:
    :return:
    """


    data_string = urllib.quote(json.dumps(data_as_dict))
    url = site + action_string #"api/3/action/package_update"
    request = urllib2.Request(url)

    request.add_header('Authorization', apikey)


    response = None
    try:
        response = urllib2.urlopen(request, data_string)
    except urllib2.HTTPError as e:
        # print("might not have the package in OG site yet")
        return False
    except:
        print("Error happening querying OG site")
        return False

    pass
def get_all_data( isSink = False, timelimit = False, restrict=False):
    '''
    retrieve all data from the remote site
    :return:
    '''
    #Get the lastest list from registry
    data_url = os.getenv("source_url")
    data_api_key = os.getenv("source_api_key")
    if isSink:
        data_url = os.getenv("destination_url")
        data_api_key = os.getenv("destination_api_key")
    rows = os.getenv("rows_to_get")

    if data_url == None or len(data_url) == 0 or data_url.find("http") == -1:
        print("Missing  url")
        return
    if data_api_key == None or len(data_api_key) == 0:
        print("Missing  api key")
    #    return


    print("Geting data from remote:%s with api key %s"%(data_url,data_api_key))
    session = requests.Session()
    session.verify = False
    rckan = RemoteCKAN(data_url, apikey=data_api_key,session=session)
    param = {"rows":rows}
    if timelimit:
        param["q"] = calculate_time_param()

    result = rckan.call_action("package_search",param)
    print("Retrieved data from remote site")
    if restrict:
        new_result={}
        new_result["count"] = result["count"]
        new_result["results"] = []
        for i in result['results']:
            kwes=[]
            kws = i["keywords"]["en"]
            remove = True
            for kw in kws:
                kwes.append(kw)
                if kw.find("Living Lab") >=0:
                    remove = False
            str_kw = ",".join(kwes)
            #print(">>>List of kw in e:%s"%str_kw)
            if not remove:
            #    result['results'].remove(i)
            #else:
                new_result['results'].append(i)
        result = new_result
    return result
