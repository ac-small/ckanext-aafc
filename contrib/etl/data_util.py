#!/usr/bin/env python
# -*- coding: cp1250 -*-
from dotenv import load_dotenv
from helper import *
import os
# import re
import sys, getopt
from synch_with_og import transform_data, to_replace
from ckanapi.errors import *
import yaml
import requests
import re


def purge_all_data(site):
    """
    Purge all datasets in site
    :param site:
    :return:
    """
    rckan = RemoteCKAN(site)

    id_list = rckan.call_action("package_list")
    purge_dataset(id_list)
    pass


def dump_data_as_json(params):  # site, json_file_name, from_og = False):
    json_file_name, flag = params
    print "dump_data_as_json called"
    print [json_file_name, flag]

    if flag == 'f':
        all_data = get_all_data_og()
    elif flag == 's' : # sink, in LLI project it's lli site
        all_data = get_all_data(True)
    else: # default, source site. in LLI it's Registry
        all_data = get_all_data()

    extracted = all_data["results"]

    with open("Data/" + json_file_name, "w") as fo:
        fo.write(json.dumps(extracted))

    pass


def load_json_data(params):
    json_file_name, from_og = params

    keys_to_remove = load_json("Data/keysToRemove.json")
    items_to_add = load_json("Data/fieldsAddedForLli.json")
    rev_dict = load_json("Data/reverse_kw_dict.json")
    extracted = load_json("Data/" + json_file_name)

    data = transform_data(extracted, keys_to_remove, items_to_add, rev_dict, to_replace)

    site = os.getenv("destination_url")
    dest_key = os.getenv("destination_api_key")
    rckan = RemoteCKAN(site, apikey=dest_key)
    count = 0
    rows_limite = os.getenv("rows_to_get")
    for d in data:
        if count > int(rows_limite):
            print("Limit reached")
            break
        if d["id"] in ["771f56ff-6ef2-477c-aa5c-e538801dcddc","dafded61-61a2-478d-91f6-2c77f030214b"]:
            continue


        print("####id:" + d["id"])
        try:
            ret = rckan.call_action("package_create", data_dict=d)
        except ValidationError as ev:
            print("Failure posting, validation error")
            for k, v in ev.error_dict.items():
                if k == '__type':
                    continue
                print(" %s : %s" % (k, v))
            continue
        except Exception as e:
            print("Failure posting, other reason ")
            print("Error message : %s" % e.message)
        count += 1

def push_data(params):
    json_file_name, dummy = params

    data = load_json("Data/" + json_file_name)
    site = os.getenv("source_url")
    dest_key = os.getenv("source_api_key")
    rckan = RemoteCKAN(site, apikey=dest_key)
    count = 0
    rows_limite = os.getenv("rows_to_get")
    for d in data:
        if count > int(rows_limite):
            print("Limit reached")
            break
        print("####id:" + d["id"])
        ret = None
        try:
            ret = rckan.call_action("package_create", data_dict=d)
        except ValidationError as ev:
            print("Failure posting, validation error")
            for k, v in ev.error_dict.items():
                if k == '__type':
                    continue
                print(" %s : %s" % (k, v))
            continue
        except Exception as e:
            print("Failure posting, other reason ")
            print("Error message : %s" % e.extra_msg)
        count += 1
    pass

def load_yaml(file_name):
    with open(file_name) as fin:
        documents = yaml.full_load(fin)
    return documents


def test_purge_all_data(params):
    site = os.getenv("destination_url")
    purge_all_data(site)


def test_purge_remote():
    """
    purge data in source.   for new posting during test
    :return:
    """
    # id_list = ["dafded61-61a2-478d-91f6-2c77f030214b","72a1decc-a602-4c76-8180-b07621967fe2"]
    id_list = ["3055d83b-edac-4b38-87fd-1b54730dbec4"]
    purge_dataset(id_list, source=True)


def test1(p=None):
    data = load_json("Data/" + 'all_from_qa.json')
    count = 0
    for d in data:
        print("%d id:%s" % (count, d['id']))
        count += 1
    first10 = data[1:3]
    with open("Data/" + "first3_from_qa.json", "w") as fo:
        fo.write(json.dumps(first10))

    pass



def test_dumpkw(params):
    '''
    Convert keywords into simple form and dump to JSON file
    :param params:
    :return:
    '''
    documents = load_yaml("Data/canada_keywords.yaml")
    print params
    kw_as_dic = {}
    pres_val_chcs = documents[0]["values"]["choices"]
    for item in pres_val_chcs:
        lble = item["label"]["en"]
        lblf = item["label"]["fr"]
        val = item["value"]
        print(val,lble,lblf)
        kw_as_dic[val] = [lble,lblf]

    with open("Data/keywords_as.json", "w") as fo:
        fo.write(json.dumps(kw_as_dic, encoding='utf-8', indent=4,ensure_ascii=True))
    # with open("Data/keywords_as.yaml", "w") as fo:
    #      fo.write(yaml.safe_dump(kw_as_dic, encoding='utf-8', allow_unicode=True))


    pass


