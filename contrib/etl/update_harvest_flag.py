#!/usr/bin/env python
# -*- coding: cp1250 -*-
from dotenv import load_dotenv
from helper import *
from publish_to_og import get_data_from_reg

'''
This is part of implementing aafc_is_harvested flag to differentiate those that were harvested from the one created internally in AAFC
Only run once after the obsolete records are removed
'''

def update_package(package_id, to_add):
    '''
    update a dataset in registry with added data
    '''
    orig_data = get_data_from_reg(package_id)
    for k, v in to_add.items():
        orig_data[k] = v
    d_site = os.getenv("destination_url")
    d_key = os.getenv("destination_api_key")
    rckan = RemoteCKAN(d_site, apikey=d_key)

    try:
        ret = rckan.call_action("package_update", data_dict=orig_data)
    except Exception as e1:
        print(e1)
        return False
    return True

def update_existing_harvested(package_id):
    '''
    add existing data with harvest flag.
    Note: "creator" is a new field that needs to be added. Otherwise there will be a failure
    '''
    data = {"aafc_is_harvested":"true","creator":"admin"}
    update_package(package_id,data)


if __name__ == "__main__":
    load_dotenv()
    ids = get_all_ids(remote=False)
    #for pid in ids[4:-3]: for test only
    for pid in ids:
        update_existing_harvested(pid)
