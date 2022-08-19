import logging
from vfb.model import Neuron, SplitDriver, Dataset, Split
from vfb.ingest_api_client import get_user_details, post_neuron, post_dataset, download_neuron_image, post_split, post_ep_split, post_ep_split_flp_out
from exception.crawler_exception import CrawlerException, TemplateParserException

logging.basicConfig()
logging.root.setLevel(logging.INFO)
log = logging.getLogger(__name__)

ORCID_ID_PREFIX = "https://orcid.org/"
PROJECT_IRI_PREFIX = "http://virtualflybrain.org/project/"

# use this submission order if multiple objects arrive
object_ingestion_order = [Dataset, Split, Neuron, SplitDriver]

# map ebi licences to vfb ones
license_mapping = {
    "SWO_1000065": "VFBlicense_CC_BY_4_0",
    "SWO_1000049": "VFBlicense_CC_BY_NC_3_0"
}


def ingest_data(user_orcid, metadata, template_instance, crawling_types):
    """
    Parses the metadata and posts to the VFB API.
    user_orcid: content editor ORCID id
    metadata: content created in the Cedar
    template_instance: content identifier in the Cedar
    crawling_types: Content types that the crawler configured to crawl.
    """
    log.info("Ingesting: " + str(metadata))

    if not str(user_orcid).startswith(ORCID_ID_PREFIX):
        user_orcid = ORCID_ID_PREFIX + user_orcid
    data_obj = parse_template_data(metadata, template_instance)

    results = []
    if data_obj:
        template_conf = get_template_config(metadata)
        if isinstance(data_obj, list):
            # single template may require to ingest multiple objects such as Split and Neuron
            sorted_data_obj = sort_by_ingestion_order(data_obj)
            created_split = None
            for data in sorted_data_obj:
                if created_split and (isinstance(data, Neuron) or isinstance(data, SplitDriver)):
                    data.set_driver_line([str(created_split)])
                response = ingest_data_obj(user_orcid, metadata, template_instance, crawling_types, data, template_conf)
                if isinstance(data, Split):
                    created_split = response["short_form"]
                if response:
                    results.append(response)
        else:
            response = ingest_data_obj(user_orcid, metadata, template_instance, crawling_types, data_obj, template_conf)
            if response:
                results.append(response)

    return results


def sort_by_ingestion_order(data_obj):
    """
    Considers data dependencies and sorts objects by ingestion order.
    """
    type_index = [object_ingestion_order.index(type(x)) for x in data_obj]
    sorted_data_obj = [x for _, x in sorted(zip(type_index, data_obj))]
    return sorted_data_obj


def ingest_data_obj(user_orcid, metadata, template_instance, crawling_types, data_obj, template_conf):
    result = None
    if data_obj and type(data_obj).__name__ in crawling_types:
        if isinstance(data_obj, Neuron):
            if template_conf["EP_fragment"]:
                if template_conf["single_neuron"]:
                    result = post_neuron(data_obj, user_orcid, get_user_details(user_orcid)["apikey"])
                else:
                    result = post_ep_split_flp_out(data_obj, user_orcid, get_user_details(user_orcid)["apikey"])
            else:
                result = post_ep_split(data_obj, user_orcid, get_user_details(user_orcid)["apikey"])
            download_neuron_image(metadata["image_location"]["@value"], metadata["dataset_id"]["@value"])
        elif isinstance(data_obj, Dataset):
            result = post_dataset(data_obj, user_orcid, get_user_details(user_orcid)["apikey"])
        elif isinstance(data_obj, Split):
            result = post_split(data_obj, user_orcid, get_user_details(user_orcid)["apikey"])
    else:
        log.warning("Skipping ingestion of the template instance {}({}) of user {}".format(
            template_instance, str(type(data_obj).__name__), user_orcid))
    return result


