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

def query_all_aafc(site):
    '''
    Query to get a list of all AAFC registry package ID's
    '''
    apicall = "api/3/action/package_search"
    q_param = "?fq=publication:open_government&rows=1000000"
    res = query_with_get(site, apicall, q_param)

    if res is None:
        return None
    response_dict = json.loads(res)
    results = response_dict['result']['results']
    id_list = process_a_batch(results)
    return id_list


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
        replace_regions(og_data)
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
        if reg_data != []:
        # strip all fields except we will keep the values AAFC Registry specific fields
            reg_keep = {
                'ready_to_publish': reg_data['ready_to_publish'],
                'drf_program_inventory': reg_data['drf_program_inventory'],
                'official_language': reg_data['official_language'],
                'aafc_owner_org': reg_data['aafc_owner_org'],
                'owner_org': reg_data['owner_org'],
                'data_steward_email': reg_data['data_steward_email'],
                'procured_data': reg_data['procured_data'],
                'elegible_for_release': reg_data['elegible_for_release'],
                'authority_to_release': reg_data['authority_to_release'],
                'mint_a_doi': reg_data['mint_a_doi'],
                'procured_data_organization_name': reg_data['procured_data_organization_name'],
                'privacy': reg_data['privacy'],
                'data_source_repository': reg_data['data_source_repository'],
                'drf_core_responsibilities': reg_data['drf_core_responsibilities'],
                'authoritative_source': reg_data['authoritative_source'],
                'formats': reg_data['formats'],
                'aafc_sector': reg_data['aafc_sector'],
                'security': reg_data['security'],
                'ineligibility_reason': reg_data['ineligibility_reason'],
                'access_to_information': reg_data['access_to_information'],
                'other': reg_data['other'],
                'publication': reg_data['publication'],
                'data_released': reg_data['data_released'],
                'open_government_portal_record_e': reg_data['open_government_portal_record_e'],
                'open_government_portal_record_f': reg_data['open_government_portal_record_f'],
                'groups': reg_data['groups']
            }
            # Keep ODI number if it exists, some datasets may not have an ODI.
            if 'odi_reference_number' in reg_data:
                reg_odi = {
                    'odi_reference_number': reg_data['odi_reference_number']
                }
            else:
                reg_odi = None
                
            # Update the Open Gov dataset
            if reg_odi != None:
                og_data.update(reg_odi)
            og_data.update(reg_keep)
            
        # Only map branch and data steward for external (FGP) datasets, for AAFC Registry datasets, this is not required.
        if 'ready_to_publish' in reg_data and reg_data['ready_to_publish'] == "false":
            replace_branch_and_data_steward(og_data)

        # Ensure that we reset ready to publish back to false after AAFC Registry dataset is posted to OG
        if 'ready_to_publish' in reg_data and reg_data['ready_to_publish'] == "true":
            og_data['ready_to_publish'] == "false"

        replace_regions(og_data)
        reg_site = os.getenv("registry_url")
        registry_key = os.getenv("registry_api_key")
        rckan = RemoteCKAN(reg_site, apikey=registry_key)
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

def map_regions(region):
    print (region)
    if region >= 1001 and region <= 1011:
        region = 10
    elif region >= 1101 and region <= 1103:
        region = 11
    elif region >= 1201 and region <= 1218:
        region = 12
    elif region >= 1301 and region <= 1315:
        region = 13
    elif region >= 2401 and region <= 2499:
        region = 2
    elif region >= 3501 and region <= 3560:
        region = 3
    elif region >= 4601 and region <= 4623:
        region = 46
    elif region >= 4701 and region <= 4718:
        region = 47
    elif region >= 4801 and region <= 4819:
        region = 48
    elif region >= 5901 and region <= 5959:
        region = 5
    elif region == 6001:
        region = 60
    elif region >= 6101 and region <= 6106:
        region = 61
    elif region >= 6204 and region <= 6208:
        region = 62
    return str(region)



region_mappings = { 10:(1001,1011),11:(1101,1103),12:(1201,1218),13:(1301,1315),2:(2401,2499),3:(3501,3560),
                    46:(4601,4623),47:(4701,4718),48:(4801,4819),5:(5901,5959),60:(6001),61:(6101,6106),62:(6204,6208)}
def map_regions2(reg_large):
    '''
    Another way to map large number to small number
    :param reg_large:
    :return:
    '''
    for reg_small, min_max in region_mappings.items():
        if reg_large> min_max[0] and reg_large < min_max[1]:
            return str(reg_small)

    return None

def replace_regions(og_data):
    if 'place_of_publication' in og_data and og_data['place_of_publication'] != []:
        pub_int = int(''.join(og_data['place_of_publication']))
        pub_reg = map_regions(pub_int)
        og_data['place_of_publication'] = [pub_reg]
    if 'geographic_region' in og_data and og_data['geographic_region'] != []:
        geo_int = int(''.join(og_data['geographic_region']))
        geo_reg = map_regions(geo_int)
        og_data['geographic_region'] = [geo_reg]
    return og_data


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

def main():
    #Get the lastest list from registry
    registry_url = os.getenv("registry_url")
    registry_ids = query_all_aafc(registry_url)
    # Get the lastest list from OG
    og_site = "https://open.canada.ca/data/"
    og_ids = query_site_for_newdata(og_site, "&fq=organization:aafc-aac&rows=500", hours_ago=48)

    # Go through both lists, retrieve missing data from OG and post into Registry and record event of failure
    for id in og_ids:
        if id in registry_ids:
            res = update_to_registry(id)
        else:
            res = create_to_registry(id)
        if res is False:
            #res = update_to_registry(id)
            #if res is False:
            with open("error_sync_with_og.log", "a") as fout:
                now = datetime.now()
                event = "Failed updating package id %s on %s\n"%(id, now)
                fout.write(event)


'''
Simple tests come here
'''

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




def test_regmap():
    testsets = [1008,1102,1212,1312,2450]

    for s in testsets:
        res1 = map_regions(s)
        res2 = map_regions2(s)
        print ("res1:%s,res2:%s\n"%(res1,res2))


if __name__ == "__main__":
    load_dotenv()
    #post_to_regsistry("08ba1d1c-4985-46d4-be2d-495005689db2")
    main()
    #test_regmap()
