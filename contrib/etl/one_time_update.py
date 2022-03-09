#!/usr/bin/env python
# -*- coding: cp1250 -*-
from dotenv import load_dotenv
from helper import *

def get_record_from_reg(package_id):

    site = os.getenv("registry_url")
    api_key= os.getenv("registry_api_key")
    rckan = RemoteCKAN(site, apikey=api_key)

    data_as_d = {"id": package_id}
    try:
        ret = rckan.call_action("package_show", data_dict=data_as_d)  # data_as_dict )
    except Exception as e:
        print("failed")

    #print(ret)
    return ret


def update_package(data):
    '''
    update a dataset in registry with added data
    '''
    d_site = os.getenv("destination_url")
    d_key = os.getenv("destination_api_key")
    rckan = RemoteCKAN(d_site, apikey=d_key)
    #print(package_id)
    print(data)
    try:
        ret = rckan.call_action("package_update", data_dict=data)
    except Exception as e1:
        print(e1)
        return False
    return True


def update_resource_date_published(data):
    for res in data["resources"]:
        if "date_published" not in res:
            res["date_published"]= data["date_published"]
        if  res["format"] is not None:
            res["format"] = "other"
        if "resouce_type" not in res:
            res["resource_type"]= "dataset"
    #print(data)
    data["aafc_is_harvested"]="true"
    data["creator"]= data["data_steward_email"]
    update_package(data)


if __name__ == "__main__":
    load_dotenv()
    package = get_record_from_reg("<insert package id>")
    update_resource_date_published(package)
