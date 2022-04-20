import os
import unittest
import json
from cedar.crawler import get_user_orcid


class CedarClientTest(unittest.TestCase):

    def test_get_user_orcid_id(self):
        # orcid_id = get_user_orcid("c25e2e67-e444-422f-bcbe-81c4ee7e75cb")
        # hk
        orcid_id = get_user_orcid("6d8029e2-68a3-4230-8393-cc457bf29d97")
        self.assertEqual("0000-0002-3315-2794", orcid_id)

        # cp
        orcid_id = get_user_orcid("7010fb1a-fe13-4e55-a848-7daa2beb849f")
        self.assertEqual("0000-0002-1373-1705", orcid_id)
