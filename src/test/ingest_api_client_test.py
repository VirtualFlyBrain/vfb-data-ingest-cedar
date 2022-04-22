import os
import unittest
import json
from vfb.ingest_api_client import get_user_details, post_neuron, post_dataset, download_neuron_image
from vfb.ingest import parse_template_data

from exception.crawler_exception import CrawlerException


current_dir = os.path.dirname(os.path.realpath(__file__))
NEURON_SAMPLE_DATA_1 = os.path.join(current_dir, "./test_data/Baker2020_WED-PN1.json")
NEURON_SAMPLE_DATA_2 = os.path.join(current_dir, "./test_data/Marin2020_57015.json")
NEURON_SAMPLE_DATA_3 = os.path.join(current_dir, "./test_data/Test2022_MBON02.json")
NEURON_SAMPLE_DATA_4 = os.path.join(current_dir, "./test_data/Xu2020_1807191501.json")
NEURON_EXCEPTION_DATA = os.path.join(current_dir, "./test_data/Exception_data.json")
DATASET_1 = os.path.join(current_dir, "./test_data/Dataset1.json")


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

        user_data = get_user_details("https://orcid.org/0000-0002-1373-1705")
        print(user_data)
        self.assertTrue(user_data)
        self.assertEqual("https://orcid.org/0000-0002-1373-1705", user_data["orcid"])
        self.assertEqual("cp390", user_data["primary_name"])
        self.assertTrue("apikey" in user_data)
        self.assertTrue(user_data["apikey"])
        self.assertTrue(str(user_data["apikey"]).startswith("y4d4a89a-"))

    def test_get_user_details_exception(self):
        try:
            get_user_details("not_existing_id")
            self.fail("There should be an exception.")
        except CrawlerException as err:
            self.assertEqual("Error occurred while getting vfb user not_existing_id", err.message)

    def test_post_neuron(self):
        vfb_data = parse_template_data(read_json(NEURON_SAMPLE_DATA_1), "test_template_instance")
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
        self.assertEqual("http://virtualflybrain.org/reports/Zoglu2020", written_data["datasetid"])
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
        vfb_data = parse_template_data(read_json(NEURON_SAMPLE_DATA_2), "test_template_instance")
        status_code, response_data = post_neuron(vfb_data, "https://orcid.org/0000-0002-7356-1779", "xyz")

        self.assertEqual(201, status_code)
        self.assertEqual(1, len(response_data["neurons"]))
        written_data = response_data["neurons"][0]
        self.assertEqual("Multiglomerular mALT lvPN VC5+", written_data["primary_name"])
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00049762", written_data["classification"])
        self.assertEqual("transmission electron microscopy (TEM)", written_data["imaging_type"])
        self.assertEqual(0, len(written_data["driver_line"]))
        self.assertEqual("http://virtualflybrain.org/reports/Zoglu2020", written_data["datasetid"])
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
        vfb_data = parse_template_data(read_json(NEURON_SAMPLE_DATA_3), "test_template_instance")
        status_code, response_data = post_neuron(vfb_data, "https://orcid.org/0000-0002-7356-1779", "xyz")

        self.assertEqual(201, status_code)
        self.assertEqual(1, len(response_data["neurons"]))
        written_data = response_data["neurons"][0]
        self.assertEqual("MBON02", written_data["primary_name"])
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00111012", written_data["classification"])
        self.assertEqual("confocal microscopy", written_data["imaging_type"])
        # self.assertEqual(1, len(written_data["driver_line"]))
        # self.assertEqual("VFBexp_FBtp0099466FBtp0099529", written_data["driver_line"][0])
        self.assertEqual("http://virtualflybrain.org/reports/Zoglu2020", written_data["datasetid"])
        self.assertEqual("VFB_00101567", written_data["template_id"])
        self.assertEqual(1, len(written_data["part_of"]))
        self.assertEqual("FBbt_00007004", written_data["part_of"][0])
        self.assertEqual(3, len(written_data["input_neuropils"]))
        self.assertTrue("FBbt_00013694" in written_data["input_neuropils"])
        self.assertTrue("FBbt_00110658" in written_data["input_neuropils"])
        self.assertTrue("FBbt_00007145" in written_data["input_neuropils"])
        # self.assertEqual(0, len(written_data["alternative_names"]))
        self.assertFalse(written_data["alternative_names"])
        self.assertEqual("comment1", written_data["classification_comment"])
        self.assertEqual("MBON02", written_data["filename"])

    def test_post_neuron4(self):
        vfb_data = parse_template_data(read_json(NEURON_SAMPLE_DATA_4), "test_template_instance")
        status_code, response_data = post_neuron(vfb_data, "https://orcid.org/0000-0002-7356-1779", "xyz")

        self.assertEqual(201, status_code)
        self.assertEqual(1, len(response_data["neurons"]))
        written_data = response_data["neurons"][0]
        self.assertEqual("LLPC3", written_data["primary_name"])
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00003881", written_data["classification"])
        self.assertEqual("serial block face SEM (SBFSEM)", written_data["imaging_type"])
        self.assertEqual(0, len(written_data["driver_line"]))
        self.assertEqual("http://virtualflybrain.org/reports/Zoglu2020", written_data["datasetid"])
        self.assertEqual("VFB_00101384", written_data["template_id"])
        self.assertEqual(1, len(written_data["part_of"]))
        self.assertEqual("FBbt_00007011", written_data["part_of"][0])
        self.assertEqual(2, len(written_data["input_neuropils"]))
        self.assertTrue("FBbt_00003852" in written_data["input_neuropils"])
        self.assertTrue("FBbt_00003885" in written_data["input_neuropils"])
        self.assertEqual(None, written_data["alternative_names"])
        self.assertEqual("", written_data["classification_comment"])
        self.assertEqual("1807191501", written_data["filename"])

    def test_post_neuron_exception(self):
        vfb_data = parse_template_data(read_json(NEURON_EXCEPTION_DATA), "test_template_instance")
        print(vars(vfb_data))
        try:
            status_code, response_data = post_neuron(vfb_data, "https://orcid.org/0000-0002-7356-1779", "xyz")
            print(status_code)
            print(response_data)
            self.fail("En exception should occur.")
        except CrawlerException as err:
            self.assertTrue(str(err.message).startswith("Error occurred while posting neurons of user https://orcid.org/0000-0002-7356-1779"))

    def test_post_neuron_continuous_exception(self):
        # first attempt
        vfb_data = parse_template_data(read_json(NEURON_EXCEPTION_DATA), "test_template_instance")
        print(vars(vfb_data))
        try:
            post_neuron(vfb_data, "https://orcid.org/0000-0002-7356-1779", "xyz")
            self.fail("En exception should occur.")
        except CrawlerException as err:
            self.assertTrue(str(err.message).startswith("Error occurred while posting neurons of user https://orcid.org/0000-0002-7356-1779"))

        # second attempt
        vfb_data = parse_template_data(read_json(NEURON_EXCEPTION_DATA), "test_template_instance")
        print(vars(vfb_data))
        try:
            post_neuron(vfb_data, "https://orcid.org/0000-0002-7356-1779", "xyz")
            self.fail("En exception should occur.")
        except CrawlerException as err:
            self.assertTrue(str(err.message).startswith(
                "Error occurred while posting neurons of user https://orcid.org/0000-0002-7356-1779"))

    def test_post_dataset(self):
        vfb_data = parse_template_data(read_json(DATASET_1), "test_template_instance")
        status_code, response_data = post_dataset(vfb_data, "https://orcid.org/0000-0002-7356-1779", "xyz")

        self.assertEqual(201, status_code)
        self.assertTrue(response_data)
        self.assertEqual("ABCD_ds1", response_data)

    def test_download_neuron_image(self):
        test_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/images/")
        test_url = "https://raw.githubusercontent.com/VirtualFlyBrain/vfb-data-ingest-cedar/main/src/test/test_data/Exception_data.json"

        os.environ["IMAGES_FOLDER_PATH"] = str(test_folder)
        print(os.getenv("IMAGES_FOLDER_PATH"))
        expected_file = os.path.join(test_folder, "Exception_data.json")
        print(str(expected_file))
        if os.path.exists(expected_file):
            os.remove(expected_file)

        self.assertFalse(os.path.isfile(expected_file))
        download_neuron_image(test_url)
        self.assertTrue(os.path.isfile(expected_file))


def read_json(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)
