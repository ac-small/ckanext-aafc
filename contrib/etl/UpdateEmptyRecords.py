#!/usr/bin/env python
import ssl
import urllib
import urllib2
import json
import pprint
from dotenv import load_dotenv
import os
import datetime


# Use the json module to dump a dictionary to a string for posting.
# data_string = urllib.parse.quote(json.dumps({'id': 'b22cd297-cdb4-4d76-9f79-cc1c16d0e9e7'}))
# print (data_string)

# ssl._create_default_https_context = ssl._create_unverified_context

def get_unfilled_dataset():
    load_dotenv()
    registry_url = os.getenv("registry_url")
    url1 = registry_url + "api/3/action/package_search"
    q_param = "?q=open_government_portal_record_e:N/A&fq=publication:open_government"
    # Make the HTTP request
    # response = urllib.request.urlopen(url1 + q_param)
    # for Python 2.7
    response = urllib2.urlopen(url1 + q_param)
    res = response.read()
    # with open("res2.json","w") as fout:
    #     fout.write(str(res))
    response_dict = json.loads(res)
    result = response_dict['result']
    count = result['count']
    print("count:%d" % count)
    res_list = result['results']
    return (count, res_list)


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
    except urllib2.HTTPError:
        # print("might not have the package in OG site yet")
        return None
    except:
        print("Error happening querying OG site")
        return None
    res = response.read()

    return res



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
    # metadata_modified
    registry_url = os.getenv("registry_url")
    url1 = registry_url + "api/3/action/package_show"
    q_param = "?id=%s" % package_id

    # req = urllib.request.Request(url1 + q_param) #, headers={'Authorization':key}) # Python 3.6
    req = urllib2.Request(url1 + q_param)
    # response = urllib.request.urlopen(req)
    response = urllib2.urlopen(req)
    res = response.read()
    # with open("res2.json","w") as fout:
    #     fout.write(str(res))
    response_dict = json.loads(res)
    with open("res_reg.json", "w") as fout:
        fout.write(str(res))

    # dataset_dict = {
    #     'name': 'my_dataset_name',
    #     'notes': 'A long description of my dataset',
    # }
    dataset_dict = response_dict["result"]
    # dataset_dict['id'] = response_dict["result"]["id"]
    # dataset_dict['title'] = "Open Gov  Modified2"
    for k, v in data.items():
        dataset_dict[k] = v

    dataset_dict['resources'][0]['language'] = [u'en']

    # data_string = urllib.parse.quote(json.dumps(dummy))#dataset_dict))
    data_string = urllib.quote(json.dumps(dataset_dict))

    # bdata = bytes(data_string, 'utf-8')
    # bdata = bytes(json.dumps(dummy), 'utf-8')
    # data = urllib.parse.urlencode(dummy)#dataset_dict)
    # data = data.encode()
    url1 = registry_url + "api/3/action/package_update"
    request = urllib2.Request(url1)

    # Creating a dataset requires an authorization header.
    # Replace *** with your API key, from your user account on the CKAN site
    # that you're creating the dataset on.
    registry_key = os.getenv("registry_api_key")
    request.add_header('Authorization', registry_key)

    response = urllib2.urlopen(request, data_string)

    # response = urllib.request.urlopen(req)

    pass


def reformat_date(date_string):
    '''
    Convert the incoming date string into simple format
    :param date_string:
    :return: simplified date string
    '''
    date_obj = datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%f')
    return date_obj.strftime('%Y-%m-%d')


def process_a_batch(data_list):
    length = len(data_list)
    ids = []
    for i in range(length):
        a_id = data_list[i]["id"]
        ids.append(a_id)
        #print("id:" + a_id)
    return ids

def query_by_aafc():
    """
    Query OG site to retrieve all the ids of AAFC
    :return:
    """
    rows = 100
    og = "https://open.canada.ca/data/"
    apicall = "api/3/action/package_search"
    q_param0 = "?q=organization:aafc-aac&rows=%d" % rows


    # useful queries:
    # ?q=metadata_modified:[2019-10-10T21:15:00Z TO *]
    #
    res = query_with_get(og, apicall, q_param0)

    if res is None:
        return None

    response_dict = json.loads(res)
    data = response_dict['result']
    record_cnt = data['count']
    results = data['results']
    id_list = process_a_batch(results)
    batches = record_cnt / rows +1

    for b in range(1,batches):
        offset = b * rows
        q_param = "?q=organization:aafc-aac&rows=%d&start=%d" % (rows,offset)
        res = query_with_get(og, apicall, q_param)
        response_dict = json.loads(res)
        results = response_dict['result']['results']
        id_list_curr = process_a_batch(results)
        id_list.extend(id_list_curr)



    return id_list




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
        data_fill = {'data_released': reformat_date(data_og['metadata_modified']),
                     'open_government_portal_record_e': u'http://open.canada.ca/data/en/dataset/%s' % package_id,
                     'open_government_portal_record_f': u'http://ouvert.canada.ca/data/fr/dataset/%s' % package_id}
        syncronize_registry(package_id, data_fill)

        print("id: %s, , title: %s, publication: %s" % (a_res["id"], a_res["title"], a_res["publication"]))


def testModification():
    data_fill = {'data_released': '2021-12-12',
                 'open_government_portal_record_e': u'http://open.canada.ca/data/en/dataset/%s' % "xxxxx-eeeee",
                 'open_government_portal_record_f': u'http://ouvert.canada.ca/data/fr/dataset/%s' % "xxxxx-fffff"}
    syncronize_registry("e328838f-3bfc-4d86-9cc5-23de0b549c91", data_fill)


if __name__ == "__main__":
    load_dotenv()
    #main2()
    id_list = query_by_aafc()
    with open("aafc_id_list.txt","w") as fout:
         str = u','.join(id_list)
         fout.write(str)