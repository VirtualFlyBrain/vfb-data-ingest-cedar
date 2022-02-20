import os
import unittest
import json
from vfb.ingest_api_client import get_user_details, post_neuron
from vfb.ingest import parse_template_data


current_dir = os.path.dirname(os.path.realpath(__file__))
SAMPLE_DATA_1 = os.path.join(current_dir, "./test_data/Baker2020_WED-PN1.json")
SAMPLE_DATA_2 = os.path.join(current_dir, "./test_data/Marin2020_57015.json")
SAMPLE_DATA_3 = os.path.join(current_dir, "./test_data/Test2022_MBON02.json")
SAMPLE_DATA_4 = os.path.join(current_dir, "./test_data/Xu2020_1807191501.json")


class IngestApiTest(unittest.TestCase):

    def test_get_user_details(self):
        user_data = get_user_details("https://orcid.org/0000-0002-7356-1779")
        print(user_data)
        self.assertTrue(user_data)
        self.assertEqual("https://orcid.org/0000-0002-7356-1779", user_data["orcid"])
        self.assertEqual("Nico", user_data["primary_name"])
        self.assertTrue("apikey" in user_data)
        self.assertTrue(user_data["apikey"])
        self.assertEqual("xyz", user_data["apikey"])

    def test_post_neuron(self):
        vfb_data = parse_template_data(read_json(SAMPLE_DATA_1), "test_template_instance")
        # post_neuron(vfb_data, "https://orcid.org/0000-0002-3315-2794",
        #             get_user_details("https://orcid.org/0000-0002-3315-2794")["apikey"])
        status_code, response_data = post_neuron(vfb_data, "https://orcid.org/0000-0002-7356-1779", "xyz")

        self.assertEqual(201, status_code)
        self.assertEqual(1, len(response_data["neurons"]))
        written_data = response_data["neurons"][0]
        self.assertEqual("WED-PN1", written_data["primary_name"])
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00049454", written_data["classification"])
        self.assertEqual("confocal microscopy", written_data["imaging_type"])
        self.assertEqual(0, len(written_data["driver_line"]))
        self.assertEqual("http://virtualflybrain.org/data/Zoglu2020", written_data["datasetid"])
        self.assertEqual("VFB_00101567", written_data["template_id"])
        self.assertEqual(1, len(written_data["part_of"]))
        self.assertEqual("FBbt_00007011", written_data["part_of"][0])
        self.assertEqual(1, len(written_data["input_neuropils"]))
        self.assertTrue("FBbt_00045027" in written_data["input_neuropils"])
        self.assertEqual(1, len(written_data["alternative_names"]))
        self.assertEqual("IPS_pr01", written_data["alternative_names"][0])
        self.assertEqual("", written_data["classification_comment"])
        self.assertEqual(None, written_data["filename"])

    def test_post_neuron2(self):
        vfb_data = parse_template_data(read_json(SAMPLE_DATA_2), "test_template_instance")
        status_code, response_data = post_neuron(vfb_data, "https://orcid.org/0000-0002-7356-1779", "xyz")

        self.assertEqual(201, status_code)
        self.assertEqual(1, len(response_data["neurons"]))
        written_data = response_data["neurons"][0]
        self.assertEqual("Multiglomerular mALT lvPN VC5+", written_data["primary_name"])
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00049762", written_data["classification"])
        self.assertEqual("transmission electron microscopy (TEM)", written_data["imaging_type"])
        self.assertEqual(0, len(written_data["driver_line"]))
        self.assertEqual("http://virtualflybrain.org/data/Zoglu2020", written_data["datasetid"])
        self.assertEqual("VFB_00101567", written_data["template_id"])
        self.assertEqual(1, len(written_data["part_of"]))
        self.assertEqual("FBbt_00007011", written_data["part_of"][0])
        self.assertEqual(2, len(written_data["input_neuropils"]))
        self.assertTrue("FBbt_00110029" in written_data["input_neuropils"])
        self.assertTrue("FBbt_00007053" in written_data["input_neuropils"])
        self.assertEqual(2, len(written_data["alternative_names"]))
        self.assertEqual("VC5+ lvPN2#1", written_data["alternative_names"][0])
        self.assertEqual("Multiglomerular mALT lvPN#R18", written_data["alternative_names"][1])
        self.assertEqual("VC5 renamed to VM6", written_data["classification_comment"])
        self.assertEqual("57015", written_data["filename"])

    def test_post_neuron3(self):
        vfb_data = parse_template_data(read_json(SAMPLE_DATA_3), "test_template_instance")
        status_code, response_data = post_neuron(vfb_data, "https://orcid.org/0000-0002-7356-1779", "xyz")

        self.assertEqual(201, status_code)
        self.assertEqual(1, len(response_data["neurons"]))
        written_data = response_data["neurons"][0]
        self.assertEqual("MBON02", written_data["primary_name"])
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00111012", written_data["classification"])
        self.assertEqual("confocal microscopy", written_data["imaging_type"])
        self.assertEqual(1, len(written_data["driver_line"]))
        self.assertEqual("VFBexp_FBtp0099466FBtp0099529", written_data["driver_line"][0])
        self.assertEqual("http://virtualflybrain.org/data/Zoglu2020", written_data["datasetid"])
        self.assertEqual("VFB_00101567", written_data["template_id"])
        self.assertEqual(1, len(written_data["part_of"]))
        self.assertEqual("FBbt_00007004", written_data["part_of"][0])
        self.assertEqual(3, len(written_data["input_neuropils"]))
        self.assertTrue("FBbt_00013694" in written_data["input_neuropils"])
        self.assertTrue("FBbt_00110658" in written_data["input_neuropils"])
        self.assertTrue("FBbt_00007145" in written_data["input_neuropils"])
        self.assertEqual(0, len(written_data["alternative_names"]))
        self.assertEqual("", written_data["classification_comment"])
        self.assertEqual("MBON02", written_data["filename"])

    def test_post_neuron4(self):
        vfb_data = parse_template_data(read_json(SAMPLE_DATA_4), "test_template_instance")
        status_code, response_data = post_neuron(vfb_data, "https://orcid.org/0000-0002-7356-1779", "xyz")

        self.assertEqual(201, status_code)
        self.assertEqual(1, len(response_data["neurons"]))
        written_data = response_data["neurons"][0]
        self.assertEqual("LLPC3", written_data["primary_name"])
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00003881", written_data["classification"])
        self.assertEqual("serial block face SEM (SBFSEM)", written_data["imaging_type"])
        self.assertEqual(0, len(written_data["driver_line"]))
        self.assertEqual("http://virtualflybrain.org/data/Zoglu2020", written_data["datasetid"])
        self.assertEqual("VFB_00101384", written_data["template_id"])
        self.assertEqual(1, len(written_data["part_of"]))
        self.assertEqual("FBbt_00007011", written_data["part_of"][0])
        self.assertEqual(2, len(written_data["input_neuropils"]))
        self.assertTrue("FBbt_00003852" in written_data["input_neuropils"])
        self.assertTrue("FBbt_00003885" in written_data["input_neuropils"])
        self.assertEqual(None, written_data["alternative_names"])
        self.assertEqual("", written_data["classification_comment"])
        self.assertEqual("1807191501", written_data["filename"])


def read_json(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)
