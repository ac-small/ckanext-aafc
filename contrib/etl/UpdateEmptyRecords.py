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
for i in range(count):
    a_res = res_list[i]
    print(f'id: {a_res["id"]}, title:{a_res["title"]}')

