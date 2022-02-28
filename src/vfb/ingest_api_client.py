import logging
import os
import requests
import json

from exception.crawler_exception import CrawlerException

logging.basicConfig()
logging.root.setLevel(logging.INFO)
log = logging.getLogger(__name__)

GET_USER_DETAILS = "{curation_api}/user/admin/?user_orcid={user_orcid}&admin_orcid={admin_orcid}&admin_apikey={admin_apikey}"
POST_NEURON_TYPE = "{curation_api}/neuron/?orcid={user_orcid}&apikey={user_apikey}"

SUCCESS = 201


def get_user_details(user_orcid_id):
    log.info("Getting user details from VFB ingest api '{}'.".format(user_orcid_id))
    headers = {'Accept': 'application/json'}
    r = requests.get(GET_USER_DETAILS.format(curation_api=os.environ['CURATIONAPI'],
                                             user_orcid=user_orcid_id,
                                             admin_orcid=os.environ['CURATIONAPI_USER'],
                                             admin_apikey=os.environ['CURATIONAPI_KEY']),
                     headers=headers)

    if r.status_code != 200:
        log.error("Error occurred while getting vfb user {}".format(user_orcid_id) + "\n" + r.text)
        raise CrawlerException("Error occurred while getting vfb user {}".format(user_orcid_id))

    return r.json()


def post_neuron(data, user_orcid, api_key):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data_wrapper = dict()
    data_wrapper["neurons"] = [vars(data)]
    # print(json.dumps(vars(data)))
    r = requests.post(POST_NEURON_TYPE.format(curation_api=os.environ['CURATIONAPI'],
                                              user_orcid=user_orcid,
                                              user_apikey=api_key), data=json.dumps(data_wrapper), headers=headers)

    if r.status_code != SUCCESS:
        log.error("Error occurred while posting neurons of user {} data {}".format(user_orcid, str(data)))
        log.error("Internal cause of neuron post error is: " + "\n" + r.text)
        raise CrawlerException("Error occurred while posting neurons of user {} : {}".format(user_orcid, r.text))

    return r.status_code, r.json()