def compare_dict(ds, dt, n=0):
    inn = ">>" + ">" * n
    outt = "<<" + "<" * n

    if isinstance(ds, dict):
        for k, v in ds.items():
            if not isinstance(dt, dict):
                print("####key ds:%s" % k)
                print("****class dt" + str(dt.__class__) + str(dt))
                continue
            if dt.has_key(k):
                # print("%s, both"%k)
                # pass
                compare_dict(v, dt[k], n + 1)
            else:
                print("%s, only ds" % k)
    elif isinstance(ds, list):
        for idx, val in enumerate(ds):
            val2 = dt[idx]
            print("@@@>")
            compare_dict(val, val2)
            print("@@@<")
    else:
        if dt == ds:
            # print("==%s"%ds)
            pass
        else:
            print(inn)
            print("%s##%s" % (ds, dt))
            #     pass
            print(outt)


def test_compare_dict(param):
    file1 = "Data/fromQa.json"
    file2 = "Data/AboutToQa1.json"
    d1 = load_json(file1)
    d2 = load_json(file2)
    compare_dict(d1, d2)


def load_raw_tosrc(params):
    site, json_file_name, from_og = params

    data = load_json("Data/" + json_file_name)
    site = os.getenv("source_url")
    dest_key = os.getenv("source_api_key")
    # site = os.getenv("destination_url")
    # dest_key = os.getenv("destination_api_key")
    rckan = RemoteCKAN(site, apikey=dest_key)
    data2 = [data]
    for d in data2:
        print("####id:" + d["id"])
        try:
            ret = rckan.call_action("package_create", data_dict=d)
        except ValidationError as ev:
            print("Failure posting, validation error")
            for k, v in ev.error_dict.items():
                if k == '__type':
                    continue
                print(" %s : %s" % (k, v))
            continue
        except Exception as e:
            print("Failure posting, other reason ")
            print(" Error: %s" % e.message)
            continue



def gen_reverse_dict(params):
    generate_kw_reverse_dict()

def simple_pull(params):
    site = os.getenv("source_url")
    dest_key = os.getenv("source_api_key")
    session = requests.Session()
    session.verify = False
    rckan = RemoteCKAN(site, apikey=dest_key,session=session)
    try:
        ret = rckan.call_action("package_list")
        for id in ret:
            print(id)
    except ValidationError as ev:
         print("Failure posting, validation error")
         for k, v in ev.error_dict.items():
             if k == '__type':
                 continue
             print(" %s : %s" % (k, v))
    except Exception as e:
         print("Failure posting, other reason ")
         print("Error message : %s" % e.message)

def test(param):
    #test1(param)
    #test2(param)
    #test_purge_remote(param)
    test_dumpkw(param) # dump keywords as json file


query_term={"q": " canada_keywords: \"ecosystems\"", "fq":""}


query_term2={"q":' canada_keywords: "agriculture" canada_keywords: "crops"', "fq":""}
query_term3={"q":' ', "fq":""}
def process_q(qterm):
    '''
    process q term
    :param qterm:
    :return: a pair of values with keyword and new string
    '''
    pattern = r"\s*canada_keywords:\s*\"([^\"]+)\""
    res = re.findall(pattern, qterm, re.MULTILINE)
    new_qterm = qterm
    if len(res) > 0:
        keywords = res
        new_qterm = re.sub(pattern,qterm,"",10)

    return keywords,new_qterm

def test3(param):
    query_term_data = query_term2 #json.loads(query_term)
    qterm = query_term_data['q']
    kw,news = process_q(qterm)
    print (" kw:%s, news:%s"%(kw,news))



funcname_map = {
    "purge": test_purge_all_data,
    "dump": dump_data_as_json,
    "load": load_json_data,
    "t1": test1,
    "t3":test3,
    "test": test,
    "genKwRev": gen_reverse_dict,
    "loads": load_raw_tosrc,
    "tcompared": test_compare_dict,
    "push": push_data,
    "simple_pull":simple_pull
}


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "f:")
    except getopt.GetoptError:
        print """
        data_util.py -f <function> param1 param2 param3'
        -f options:
            purge -purge all data
            dump -dump data to drive as json
                param1: The output json file name
                param2: 's', dump sink site, 'n' (or others not 'f') dump source site
            load -load json file as data from drive
            push -push datafrom json file to remote site
                param1: the json file name
      """
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-f':
            value = arg
            func = funcname_map.get(value, "invalid")
            if func == "invalid":
                print "Not a valid function"
                exit()

            func(args)

        # elif opt == '-o':
        #     value = arg
        #     oparams = value

    # print 'function is: ', func
    # #print 'Other params are ', oparams
    # print "extra params:", args


if __name__ == "__main__":
    load_dotenv()
    main(sys.argv[1:])
