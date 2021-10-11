#!/usr/bin/env python
# -*- coding: cp1250 -*-
from dotenv import load_dotenv
from helper import *

'''
Purpose:
Delete the datasets form local registry that the open government already removed.

Notes:
Since the deleting of OG are not frequent action, this program is created so it can be
scheduled by a separate task with much lower frequency. for example run onece every 2 weeks
'''

def dump_all_remote_ids():
    '''
    used only during dev
    '''
    ids = get_all_ids()
    print(len(ids))
    with open("Data/" + "all_ids_from_og.json", "w") as fo:
        fo.write(json.dumps(ids))

def get_missing_ids():
    remote_ids = get_all_ids()
    #For test during dev
    #with open("Data/" + "all_ids_from_og.json") as fo:
    #    remote_ids = json.load(fo)

    local_ids = get_all_ids(False)
    #print("local id len:%i"%len(local_ids))
    #print("remote id len:%i"%len(remote_ids))

    missing_ids = []
    for id in local_ids:
        if id not in remote_ids:
            missing_ids.append(id)

    return missing_ids


if __name__ == "__main__":
    load_dotenv()
    missing = get_missing_ids()
    #For checing length
    #print(len(missing))

    #missing = missing[:3]
    #for id in missing:
    #    print(id)
    purge_dataset(missing)