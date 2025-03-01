import json
import os
import urllib
import urllib.request as urllib2
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
    try:
        with open(file) as json_fp:
            data = json.load(json_fp)
    except IOError:
        data = None
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
	
def get_all_public_ids(remote=True):
    '''
    Get all ids from site
    :param remote:
    :return:
    '''
    if remote:
        site = os.getenv("source_url")
        api_key = os.getenv("source_api_key")
    else: #local
        site = os.getenv("destination_url")
        api_key = os.getenv("destination_api_key")
    session = requests.Session()
    session.verify = False
    rckan = RemoteCKAN(site, apikey=api_key,session=session)
    try:
        ret = rckan.call_action("package_list")
        #for id in ret:
        #    print(id)
    except Exception as e:
        print("Error message : %s" % e.message)
        ret = []
    return ret


def get_all_private_ids(remote=True):
    '''
    Get all private record IDs from site
    :param remote:
    :return:
    '''
    if remote:
        site = os.getenv("source_url")
        api_key = os.getenv("source_api_key")
    else: #local
        site = os.getenv("destination_url")
        api_key = os.getenv("destination_api_key")
    session = requests.Session()
    session.verify = False
    rckan = RemoteCKAN(site, apikey=api_key,session=session)
    try:
        ret = rckan.action.package_search(q='+private:true', include_private='true', rows=1000)
        records = ret["results"]
        id_list = []
        for item in records:
            id_list.append(item["id"])
        print(id_list)
    except Exception as e:
        print("Error message : %s" % e.message)
        id_list = []
    return id_list


def get_data_from_reg(package_id):
    """
    Called by get_n_post
    Get data from registry
    :param package_id:
    :return:
    """
    site = os.getenv("registry_url")
    api_key= os.getenv("registry_api_key")
    rckan = RemoteCKAN(site, apikey=api_key)

    data_as_d = {"id": package_id}
    try:
        ret = rckan.call_action("package_show", data_dict=data_as_d)  # data_as_dict )
    except Exception as e:
        print("failed")

    return ret

def is_harvested(package_id):
    data = get_data_from_reg(package_id)
    if data.get("aafc_is_harvested"):
        return True
    return False