def parse_template_data(metadata, template_instance):
    if "imaging_type" in metadata or "classification" in metadata or "split_combo" in metadata:
        if not is_neuron_published(metadata):
            return None

        template_conf = get_template_config(metadata)
        if template_conf["EP_fragment"]:
            if template_conf["single_neuron"]:
                neuron_data = Neuron(metadata["primary_name"]["@value"])
            else:
                neuron_data = SplitDriver(metadata["primary_name"]["@value"])
        else:
            neuron_data = SplitDriver(metadata["primary_name"]["@value"])

        split_data = None
        if "hemidriver_1" in metadata and "hemidriver_2" in metadata:
            if get_metadata_value(metadata["hemidriver_1"]) and get_metadata_value(metadata["hemidriver_2"]):
                split_data = Split(str(get_metadata_value(metadata["hemidriver_1"])),
                                   str(get_metadata_value(metadata["hemidriver_2"])))

        auto_fill_data_obj(neuron_data, metadata)

        # handle outlier fields and transformations
        if "dataset_id" in metadata:
            neuron_data.set_datasetid(get_metadata_value(metadata["dataset_id"]))
        if "has synaptic terminal in" in metadata:
            neuron_data.set_input_neuropils(get_metadata_value(metadata["has synaptic terminal in"]))
        if isinstance(neuron_data.part_of, str):
            # part_of is list by default, but ui is only providing single value (gender) now
            neuron_data.set_part_of([neuron_data.part_of])
        if "split_combo" in metadata:
            # TODO driverline entities are not in the kb so save as classification comment for now
            neuron_data.set_comment(str(get_metadata_value(metadata["split_combo"])))
            neuron_data.set_driver_line([])
        parse_imaging_type(neuron_data, template_instance)

        if split_data:
            data_obj = list()
            data_obj.append(split_data)
            data_obj.append(neuron_data)
        else:
            data_obj = neuron_data
    elif "licence" in metadata:
        data_obj = Dataset("", metadata["short_name"]["@value"], metadata["title"]["@value"])
        auto_fill_data_obj(data_obj, metadata)

        # handle outlier fields and transformations
        if "licence" in metadata:
            selected_licence = get_metadata_value(metadata["licence"])
            if selected_licence in license_mapping:
                data_obj.set_license(license_mapping[selected_licence])
        if "projectid" in metadata:
            project_iri = get_metadata_value(metadata["projectid"])
            if not str(get_metadata_value(metadata["projectid"])).startswith(PROJECT_IRI_PREFIX):
                project_iri = PROJECT_IRI_PREFIX + project_iri
            data_obj.set_project_id(project_iri)
    else:
        raise TemplateParserException("Unrecognised template data: " + template_instance)

    return data_obj


def get_template_config(metadata):
    """
    Template instances are not bare data objects, they also contain configuration related properties that drive the
    business logic. Extracts these configurations before parsing rest of the data.
    Args:
        metadata: template instance content
    Returns:
        template configuration dict
    """
    config = dict()
    if "imaging_type" in metadata or "classification" in metadata or "split_combo" in metadata:
        if get_metadata_value(metadata["EP_fragment"]) == "Yes":
            config["EP_fragment"] = True
        else:
            config["EP_fragment"] = False
        if get_metadata_value(metadata["single_neuron"]) == "Yes":
            config["single_neuron"] = True
        else:
            config["single_neuron"] = False
    return config


def parse_imaging_type(data_obj, template_instance):
    # VFB_neo4 KB_tools requires string values, transform them
    imaging_type_lookup = {
        'FBbi_00000224': 'computer graphic',
        'VFBext_0000014': 'channel',
        'FBbi_00000251': 'confocal microscopy',
        'FBbi_00000585': 'SB-SEM',
        'FBbi_00050000': 'SB-SEM',
        'FBbi_00000258': 'TEM'
    }
    if data_obj.imaging_type:
        if data_obj.imaging_type in imaging_type_lookup:
            data_obj.set_imaging_type(imaging_type_lookup[data_obj.imaging_type])
        else:
            raise TemplateParserException("Unsupported imaging type '{imaging_type}' in the template: "
                                          "{template_instance}".format(imaging_type=data_obj.imaging_type,
                                                                       template_instance=template_instance))


def is_neuron_published(metadata):
    """
    Determines if neuron type is published. If not published "publish" field value is None.
    return: Value of the "publish" field
    """
    if "publish" in metadata:
        return get_metadata_value(metadata["publish"])
    else:
        return None


def auto_fill_data_obj(data_obj, metadata):
    for prop, value in vars(data_obj).items():
        setter_function = getattr(data_obj, "set_" + prop, None)
        if callable(setter_function):
            value = None
            if prop in metadata:
                value = get_metadata_value(metadata[prop])
            elif prop.replace("_", " ") in metadata:
                value = get_metadata_value(metadata[prop.replace("_", " ")])
            # else:
            #     print("Property '" + prop + "' does not exist in the metadata of template " + str(type(data_obj)))
            if value:
                setter_function(value)


def get_metadata_value(metadata_prop):
    if isinstance(metadata_prop, list):
        value = list()
        for item in metadata_prop:
            item_value = get_metadata_obj_value(item)
            if item_value:
                value.append(item_value)
    else:
        value = get_metadata_obj_value(metadata_prop)
    return value


def get_metadata_obj_value(metadata_prop):
    if "@id" in metadata_prop:
        entity_id = metadata_prop["@id"]
        value = str(entity_id).split("/")[-1]
    elif "@value" in metadata_prop:
        value = metadata_prop["@value"]
    else:
        value = None
    return value


