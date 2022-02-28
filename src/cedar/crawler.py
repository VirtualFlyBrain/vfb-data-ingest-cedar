import logging
import os

import requests
import urllib.parse
from datetime import datetime as dt
from vfb.repository import db
from vfb import ingest

logging.basicConfig()
logging.root.setLevel(logging.INFO)
log = logging.getLogger(__name__)

GET_ALL_TEMPLATES = "https://resource.metadatacenter.org/search?resource_types=template&version=all&publication_status={publication_status}&sort=name&limit=499&sharing={sharing}&mode=null"
LIST_TEMPLATE_INSTANCES = "https://resource.metadatacenter.org/search?version=all&publication_status=all&is_based_on={template}&sort=lastUpdatedOnTS&limit=499&offset={offset}"
GET_TEMPLATE_INSTANCE_DATA = "https://resource.metadatacenter.org/template-instances/{template_instance}?format=jsonld"
GET_ALL_USERS = "https://resource.metadatacenter.org/users"
GET_USER_ORCID_ID = "https://user.metadatacenter.org/users/{}/summary"

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
MIN_DATE = "2000-01-01T01:01:01-01:00"
REQUEST_LIMIT = 499


def crawl():
    templates = get_all_templates()
    for template in templates:
        instances = get_template_instances(template)
        last_updated_on = dt.strptime(MIN_DATE, DATE_FORMAT)
        for instance in instances:
            try:
                instance_data = get_instance_data(instance)
                editor = get_user_orcid(instance_data["oslc:modifiedBy"])
                ingest.ingest_data(editor, instance_data, instance)
                update_time = dt.strptime(instance_data["pav:lastUpdatedOn"], DATE_FORMAT)
                if update_time > last_updated_on:
                    last_updated_on = update_time
            except Exception as err:
                log.error("Exception occurred while processing instance '{}' of template '{}'.".format(instance, template))
                log.error("Exception occurred during crawling: " + str(err))
                # db.update_last_crawling_time(template, dt.strftime(last_updated_on, DATE_FORMAT))
                log.error("Stopping the crawling.")
                break

        # db.update_last_crawling_time(template, dt.strftime(last_updated_on, DATE_FORMAT))


def get_user_orcid(user_id):
    log.info("Getting user orcid_id from cedar: " + user_id)
    user_id_short = user_id.rsplit('/', 1)[-1]

    headers = {'Accept': 'application/json', 'Authorization': os.environ['CEDAR_API_KEY']}
    r = requests.get(GET_USER_ORCID_ID.format(user_id_short), headers=headers)
    response = r.json()

    orcid_id = None
    if "authenticationProvider" in response and len(response["authenticationProvider"]) > 0:
        for provider in response["authenticationProvider"]:
            if provider["name"] == "oidc-orcid":
                orcid_id = provider["id"]

    if not orcid_id:
        raise ValueError("User's orcid_id couldn't be found in CEDAR: " + user_id)

    return orcid_id


def get_all_users():
    log.info("Getting all user data.")
    headers = {'Accept': 'application/json', 'Authorization': os.environ['CEDAR_API_KEY']}
    r = requests.get(GET_ALL_USERS, headers=headers)
    return r.json()["users"]


def get_user(all_users, user_id):
    for user in all_users:
        if user["@id"] == user_id:
            return user
    raise ValueError("User cannot be found in CEDAR: " + user_id)


def get_instance_data(template_instance):
    log.info("Getting content of the template instance '{}'.".format(template_instance))
    headers = {'Accept': 'application/json', 'Authorization': os.environ['CEDAR_API_KEY']}
    r = requests.get(GET_TEMPLATE_INSTANCE_DATA.format(template_instance=urllib.parse.quote_plus(template_instance)),
                     headers=headers)
    return r.json()


def get_template_instances(template, template_instances=None, offset=0, limit=REQUEST_LIMIT):
    log.info("Querying all instances of the template '{}'.".format(template))
    headers = {'Accept': 'application/json', 'Authorization': os.environ['CEDAR_API_KEY']}
    r = requests.get(LIST_TEMPLATE_INSTANCES.format(template=template, limit=limit, offset=offset), headers=headers)
    response = r.json()

    last_crawl_str = db.get_last_crawling_time(template)
    last_crawl_time = dt.strptime(last_crawl_str, DATE_FORMAT)

    log.info("Last crawl time of template instance '{}' is {}.".format(template, last_crawl_str))

    if template_instances is None:
        template_instances = set()

    reached_already_processed_data = False
    for resource in response["resources"]:
        last_update_time = dt.strptime(resource["pav:lastUpdatedOn"], DATE_FORMAT)
        if last_update_time > last_crawl_time:
            template_instances.add(resource["@id"])
        else:
            reached_already_processed_data = True
            break

    if len(response["resources"]) == REQUEST_LIMIT and not reached_already_processed_data:
        get_template_instances(template, template_instances, offset=offset + REQUEST_LIMIT + 1, limit=REQUEST_LIMIT)
    log.info('Total {} new template instances found for processing.'.format(len(template_instances)))
    return template_instances


def get_all_templates():
    """
    Lists all published templates that are shared with the "vfb crawler" group.

    return: all published templates that are shared with the "vfb crawler" group.
    """
    log.info('Querying all templates shared with the crawler.')
    sharing = "shared-with-me"
    # publication_status = "bibo%3Apublished"
    publication_status = "all"
    headers = {'Accept': 'application/json', 'Authorization': os.environ['CEDAR_API_KEY']}
    r = requests.get(GET_ALL_TEMPLATES.format(publication_status=publication_status, sharing=sharing), headers=headers)
    response = r.json()

    templates = set()
    for resource in response["resources"]:
        templates.add(resource["@id"])

    log.info(templates)
    log.info('Total {} templates shared with the crawler'.format(len(templates)))
    return templates
