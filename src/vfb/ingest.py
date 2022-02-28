import logging
from vfb.model import Neuron, NeuronType, Dataset
from vfb.ingest_api_client import get_user_details, post_neuron
from exception.crawler_exception import CrawlerException, TemplateParserException

logging.basicConfig()
logging.root.setLevel(logging.INFO)
log = logging.getLogger(__name__)


ORCID_ID_PREFIX = "https://orcid.org/"


def ingest_data(user, metadata, template_instance):
    log.info("Ingesting: " + str(metadata))

    user_orcid = ORCID_ID_PREFIX + user
    data_obj = parse_template_data(metadata, template_instance)

    if isinstance(data_obj, Neuron):
        vfb_user = get_user_details(user_orcid)
        post_neuron(data_obj, user_orcid, vfb_user["apikey"])


def parse_template_data(metadata, template_instance):
    if "imaging_type" in metadata or "classification" in metadata or "driver_line" in metadata:
        data_obj = Neuron(metadata["primary_name"]["@value"])
        auto_fill_data_obj(data_obj, metadata)

        # handle outlier fields and transformations
        if "dataset_id" in metadata:
            data_obj.set_datasetid(get_metadata_value(metadata["dataset_id"]))
        if "has synaptic terminal in" in metadata:
            data_obj.set_input_neuropils(get_metadata_value(metadata["has synaptic terminal in"]))
        if isinstance(data_obj.part_of, str):
            # part_of is list by default, but ui is only providing single value (gender) now
            data_obj.set_part_of([data_obj.part_of])
        parse_imaging_type(data_obj, template_instance)
    else:
        raise TemplateParserException("Unrecognised template data: " + template_instance)

    return data_obj


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


