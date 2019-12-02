import pandas as pd
import json
import numpy as np



datafile = "Data//sharepoint.xlsm"

FIELDS_SPECL_CHR = [('Collection Type', r'\d+;#'), ('Data Steward Email', r';#\d+'),
                    ('DRF', r'\d+;#')]

OWNER_ORG_PLACEHOLDER = "00000000-0000-0000-0000-000000000000"
# GROUP_INFO =[
#     {"":{"display_name":"","description":"","image_display_url": "", "title": "Inventory", "id": "bb812a2e-fd92-4077-8910-5aec702a859a", "name": "inventory"}}
# ]
# Audience
GROUP_INFO_KEYS = ["display_name","description","image_display_url","title","id","name"]

groups_info = {}

def remove_special_character(df, field, regex):
    """
    remove special characters from a column
    :param df: data frame
    :param field: field name. i.e. 'Collection Type'
    :param regex: regex expression of the pattern that need to removed. i.e. r';#\d+'
    :return: fixed data frame
    """
    dcolumn = df[field]
    df[field] = dcolumn.str.replace(regex, '')
    return df


def main():
    global  groups_info
    groups_info = load_groups("Data//groups_info.json")
    df = pd.read_excel(datafile)

    df.fillna("")
    for fr in FIELDS_SPECL_CHR:
        f = fr[0]
        r = fr[1]
        df = remove_special_character(df, f, r)

    schema = load_schema("Data//schema.json")
    generated_dic = gen_json(schema, df)

    with open("Data//dumped_data.json", "w") as ofp:
        json.dump(generated_dic, ofp)

    # For generate raw encoded data
    # with open("Data//dumped_data_asc.json", "w",encoding="cp1252") as ofp:
    #     json.dump(generated_dic, ofp, ensure_ascii=False)

    pass

def load_groups(file):
    """
    Laod group meta data file and generate a dictionary for use
    :param file:
    :return:
    """
    groups_row = []
    groups = {}
    with open(file) as json_fp:
        groups_row = json.load(json_fp)
    for g in groups_row:
        g_key = g["title"]
        g_data = {}
        for k in  GROUP_INFO_KEYS:
            g_data[k] = g[k]

        groups[g_key] = g_data
    return groups

def load_schema(file):
    sch = ""
    with open(file) as json_fp:
        sch = json.load(json_fp)
    return sch


def process(data_value, case):
    """
    For processing data to generate specific json case by case
    :param data_value:
    :param case:
    :return:
    """
    pass

def gen_json(schema, data_frame):
    """
    Generate data as dictionary so it can be dumped to json string or a file
    :param schema:
    :param data_frame:
    :return:
    """
    res = []
    count = data_frame.shape[0]
    for i in range(count):
        row = data_frame.iloc[i]
        row = row.fillna("")
        item = {}
        for k, v in schema.items():
            value = row[v['coln']]
            # if k == "keywords":
            #    value = process(value, "kw")
            if k.startswith("official_lang"):
                   value = str(value).lower()

            if 'multi' in v:
                value = value.split(",")
            if value is np.nan:
                value = ""
            if value is pd.NaT:
                value = ""
            if isinstance(value, np.bool_):
                value = str(bool(value)).lower()
            if isinstance(value, pd.Timestamp):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            # if isinstance(value, np.nan):
            #     value = "N/A"
            if k == "groups":
                #value0 = value.split(",")
                value1 = []
                for v in value:
                    v = v.strip()
                    value1.append(groups_info[v])
                value = value1
            item[k] = value
        # print(f'{k}, {v["col"]}')
        res.append(item)

    return res


if __name__ == '__main__':
    main()
    pass
