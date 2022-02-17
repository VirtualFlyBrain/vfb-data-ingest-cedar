import os
import unittest
import json
from vfb.ingest_api_client import get_user_details, post_neuron
from vfb.ingest import parse_template_data


class IngestApiTest(unittest.TestCase):

    def test_get_user_details(self):
        user_data = get_user_details("https://orcid.org/0000-0002-3315-2794")
        print(user_data)
        self.assertEqual("https://orcid.org/0000-0002-3315-2794", user_data["orcid"])
        self.assertEqual("hkir", user_data["primary_name"])
        self.assertTrue("apikey" in user_data)
        self.assertTrue(user_data["apikey"])

    def test_post_neuron(self):
        sample_json = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/Marin2020_57015_2.json")
        vfb_data = parse_template_data(read_json(sample_json))
        # post_neuron(vfb_data, "https://orcid.org/0000-0002-3315-2794",
        #             get_user_details("https://orcid.org/0000-0002-3315-2794")["apikey"])
        post_neuron(vfb_data, "https://orcid.org/0000-0002-7356-1779", "xyz")


def read_json(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)
