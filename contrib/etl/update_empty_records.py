#!/usr/bin/env python
import ssl
import urllib
import json
import pprint
from dotenv import load_dotenv
import os
import datetime
from helper import *
""""
Purpose: This script is used for updating the 3 fields in Registry after records published in OG:
The 3 fields are:
 data_released
 open_government_portal_record_e
 open_government_portal_record_f
"""


# Use the json module to dump a dictionary to a string for posting.
# data_string = urllib.parse.quote(json.dumps({'id': 'b22cd297-cdb4-4d76-9f79-cc1c16d0e9e7'}))
# print (data_string)

# ssl._create_default_https_context = ssl._create_unverified_context

def get_unfilled_dataset():
    load_dotenv()
    registry_url = os.getenv("registry_url")
    url1 = registry_url + "api/3/action/package_search"
    q_param = "?q=open_government_portal_record_e:N/A&fq=publication:open_government&rows=500"
    # Make the HTTP request
    response = urllib.request.urlopen(url1 + q_param)
    res = response.read()
    response_dict = json.loads(res)
    result = response_dict['result']
    count = result['count']
    print("count:%d" % count)
    res_list = result['results']
    return (count, res_list)



def query_remote(package_id):
    open_gov_url = os.getenv("open_gov_url")
    key = os.getenv("api_key")
    q_param = "?id=%s" % package_id

    res = query_with_get(open_gov_url,"api/3/action/package_show",q_param,key)
    # with open("res2.json","w") as fout:
    #     fout.write(str(res))
    if res is None:
        return None
    response_dict = json.loads(res)
    return response_dict


def syncronize_registry(package_id, data):
    """
    update registry data

    :param package_id:
    :param data:
    :return:
    """
    # English: http: // open.canada.ca / data / en / dataset / {PACKAGE_ID}
    # French: http: // ouvert.canada.ca / data / fr / dataset / {PACKAGE_ID}
    # metadata_created
    registry_url = os.getenv("registry_url")
    url1 = registry_url + "api/3/action/package_show"
    q_param = "?id=%s" % package_id

    req = urllib.request.Request(url1 + q_param)
    response = urllib.request.urlopen(req)
    res = response.read()
    response_dict = json.loads(res)
    with open("res_reg.json", "w") as fout:
        fout.write(str(res))

    dataset_dict = response_dict["result"]
    for k, v in data.items():
        dataset_dict[k] = v

    dataset_dict['resources'][0]['language'] = [u'en']

    data_string = urllib.quote(json.dumps(dataset_dict))

    url1 = registry_url + "api/3/action/package_update"
    request = urllib.request.Request(url1)

    # Creating a dataset requires an authorization header.
    # Replace *** with your API key, from your user account on the CKAN site
    # that you're creating the dataset on.
    registry_key = os.getenv("registry_api_key")
    request.add_header('Authorization', registry_key)

    response = urllib.request.urlopen(request, data_string)

    pass


def reformat_date(date_string):
    '''
    Convert the incoming date string into simple format
    :param date_string:
    :return: simplified date string
    '''
    date_obj = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%f')
    return date_obj.strftime('%Y-%m-%d')


def main():
    count, res_list = get_unfilled_dataset()
    for i in range(count):  # for each unfilled item
        a_res = res_list[i]
        package_id = a_res["id"]
        # retrieve info from OG
        res_og = query_remote(package_id)
        if res_og is None:
            print("The dataset %s is not published in OG yet" % package_id)
            continue
        data_og = res_og['result']
        # populate retrieved value
        data_fill = {'data_released': reformat_date(data_og['metadata_created']),
                     'open_government_portal_record_e': u'https://open.canada.ca/data/en/dataset/%s' % package_id,
                     'open_government_portal_record_f': u'https://ouvert.canada.ca/data/fr/dataset/%s' % package_id}
        syncronize_registry(package_id, data_fill)

        print("id: %s, , title: %s, publication: %s" % (a_res["id"], a_res["title"], a_res["publication"])).encode('utf-8')


def testModification():
    data_fill = {'data_released': '2021-12-12',
                 'open_government_portal_record_e': u'http://open.canada.ca/data/en/dataset/%s' % "xxxxx-eeeee",
                 'open_government_portal_record_f': u'http://ouvert.canada.ca/data/fr/dataset/%s' % "xxxxx-fffff"}
    syncronize_registry("e328838f-3bfc-4d86-9cc5-23de0b549c91", data_fill)


if __name__ == "__main__":
    load_dotenv()
    main()
