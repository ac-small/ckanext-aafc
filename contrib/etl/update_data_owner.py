#!/usr/bin/env python
# -*- coding: cp1250 -*-
from dotenv import load_dotenv
from helper import *
from update_harvest_flag import update_package

'''
Update the Data Owner field to the data contained in the Data Steward record for existing records. 
'''


def update_dataowner(package_id, data_owner = ""):
    '''
    update the data owner field(Labled as "Data Owner" but field name is "creator") in the package

    '''
    data = {"creator":data_owner}
    update_package(package_id,data)


if __name__ == "__main__":
    load_dotenv()
    ids = get_all_ids(remote=False)
    for i, pid in enumerate(ids):
        #if i in include:
        #    print(">>>%d, %s"%(i, pid))
        #    update_existing_harvested(pid)
        res = get_data_from_reg(pid)
		# Fro refix of AR 212
		is_harvested = res.get("aafc_is_harvested")
		if not is_harvested:
		   continue
        steward = res.get("data_steward_email")
        update_dataowner(pid, steward)
