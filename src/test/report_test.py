import os
import unittest
import json
from vfb.report import send_email, send_reports, Report


class ReportingTest(unittest.TestCase):

    def test_reports(self):
        reports = [Report("my_template", "my_instance", 'https://orcid.org/0000-0002-3315-2794')]
        send_reports(reports)

