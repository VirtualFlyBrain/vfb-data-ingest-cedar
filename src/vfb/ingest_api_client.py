import logging
import os
import requests
import json


logging.basicConfig()
logging.root.setLevel(logging.INFO)
log = logging.getLogger(__name__)

GET_USER_DETAILS = "{curation_api}/user/admin/?user_orcid={user_orcid}&admin_orcid={admin_orcid}&admin_apikey={admin_apikey}"
POST_NEURON_TYPE = "{curation_api}/neuron/?orcid={user_orcid}&apikey={user_apikey}"


def get_user_details(user_orcid_id):
    log.info("Getting user details from VFB ingest api '{}'.".format(user_orcid_id))
    headers = {'Accept': 'application/json'}
    r = requests.get(GET_USER_DETAILS.format(curation_api=os.environ['CURATIONAPI'],
                                             user_orcid=user_orcid_id,
                                             admin_orcid=os.environ['CURATIONAPI_USER'],
                                             admin_apikey=os.environ['CURATIONAPI_KEY']),
                     headers=headers)
    return r.json()


def post_neuron(data, user_orcid, api_key):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data.set_id("dummy_id")
    data_wrapper = dict()
    data_wrapper["neurons"] = [vars(data)]
    print(json.dumps(data_wrapper))
    # print(json.dumps(vars(data)))
    r = requests.post(POST_NEURON_TYPE.format(curation_api=os.environ['CURATIONAPI'],
                                              user_orcid=user_orcid,
                                              user_apikey=api_key), data=json.dumps(data_wrapper), headers=headers)
    # r = requests.post(POST_NEURON_TYPE.format(curation_api=os.environ['CURATIONAPI'],
    #                                           user_orcid=user_orcid,
    #                                           user_apikey=api_key),
    #                   json=data)
    print(r.status_code)
    print(r.text)
