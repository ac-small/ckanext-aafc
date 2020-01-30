#!/usr/bin/env python
import json
from dotenv import load_dotenv
from helper import *
import os
import re
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

def create_to_registry(package_id):
        with open("Data//fieldsAdded.json") as json_fp:
            add_fields = json.load(json_fp)
        og_data = get_data_from_url(package_id, "open_gov_url")
        for k,v in add_fields.items():
            og_data[k] = add_fields[k]
        #Post to registry
        replace_branch_and_data_steward(og_data)
        reg_site = os.getenv("registry_url")
        registry_key = os.getenv("registry_api_key")
        rckan = RemoteCKAN(reg_site, apikey=registry_key)
        try:
            ret = rckan.call_action("package_create", data_dict=og_data)
        except Exception as e:
            return False
        return True

def update_to_registry(package_id):
        og_data = get_data_from_url(package_id, "open_gov_url")
        # query for registry data and remove shared fields (aafc registry exclusive fields will be kept i.e. ODI reference number, DRF core responsibilties)
        reg_data = get_data_from_url(package_id, "registry_url")
        keys_to_remove = ['resources', 'organization', 'data_steward_email', 'notes_translated', 'title_translated', 'notes', 'owner_org', 'num_resources', 'title', 'keywords', 'revision_id', 'audience']
        if reg_data != []:
            for k in keys_to_remove:
                reg_data.pop(k, None)
            for k,v in reg_data.items():
                og_data[k] = reg_data[k]
        replace_branch_and_data_steward(og_data)
        reg_site = os.getenv("registry_url")
        registry_key = os.getenv("registry_api_key")
        rckan = RemoteCKAN(reg_site, apikey=registry_key)
        #print(og_data)
        try:
            ret = rckan.call_action("package_update", data_dict=og_data)
        except Exception as e:
            return False
        return True

def extract_branch_and_data_steward(og_data):
    if 'metadata_contact' in og_data and og_data['metadata_contact'] != {}:
        #print og_data['metadata_contact']['en']
        contact = og_data['metadata_contact']['en']
        # Extract contact information fields
        pattern = re.compile(r";|,")
        contact_str = pattern.split(contact)
    else:
        contact_str = ["Government of Canada", "Agriculture and Agrifood Canada", "Unknown Branch", "Unknown"]
    return contact_str

def switch_branch(con_str):
    #To Do: check branch names for typos / apostrophes
    branches = {
        "Science and Technology Branch":"ae56a90e-502b-43f9-b256-35a8f3a71bd3",
        "Corporate Management Branch":"186eb448-b6b5-4f16-b615-dba53e26a1ad",
        "Deputy Minister's Office":"acf141cc-2239-4884-8a2b-c7cdae8ea486",
        "International Affairs Branch":"2da3aae3-5901-4bbf-8d08-080d0665bad9",
        "Information Systems Branch":"4b90a457-bbe8-4e2b-938e-0358307d2af8",
        "Market and Industry Services Branch":"0f41dff5-e56d-447b-85e1-3a95a8fb7cc7",
        "Legal Services":"099265ac-e7b0-4f02-8c3d-45a4a4d3bac5",
        "Minister's Office":"e507595f-a6c7-4244-a0f2-3f4de258b2d5",
        "Office of Audit and Evaluation":"4cc47fdc-891a-4349-a9fd-f43a65476db1",
        "Strategic Policy Branch":"b93050e4-1601-41f5-bb16-bf95709c1a30",
        "Public Affairs Branch":"b6e22d31-5878-4378-9bc1-8c7a7f4574e2",
        "Programs Branch":"71619d89-756b-4795-9e1b-ecf460dce051"
    }
    # Default (for now) if there is no match, place in generic AAFC Organization
    return branches.get(con_str, "2ABCCA59-6C57-4886-99E7-85EC6C719218")

def replace_branch_and_data_steward(og_data):
        contact = extract_branch_and_data_steward(og_data)
        branch = switch_branch(contact[2].strip())
        data_steward = contact[len(contact)-1].strip()
        og_data["owner_org"] = branch
        og_data["data_steward_email"] = data_steward
        #print (json.dumps(og_data))

def main():
    #Get the lastest list from registry
    registry_url = os.getenv("registry_url")
    registry_ids = query_site_for_newdata(registry_url, "&fq=publication:open_government&rows=500", hours_ago=48)
    # Get the lastest list from OG
    og_site = "https://open.canada.ca/data/"
    og_ids = query_site_for_newdata(og_site, "&fq=organization:aafc-aac&rows=500", hours_ago=48)

    # Go through both lists, retrieve missing data from OG and post into Registry and record event of failure
    for id in og_ids:
        if id in registry_ids:
            continue
        res = create_to_registry(id)
        if res is False:
            res = update_to_registry(id)
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

def get_data_from_url(package_id, url):
    #site = os.getenv("registry_url")
    site = os.getenv(url)
    rckan = RemoteCKAN(site)

    data_as_d = {"id":package_id}
    try:
        ret = rckan.call_action("package_show", data_dict=data_as_d)#data_as_dict )
    except Exception as e:
    # if no data exists yet, return empty
        ret = []

    return ret



if __name__ == "__main__":
    load_dotenv()
    #post_to_regsistry("08ba1d1c-4985-46d4-be2d-495005689db2")
    main()
