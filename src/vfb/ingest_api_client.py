import logging
import os
import requests
import json

from exception.crawler_exception import CrawlerException, ContentException

logging.basicConfig()
logging.root.setLevel(logging.INFO)
log = logging.getLogger(__name__)

GET_USER_DETAILS = "{curation_api}/user/admin/?user_orcid={user_orcid}&admin_orcid={admin_orcid}&admin_apikey={admin_apikey}"
POST_NEURON = "{curation_api}/neuron/?orcid={user_orcid}&apikey={user_apikey}"
POST_DATASET = "{curation_api}/dataset/?orcid={user_orcid}&apikey={user_apikey}"
POST_SPLIT = "{curation_api}/split/?orcid={user_orcid}&apikey={user_apikey}"
POST_EP_SPLIT = "{curation_api}/ep_split/?orcid={user_orcid}&apikey={user_apikey}"
POST_EP_SPLIT_FLP_OUT = "{curation_api}/ep_split_flp_out/?orcid={user_orcid}&apikey={user_apikey}"

SUCCESS = 201


def get_user_details(user_orcid_id):
    log.info("Getting user details from VFB ingest api '{}'.".format(user_orcid_id))
    headers = {'Accept': 'application/json'}
    service_url = GET_USER_DETAILS.format(curation_api=os.environ['CURATIONAPI'],
                                          user_orcid=user_orcid_id,
                                          admin_orcid=os.environ['CURATIONAPI_USER'],
                                          admin_apikey=os.environ['CURATIONAPI_KEY'])
    log.info("Request made: " + service_url)
    r = requests.get(service_url, headers=headers)

    if r.status_code != 200:
        log.error("Error occurred while getting vfb user {}".format(user_orcid_id) + "\n" + r.text)
        raise CrawlerException("Error occurred while getting vfb user {}".format(user_orcid_id))

    return r.json()


def post_neuron(data, user_orcid, api_key):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data_wrapper = dict()
    data_wrapper["neurons"] = [vars(data)]
    print(json.dumps(vars(data)))
    log.info("Posting neuron ({}) of user {} to VFB API.".format(str(data.primary_name), user_orcid))
    r = requests.post(POST_NEURON.format(curation_api=os.environ['CURATIONAPI'],
                                         user_orcid=user_orcid,
                                         user_apikey=api_key), data=json.dumps(data_wrapper), headers=headers)

    if r.status_code != SUCCESS:
        log.error("Error occurred while posting neurons of user {} data {}".format(user_orcid, str(data)))
        log.error("Internal cause of neuron post error is: " + "\n" + r.text)
        raise ContentException("Internal cause of neuron post error is: " + "\n" + r.text)

    return r.json()


def download_neuron_image(image_url, dataset_name):
    if image_url:
        if "IMAGES_FOLDER_PATH" in os.environ:
            target_folder = os.path.join(os.getenv("IMAGES_FOLDER_PATH"), dataset_name)
            print("Target Folder: " + str(target_folder))
            if target_folder and not os.path.exists(target_folder):
                os.makedirs(target_folder)
            get_response = requests.get(image_url, stream=True)
            file_name = image_url.split("/")[-1]
            with open(os.path.join(target_folder, file_name), 'wb') as f:
                for chunk in get_response.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
            log.info("Neuron image file saved to: " + str(os.path.join(target_folder, file_name)))
        else:
            raise CrawlerException("Neuron images download folder is not specified in the environment variables. !!!")


def post_dataset(data, user_orcid, api_key):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data_content = vars(data)
    data_content.pop('publication', None)
    data_content.pop('source_data', None)
    print(json.dumps(data_content))
    log.info("Posting dataset ({}) of user {} to VFB API.".format(str(data.short_name), user_orcid))
    r = requests.post(POST_DATASET.format(curation_api=os.environ['CURATIONAPI'],
                                              user_orcid=user_orcid,
                                              user_apikey=api_key), data=json.dumps(data_content), headers=headers)

    if r.status_code != SUCCESS:
        log.error("Error occurred while posting dataset of user {} data {}".format(user_orcid, str(data)))
        log.error("Internal cause of dataset post error is: " + "\n" + r.text)
        raise ContentException("Internal cause of dataset post error is: " + "\n" + r.text)

    return r.json()


def post_split(data, user_orcid, api_key):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    # print(json.dumps(vars(data)))
    log.info("Posting split ({}) for user {} operation to VFB API.".format(str(data), user_orcid))
    r = requests.post(POST_SPLIT.format(curation_api=os.environ['CURATIONAPI'],
                                        user_orcid=user_orcid,
                                        user_apikey=api_key), data=json.dumps(vars(data)), headers=headers)

    if r.status_code != SUCCESS:
        log.error("Error occurred while posting split of user {} data {}".format(user_orcid, str(data)))
        log.error("Internal cause of split post error is: " + "\n" + r.text)
        raise ContentException("Internal cause of split post error is: " + "\n" + r.text)

    return r.json()


def post_ep_split(data, user_orcid, api_key):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data_wrapper = dict()
    data_wrapper["split_drivers"] = [vars(data)]
    # print(json.dumps(vars(data)))
    log.info("Posting EP/Split ({}) of user {} to VFB API.".format(str(data.primary_name), user_orcid))
    r = requests.post(POST_EP_SPLIT.format(curation_api=os.environ['CURATIONAPI'],
                                           user_orcid=user_orcid,
                                           user_apikey=api_key), data=json.dumps(data_wrapper), headers=headers)

    if r.status_code != SUCCESS:
        log.error("Error occurred while posting EP/Split of user {} data {}".format(user_orcid, str(data)))
        log.error("Internal cause of EP/Split post error is: " + "\n" + r.text)
        raise ContentException("Internal cause of EP/Split post error is: " + "\n" + r.text)

    return r.json()


def post_ep_split_flp_out(data, user_orcid, api_key):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data_wrapper = dict()
    data_wrapper["split_drivers"] = [vars(data)]
    print(json.dumps(vars(data)))
    log.info("Posting EP/Split Flp-Out ({}) of user {} to VFB API.".format(str(data.primary_name), user_orcid))
    r = requests.post(POST_EP_SPLIT_FLP_OUT.format(curation_api=os.environ['CURATIONAPI'],
                                                   user_orcid=user_orcid,
                                                   user_apikey=api_key), data=json.dumps(data_wrapper), headers=headers)

    if r.status_code != SUCCESS:
        log.error("Error occurred while posting EP/Split Flp-Out of user {} data {}".format(user_orcid, str(data)))
        log.error("Internal cause of EP/Split Flp-Out post error is: " + "\n" + r.text)
        raise ContentException("Internal cause of EP/Split Flp-Out post error is: " + "\n" + r.text)

    return r.json()
