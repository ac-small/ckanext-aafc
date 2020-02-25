import json
import urllib
import urllib2




def query_with_get( site, apicall, q_param, apikey = None):
    """
    Query remote site with get
    :param site:
    :param apicall:
    :param q_param:
    :param apikey:
    :return:
    """

    url1 = site + apicall
    req = urllib2.Request(url1 + q_param)
    if apikey != None:
        req.add_header('Authorization', apikey)
    # response = urllib.request.urlopen(req)
    # For Python 2.7
    response = None
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        # print("might not have the package in OG site yet")
        return None
    except:
        print("Error happening querying OG site")
        return None
    res = response.read()

    return res


# TODO: moved to here for now before delete it.
def post_to_site(site, action_string, data_as_dict, apikey):
    """

    :param site:
    :param action_string: like "api/3/action/package_update" , or "api/3/action/package_create"
    :param data_as_dict:
    :return:
    """


    data_string = urllib.quote(json.dumps(data_as_dict))
    url = site + action_string #"api/3/action/package_update"
    request = urllib2.Request(url)

    request.add_header('Authorization', apikey)


    response = None
    try:
        response = urllib2.urlopen(request, data_string)
    except urllib2.HTTPError as e:
        # print("might not have the package in OG site yet")
        return False
    except:
        print("Error happening querying OG site")
        return False

    pass