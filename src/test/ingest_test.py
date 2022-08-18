import os
import unittest
import json
from vfb.ingest import parse_template_data, sort_by_ingestion_order
from vfb.model import Neuron, SplitDriver, Dataset, Split

current_dir = os.path.dirname(os.path.realpath(__file__))
SAMPLE_DATA_1 = os.path.join(current_dir, "./test_data/Baker2020_WED-PN1.json")
SAMPLE_DATA_2 = os.path.join(current_dir, "./test_data/Marin2020_57015.json")
SAMPLE_DATA_3 = os.path.join(current_dir, "./test_data/Test2022_MBON02.json")
SAMPLE_DATA_4 = os.path.join(current_dir, "./test_data/Xu2020_1807191501.json")
SAMPLE_DATA_5 = os.path.join(current_dir, "./test_data/neuron_not_publish.json")
DATASET_1 = os.path.join(current_dir, "./test_data/Dataset1.json")


class IngestTest(unittest.TestCase):

    def test_ingest_data_1(self):
        vfb_data = parse_template_data(read_json(SAMPLE_DATA_1), "test_template_instance")
        self.assertEqual(type(vfb_data), Neuron)

        print(vfb_data)
        self.assertEqual("WED-PN1", vfb_data.primary_name)
        self.assertEqual(1, len(vfb_data.classification))
        self.assertTrue("FBbt_00049454" in vfb_data.classification)
        self.assertEqual("confocal microscopy", vfb_data.imaging_type)
        self.assertEqual(0, len(vfb_data.driver_line))
        self.assertEqual("Zoglu2020", vfb_data.datasetid)
        self.assertEqual("VFB_00101567", vfb_data.template_id)
        self.assertEqual(1, len(vfb_data.part_of))
        self.assertEqual("FBbt_00007011", vfb_data.part_of[0])
        self.assertEqual(1, len(vfb_data.input_neuropils))
        self.assertEqual("FBbt_00045027", vfb_data.input_neuropils[0])
        self.assertEqual(1, len(vfb_data.alternative_names))
        self.assertEqual("IPS_pr01", vfb_data.alternative_names[0])
        self.assertEqual("", vfb_data.classification_comment)
        self.assertEqual("", vfb_data.filename)
        self.assertEqual("['VFBexp_FBti0205553FBti0205557']", vfb_data.comment)

    def test_ingest_data_2(self):
        vfb_data = parse_template_data(read_json(SAMPLE_DATA_2), "test_template_instance")

        self.assertEqual(type(vfb_data), list)
        self.assertEqual(type(vfb_data[0]), Split)
        self.assertEqual(type(vfb_data[1]), Neuron)

        split = vfb_data[0]
        neuron = vfb_data[1]
        print(neuron)
        self.assertEqual("Multiglomerular mALT lvPN VC5+", neuron.primary_name)
        self.assertEqual(1, len(neuron.classification))
        self.assertTrue("FBbt_00049762" in neuron.classification)
        self.assertEqual("TEM", neuron.imaging_type)
        self.assertEqual("Zoglu2020", neuron.datasetid)
        self.assertEqual("VFB_00101567", neuron.template_id)
        self.assertEqual(1, len(neuron.part_of))
        self.assertEqual("FBbt_00007011", neuron.part_of[0])
        self.assertEqual(2, len(neuron.input_neuropils))
        self.assertEqual("FBbt_00110029", neuron.input_neuropils[0])
        self.assertEqual("FBbt_00007053", neuron.input_neuropils[1])
        self.assertEqual(2, len(neuron.alternative_names))
        self.assertEqual("VC5+ lvPN2#1", neuron.alternative_names[0])
        self.assertEqual("Multiglomerular mALT lvPN#R18", neuron.alternative_names[1])
        self.assertEqual("VC5 renamed to VM6", neuron.classification_comment)
        self.assertEqual("57015", neuron.filename)
        self.assertEqual("[]", neuron.comment)

        self.assertEqual("FBti0001774", split.dbd)
        self.assertEqual("FBti0001776", split.ad)

    def test_ingest_data_3(self):
        vfb_data = parse_template_data(read_json(SAMPLE_DATA_3), "test_template_instance")

        self.assertEqual(type(vfb_data), list)
        self.assertEqual(type(vfb_data[0]), Split)
        self.assertEqual(type(vfb_data[1]), SplitDriver)

        split = vfb_data[0]
        neuron = vfb_data[1]
        print(neuron)
        self.assertEqual("MBON02", neuron.primary_name)
        self.assertEqual(1, len(neuron.classification))
        self.assertTrue("FBbt_00111012" in neuron.classification)
        self.assertEqual("confocal microscopy", neuron.imaging_type)
        # self.assertEqual(1, len(neuron.driver_line))
        # self.assertEqual("VFBexp_FBtp0099466FBtp0099529", neuron.driver_line[0])
        self.assertEqual("Zoglu2020", neuron.datasetid)
        self.assertEqual("VFB_00101567", neuron.template_id)
        self.assertEqual(1, len(neuron.part_of))
        self.assertEqual("FBbt_00007004", neuron.part_of[0])
        self.assertEqual(3, len(neuron.input_neuropils))
        self.assertEqual("FBbt_00013694", neuron.input_neuropils[0])
        self.assertEqual("FBbt_00110658", neuron.input_neuropils[1])
        self.assertEqual("FBbt_00007145", neuron.input_neuropils[2])
        self.assertEqual(0, len(neuron.alternative_names))
        self.assertEqual("comment1", neuron.classification_comment)
        self.assertEqual("MBON02", neuron.filename)
        self.assertEqual("[]", neuron.comment)

        self.assertEqual("FBti0001774", split.dbd)
        self.assertEqual("FBti0001776", split.ad)

    def test_ingest_data_4(self):
        vfb_data = parse_template_data(read_json(SAMPLE_DATA_4), "test_template_instance")

        self.assertEqual(type(vfb_data), SplitDriver)
        neuron = vfb_data
        self.assertEqual("LLPC3", neuron.primary_name)
        self.assertEqual(1, len(neuron.classification))
        self.assertTrue("FBbt_00003881" in neuron.classification)
        self.assertEqual("SB-SEM", neuron.imaging_type)
        self.assertEqual(0, len(neuron.driver_line))
        self.assertEqual("Zoglu2020", neuron.datasetid)
        self.assertEqual("VFB_00101384", neuron.template_id)
        self.assertEqual(1, len(neuron.part_of))
        self.assertEqual("FBbt_00007011", neuron.part_of[0])
        self.assertEqual(2, len(neuron.input_neuropils))
        self.assertEqual("FBbt_00003852", neuron.input_neuropils[0])
        self.assertEqual("FBbt_00003885", neuron.input_neuropils[1])
        self.assertEqual(0, len(neuron.alternative_names))
        self.assertEqual("", neuron.classification_comment)
        self.assertEqual("1807191501", neuron.filename)
        self.assertEqual("['VFBexp_FBti0001774FBti0001776']", neuron.comment)

    def test_ingest_data_5(self):
        vfb_data = parse_template_data(read_json(SAMPLE_DATA_5), "test_template_instance")

        print(vfb_data)
        self.assertFalse(vfb_data)

    def test_ingest_dataset_1(self):
        vfb_data = parse_template_data(read_json(DATASET_1), "test_template_instance")

        self.assertEqual("ABCD_ds1", vfb_data.short_name)
        self.assertEqual("http://virtualflybrain.org/project/ABCD", vfb_data.projectid)
        self.assertEqual("ABCD Dataset1", vfb_data.title)
        self.assertEqual("ABCD Dataset1 description", vfb_data.description)
        self.assertEqual("https://doi.org/10.1093/mind/LIX.236.433", vfb_data.publication)
        self.assertEqual("VFBlicense_CC_BY_4_0", vfb_data.license)
        self.assertEqual("", vfb_data.source_data)

    def test_ingestion_order_sorting(self):
        neuron = Neuron("n1")
        split = Split("", "")
        dataset = Dataset("d1", "xx", "yy")
        split_driver = SplitDriver("sd1")
        self.assertEqual([split, neuron], sort_by_ingestion_order([neuron, split]))
        self.assertEqual([dataset, split, neuron], sort_by_ingestion_order([neuron, split, dataset]))
        self.assertEqual([dataset, split, neuron, split_driver], sort_by_ingestion_order([neuron, split, split_driver, dataset]))


def read_json(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)
