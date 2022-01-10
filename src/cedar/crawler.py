import logging
import os
import requests
import urllib.parse
from datetime import datetime as dt
from vfb import ingest

logging.basicConfig()
logging.root.setLevel(logging.INFO)
log = logging.getLogger(__name__)

GET_ALL_TEMPLATES = "https://resource.metadatacenter.org/search?resource_types=template&version=all&publication_status={publication_status}&sort=name&limit=499&sharing={sharing}&mode=null"
LIST_TEMPLATE_INSTANCES = "https://resource.metadatacenter.org/search?version=all&publication_status=all&is_based_on={template}&sort=lastUpdatedOnTS&limit=499&offset={offset}"
GET_TEMPLATE_INSTANCE_DATA = "https://resource.metadatacenter.org/template-instances/{template_instance}?format=jsonld"
GET_ALL_USERS = "https://resource.metadatacenter.org/users"

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
REQUEST_LIMIT = 499


def crawl():
    templates = get_all_templates()
    all_users = get_all_users()
    for template in templates:
        instances = get_template_instances(template)
        for instance in instances:
            instance_data = get_instance_data(instance)
            editor = get_user(all_users, instance_data["oslc:modifiedBy"])
            ingest.ingest_data(editor, instance_data)


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

    # TODO get from neo4j
    last_crawl_str = "2022-01-09T04:09:57-08:00"
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
        get_template_instances(template, template_instances, offset=offset+REQUEST_LIMIT+1, limit=REQUEST_LIMIT)
    log.info('Total {} new template instances found for processing.'.format(len(template_instances)))
    return template_instances


def get_all_templates():
    """
    Lists all published templates that are shared with the "vfb crawler" group.

    return: all published templates that are shared with the "vfb crawler" group.
    """
    log.info('Querying all templates shared with the crawler.')
    sharing = "shared-with-me"
    publication_status = "bibo%3Apublished"
    headers = {'Accept': 'application/json', 'Authorization': os.environ['CEDAR_API_KEY']}
    r = requests.get(GET_ALL_TEMPLATES.format(publication_status=publication_status, sharing=sharing), headers=headers)
    response = r.json()

    templates = set()
    for resource in response["resources"]:
        templates.add(resource["@id"])

    log.info('Total {} templates shared with the crawler'.format(len(templates)))
    return templates
