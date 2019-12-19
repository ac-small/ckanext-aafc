#!/usr/bin/env python
import json
from dotenv import load_dotenv
from helper import *



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
    id_list = query_by_aafc()
    with open("aafc_id_list2.txt","w") as fout:
         str = u','.join(id_list)
         fout.write(str)


if __name__ == "__main__":
    load_dotenv()
    main()
