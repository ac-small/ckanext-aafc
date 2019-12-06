#!/usr/bin/env python
import ssl
import urllib
import json
import pprint
from dotenv import load_dotenv
import os

# Use the json module to dump a dictionary to a string for posting.
# data_string = urllib.parse.quote(json.dumps({'id': 'b22cd297-cdb4-4d76-9f79-cc1c16d0e9e7'}))
# print (data_string)

#ssl._create_default_https_context = ssl._create_unverified_context

def get_unfilled_dataset():
    load_dotenv()
    registry_url = os.getenv("registry_url")
    url1 = registry_url + "api/3/action/package_search"
    q_param = "?q=open_government_portal_record_e:n/a"
    # Make the HTTP request
    response = urllib.request.urlopen(url1 + q_param)
    res = response.read()
    # with open("res2.json","w") as fout:
    #     fout.write(str(res))
    response_dict = json.loads(res)
    result = response_dict['result']
    count = result['count']
    print(f'count:{count}')
    res_list = result['results']
    return (count, res_list)



def query_remote(package_id):
    open_gov_url = os.getenv("open_gov_url")
    url1 = open_gov_url + "api/3/action/package_show"
    #q_param = "?id=b22cd297-cdb4-4d76-9f79-cc1c16d0e9e7"
    q_param = f'?id={package_id}'



    req = urllib.request.Request(url1 + q_param, headers={'Authorization':'b5a64a5a-e737-4fe2-9ae8-f92e7c7a8072'})

    response = urllib.request.urlopen(req)

    res = response.read()
    # with open("res2.json","w") as fout:
    #     fout.write(str(res))
    response_dict = json.loads(res)
    return response_dict

def main():
    count, res_list = get_unfilled_dataset()
    for i in range(count):
        a_res = res_list[i]
        print(f'id: {a_res["id"]}, title:{a_res["title"]}')


def syncronize_registry(package_id):
    # English: http: // open.canada.ca / data / en / dataset / {PACKAGE_ID}
    # French: http: // ouvert.canada.ca / data / fr / dataset / {PACKAGE_ID}
	# metadata_modified
    pass


def main2():
    query_remote()


if __name__ == "__main__":
    load_dotenv()
    main()
 