import logging
from vfb.model import Neuron, NeuronType, Dataset

logging.basicConfig()
logging.root.setLevel(logging.INFO)
log = logging.getLogger(__name__)


def ingest_data(user, metadata):
    print(user)
    print(metadata)
    ingest_template_data(metadata)
    return None


def ingest_template_data(metadata):
    if "imaging_type" in metadata or "classification" in metadata or "driver_line" in metadata:
        data_obj = Neuron(metadata["primary_name"]["@value"])
        auto_fill_data_obj(data_obj, metadata)

        # naming outliers
        if "dataset_id" in metadata:
            data_obj.set_datasetid(get_metadata_value(metadata["dataset_id"]))
        if "has synaptic terminal in" in metadata:
            data_obj.set_input_neuropils(get_metadata_value(metadata["has synaptic terminal in"]))
    else:
        raise ValueError("Unrecognised template data: " + metadata)

    return data_obj


def auto_fill_data_obj(data_obj, metadata):
    for prop, value in vars(data_obj).items():
        setter_function = getattr(data_obj, "set_" + prop, None)
        if callable(setter_function):
            if prop in metadata:
                setter_function(get_metadata_value(metadata[prop]))
            elif prop.replace("_", " ") in metadata:
                setter_function(get_metadata_value(metadata[prop.replace("_", " ")]))
            else:
                print("Property '" + prop + "' does not exist in the metadata of template " + str(type(data_obj)))


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
        value = metadata_prop["@id"]
    elif "@value" in metadata_prop:
        value = metadata_prop["@value"]
    else:
        value = None
    return value


