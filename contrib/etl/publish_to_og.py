import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
from ckanapi import RemoteCKAN

to_remove = ["aafc_sector", "procured_data", "aafc_subject", "procured_data_organization_name", "authoritative_source",
             "drf_program_inventory", "data_steward_email", "elegible_for_release", "publication",
             "data_source_repository", "aafc_note", "drf_core_responsibilities", "aafc_resource_metadata_schema",
             "mint_a_doi", "other", "ineligibility_reason", "authority_to_release", "privacy", "formats", "security",
             "official_language", "access_to_information", "access_restriction", "organization",
             ]
to_replace = {"type": "dataset", "owner_org": "2ABCCA59-6C57-4886-99E7-85EC6C719218", "restrictions": "unrestricted",
              "collection": "primary", "jurisdiction": "federal"}


def get_data_from_reg(package_id):
    """
    Get data from registry
    :param package_id:
    :return:
    """
    site = os.getenv("registry_url")
    rckan = RemoteCKAN(site)

    data_as_d = {"id": package_id}
    try:
        ret = rckan.call_action("package_show", data_dict=data_as_d)  # data_as_dict )
    except Exception as e:
        print("failed")

    return ret


def get_n_post(package_id):
    """
    Get an data from registry , modify and post it to OG
    :param package_id:
    :return:
    """
    og_data = get_data_from_reg(package_id)

    # replace
    for k,v  in to_replace:
        og_data[k] = to_replace[k]

    # remove
    for k  in to_remove:
        del og_data[k]

    og_site = os.getenv("open_gov_url")
    og_key = os.getenv("api_key")
    rckan = RemoteCKAN(og_site, apikey=og_key)

    try:
        ret = rckan.call_action("package_create", data_dict=og_data)

    except Exception as e:
        return False

    return True


def get_ids():
    site = os.getenv("registry_url")
    rckan = RemoteCKAN(site)

    '''
        # query for last 48 hours
        apicall = "api/3/action/package_search"
        q_param = "?q=metadata_modified:[2019-10-10T21:15:00Z TO *]&fq=publication:open_government"

        if hours_ago is None:
            hours_ago = 48
        two_days_ago = datetime.now() - timedelta(hours=hours_ago)
        str_2days_ago =  two_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ')
        q_param1 = "?q=metadata_modified:[%s%sTO%s*]"%(str_2days_ago, '%20','%20') + sec_param
        res = query_with_get(site, apicall, q_param1)
        # process the result to get filtered ids
    '''

    try:
        ret = rckan.call_action("package_list")
    except Exception as e:
        return []
    return ret


def main():
    id_list = get_ids()
    for id in id_list:
        res = get_n_post(id)
        if res is False:

            with open("error_post_to_og.log", "a") as fout:
                now = datetime.now()
                event = "Failed publishing package id %s on %s\n"%(id, now)
                fout.write(event)

if __name__ == "__main__":
    load_dotenv()
    get_ids()
    main()