#!/usr/bin/env python
import json
from dotenv import load_dotenv
from helper import *
import os
from datetime import datetime, timedelta
import urllib
from random import randint
from ckanapi import RemoteCKAN
'''
There are many data sets go to Open Government that are not through
'''


def process_a_batch(data_list):
    length = len(data_list)
    ids = []
    for i in range(length):
        a_id = data_list[i]["id"]
        ids.append(a_id)
        # print("id:" + a_id)
    return ids


def query_by_aafc(site):
    """
    Query OG site to retrieve all the ids of AAFC
    :return:
    """
    rows = 100
    apicall = "api/3/action/package_search"
    q_param0 = "?q=organization:aafc-aac&rows=%d" % rows

    # useful queries:
    # ?q=metadata_modified:[2019-10-10T21:15:00Z TO *]
    #
    res = query_with_get(site, apicall, q_param0)

    if res is None:
        return None

    response_dict = json.loads(res)
    data = response_dict['result']
    record_cnt = data['count']
    results = data['results']
    id_list = process_a_batch(results)
    batches = record_cnt / rows + 1

    for b in range(1, batches):
        offset = b * rows
        q_param = "?q=organization:aafc-aac&rows=%d&start=%d" % (rows, offset)
        res = query_with_get(site, apicall, q_param)
        response_dict = json.loads(res)
        results = response_dict['result']['results']
        id_list_curr = process_a_batch(results)
        id_list.extend(id_list_curr)

    return id_list


def query_site_for_newdata(site, sec_param="", hours_ago=None):
    '''
    Query  site to get list of new ids in last X hours
    :param sec_param: restrict to some condition. examples: "&fq=publication:open_government", "&fq=organization:aafc-aac"
    :param site:
    :return:
    '''
    apicall = "api/3/action/package_search"
    q_param = "?q=metadata_modified:[2019-10-10T21:15:00Z TO *]&fq=publication:open_government"

    if hours_ago is None:
        hours_ago = 48
    two_days_ago = datetime.now() - timedelta(hours=hours_ago)
    str_2days_ago =  two_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ')
    q_param1 = "?q=metadata_modified:[%s%sTO%s*]"%(str_2days_ago, '%20','%20') + sec_param
    res = query_with_get(site, apicall, q_param1)

    if res is None:
        return None
    response_dict = json.loads(res)
    results = response_dict['result']['results']
    id_list = process_a_batch(results)
    return id_list


def main1():
    og_site = "https://open.canada.ca/data/"
    id_list = query_by_aafc(og_site)
    with open("aafc_id_list2.txt", "w") as fout:
        str = u','.join(id_list)
        fout.write(str)

def test_og():
    og_site = "https://open.canada.ca/data/"
    id_list = query_site_for_newdata(og_site, "&fq=organization:aafc-aac", hours_ago=1240)
    for id in id_list:
        print("id:%s"%id)

def test_registry():
    registry_url = os.getenv("registry_url")
    id_list = query_site_for_newdata(registry_url, "&fq=publication:open_government", hours_ago=1240)
    for id in id_list:
        print("id:%s"%id)


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


def post_to_regsistry(package_id):


    data_as_d = {}
    with open("Data//fromAlexis.json") as json_fp:
        data_as_d = json.load(json_fp)



    #Post to registry
    site = os.getenv("registry_url")
    registry_key = os.getenv("registry_api_key")
    rckan = RemoteCKAN(site, apikey=registry_key)

    try:
        ret = rckan.call_action("package_create", data_dict=data_as_d)#data_as_dict )

    except Exception as e:
        return False

    return True #False

def main():
    #Get the lastest list from registry
    registry_url = os.getenv("registry_url")
    registry_ids = query_site_for_newdata(registry_url, "&fq=publication:open_government", hours_ago=48)
    # Get the lastest list from OG
    og_site = "https://open.canada.ca/data/"
    og_ids = query_site_for_newdata(og_site, "&fq=organization:aafc-aac", hours_ago=48)

    # Go through both lists, retrieve missing data from OG and post into Registry and record event of failure
    for id in og_ids:
        if id in registry_ids:
            continue
        res = post_to_regsistry(id)
        if res is False:

            with open("error_post.log", "a") as fout:
                now = datetime.now()
                event = "Failed updating package id %s on %s\n"%(id, now)
                fout.write(event)


def test_post():
    package_id = "e328838f-3bfc-4d86-9cc5-23de0b549c91"
    apicall = "api/3/action/package_show"
    q_param="?id=" +package_id
    site = os.getenv("registry_url")
    registry_key = os.getenv("registry_api_key")
    ret_as_string = query_with_get(site, apicall, q_param, apikey=registry_key)
    res_as_dict = json.loads(ret_as_string)['result']
    data_as_dict = res_as_dict
    data_as_dict['title'] = res_as_dict['title']  + str(randint(0,99))
    del data_as_dict['id']
    del data_as_dict['revision_id']
    if "aafc_subject" in data_as_dict:
        del data_as_dict['aafc_subject']

    data_as_d = {}
    with open("Data//fromAlexis.json") as json_fp:
        data_as_d = json.load(json_fp)


    # do a post
    registry_key = os.getenv("registry_api_key")
    rckan = RemoteCKAN(site, apikey=registry_key)

    try:
        ret = rckan.call_action("package_create", data_dict=data_as_d)#data_as_dict )

    except Exception as e:
        pass
    #post_to_site(site, "api/3/action/package_create",data_as_dict,registry_key)

    pass

if __name__ == "__main__":
    load_dotenv()
    test_post()
    #main()
