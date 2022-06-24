import os
import unittest
import json
from vfb.report import send_email, send_reports, Report, generate_report_content


class ReportingTest(unittest.TestCase):

    # def test_email(self):
    #     reports = [Report("my_template", "my_instance", 'https://orcid.org/0000-0002-3315-2794')]
    #     send_reports(reports)

    def test_report_generation(self):
        reports = list()
        reports.append(Report("template1", "instance1", "my_orcid"))
        reports.append(Report("template2", "instance2", "my_orcid"))
        reports.append(Report("template2", "instance3", "my_orcid"))
        reports.append(Report("template1", "instance4", "my_orcid"))

        error_report1 = Report("template1", "instance5", "my_orcid")
        error_report1.set_error("Error message")
        reports.append(error_report1)
        error_report2 = Report("template1", "instance6", "my_orcid")
        error_report2.set_error("Error message \n multi \n line")
        reports.append(error_report2)

        content = generate_report_content(reports)
        self.assertTrue(content)
        expected_content = ("==== Failed CEDAR Forms \n" 
                            "1- Error occurred while processing: https://cedar.metadatacenter.org/instances/edit/instance5.\n"
                            "	 Cause: Error message\n"
                            "\n"
                            "2- Error occurred while processing: https://cedar.metadatacenter.org/instances/edit/instance6.\n"
                            "	 Cause: Error message \n"
                            " multi \n"
                            " line\n"
                            "\n"
                            "==== Successfully Crawled CEDAR Forms \n"
                            "1- CEDAR form crawled: https://cedar.metadatacenter.org/instances/edit/instance1\n"
                            "2- CEDAR form crawled: https://cedar.metadatacenter.org/instances/edit/instance2\n"
                            "3- CEDAR form crawled: https://cedar.metadatacenter.org/instances/edit/instance3\n"
                            "4- CEDAR form crawled: https://cedar.metadatacenter.org/instances/edit/instance4\n"
                            "")

        self.assertEqual(expected_content, content)



