import os
import unittest
import json
from vfb.ingest import ingest_template_data

current_dir = os.path.dirname(os.path.realpath(__file__))
SAMPLE_DATA_1 = os.path.join(current_dir, "./test_data/Baker2020_WED-PN1.json")
SAMPLE_DATA_2 = os.path.join(current_dir, "./test_data/Marin2020_57015.json")
SAMPLE_DATA_3 = os.path.join(current_dir, "./test_data/Test2022_MBON02.json")
SAMPLE_DATA_4 = os.path.join(current_dir, "./test_data/Xu2020_1807191501.json")


class IngestTest(unittest.TestCase):

    def test_ingest_data_1(self):
        vfb_data = ingest_template_data(read_json(SAMPLE_DATA_1))

        print(vfb_data)
        self.assertEqual("WED-PN1", vfb_data.primary_name)
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00049454", vfb_data.classification)
        self.assertEqual("http://purl.obolibrary.org/obo/FBbi_00000251", vfb_data.imaging_type)
        self.assertEqual(0, len(vfb_data.driver_line))
        self.assertEqual(None, vfb_data.datasetid)
        self.assertEqual(None, vfb_data.template_id)
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00007011", vfb_data.part_of)
        self.assertEqual(1, len(vfb_data.input_neuropils))
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00045027", vfb_data.input_neuropils[0])
        self.assertEqual(1, len(vfb_data.alternative_names))
        self.assertEqual("IPS_pr01", vfb_data.alternative_names[0])
        self.assertEqual(None, vfb_data.classification_comment)
        self.assertEqual(None, vfb_data.filename)

    def test_ingest_data_2(self):
        vfb_data = ingest_template_data(read_json(SAMPLE_DATA_2))

        print(vfb_data)
        self.assertEqual("Multiglomerular mALT lvPN VC5+", vfb_data.primary_name)
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00049762", vfb_data.classification)
        self.assertEqual("http://purl.obolibrary.org/obo/FBbi_00000258", vfb_data.imaging_type)
        self.assertEqual(0, len(vfb_data.driver_line))
        self.assertEqual("Marin2020", vfb_data.datasetid)
        self.assertEqual("http://virtualflybrain.org/reports/VFB_00101567", vfb_data.template_id)
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00007011", vfb_data.part_of)
        self.assertEqual(2, len(vfb_data.input_neuropils))
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00110029", vfb_data.input_neuropils[0])
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00007053", vfb_data.input_neuropils[1])
        self.assertEqual(2, len(vfb_data.alternative_names))
        self.assertEqual("VC5+ lvPN2#1", vfb_data.alternative_names[0])
        self.assertEqual("Multiglomerular mALT lvPN#R18", vfb_data.alternative_names[1])
        self.assertEqual("VC5 renamed to VM6", vfb_data.classification_comment)
        self.assertEqual("57015", vfb_data.filename)

    def test_ingest_data_3(self):
        vfb_data = ingest_template_data(read_json(SAMPLE_DATA_3))

        print(vfb_data)
        self.assertEqual("MBON02", vfb_data.primary_name)
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00111012", vfb_data.classification)
        self.assertEqual("http://purl.obolibrary.org/obo/FBbi_00000251", vfb_data.imaging_type)
        self.assertEqual(1, len(vfb_data.driver_line))
        self.assertEqual("http://virtualflybrain.org/reports/VFBexp_FBtp0099466FBtp0099529", vfb_data.driver_line[0])
        self.assertEqual("Test2022", vfb_data.datasetid)
        self.assertEqual(None, vfb_data.template_id)
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00007004", vfb_data.part_of)
        self.assertEqual(3, len(vfb_data.input_neuropils))
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00013694", vfb_data.input_neuropils[0])
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00110658", vfb_data.input_neuropils[1])
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00007145", vfb_data.input_neuropils[2])
        self.assertEqual(0, len(vfb_data.alternative_names))
        self.assertEqual(None, vfb_data.classification_comment)
        self.assertEqual("MBON02", vfb_data.filename)

    def test_ingest_data_4(self):
        vfb_data = ingest_template_data(read_json(SAMPLE_DATA_4))

        print(vfb_data)
        self.assertEqual("LLPC3", vfb_data.primary_name)
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00003881", vfb_data.classification)
        self.assertEqual("http://purl.obolibrary.org/obo/FBbi_00050000", vfb_data.imaging_type)
        self.assertEqual(0, len(vfb_data.driver_line))
        self.assertEqual("Xu2020", vfb_data.datasetid)
        self.assertEqual("http://virtualflybrain.org/reports/VFB_00101384", vfb_data.template_id)
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00007011", vfb_data.part_of)
        self.assertEqual(2, len(vfb_data.input_neuropils))
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00003852", vfb_data.input_neuropils[0])
        self.assertEqual("http://purl.obolibrary.org/obo/FBbt_00003885", vfb_data.input_neuropils[1])
        self.assertEqual(0, len(vfb_data.alternative_names))
        self.assertEqual("", vfb_data.classification_comment)
        self.assertEqual("1807191501", vfb_data.filename)


def read_json(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)