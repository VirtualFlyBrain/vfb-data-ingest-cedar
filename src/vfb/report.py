import os
import smtplib
import logging
from typing import List

from exception.crawler_exception import CrawlerException
from vfb.ingest_api_client import get_user_details

REPORT_SUBJECT = "VFB data ingestion report"
ORCID_ID_PREFIX = "https://orcid.org/"
CEDAR_SITE = "https://cedar.metadatacenter.org/instances/edit/"

logging.basicConfig()
logging.root.setLevel(logging.INFO)
log = logging.getLogger(__name__)


class Report:
    def __init__(self, template, template_instance, editor):
        self.template = template
        self.template_instance = template_instance
        self.editor = editor
        self.is_success = True
        self.error_message = None

    def set_error(self, message):
        self.is_success = False
        self.error_message = message


def send_reports(reports: list):
    sender_email = get_email_user()
    password = get_email_password()

    user_reports = dict()
    for report in reports:
        if report.editor in user_reports:
            user_reports[report.editor].append(report)
        else:
            user_reports[report.editor] = [report]

    failed_reports = list()
    for user in user_reports:
        editor_orcid = user
        if not str(editor_orcid).startswith(ORCID_ID_PREFIX):
            editor_orcid = ORCID_ID_PREFIX + editor_orcid
        user_info = get_user_details(editor_orcid)
        if "email" not in user_info:
            failed_reports.append("User email doesn't exist in the VFB :" + editor_orcid)
        receiver_email = user_info["email"]
        send_email(sender_email, password, receiver_email, generate_report_content(user_reports[user]))

    return failed_reports


def generate_report_content(user_reports: List[Report]):
    success_report = ""
    error_report = ""
    error_counter = 1
    success_counter = 1
    for report in user_reports:
        if report.error_message:
            error_report += str(error_counter) + "- Error occurred while processing: " + CEDAR_SITE + \
                            report.template_instance + ".\n"
            error_report += "\t Cause: " + report.error_message + "\n\n"
            error_counter += 1
        else:
            success_report += str(success_counter) + "- Template instance crawled: " + CEDAR_SITE + \
                              report.template_instance + "\n"
            success_counter += 1

    message = ""
    if error_report:
        message = """==== Failed Template Instances \n""" + error_report
    if success_report:
        message += """==== Successfully Crawled Template Instances \n""" + success_report

    return message


def send_email(sender_email, password, receiver_email, message):
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (sender_email, receiver_email, REPORT_SUBJECT, message)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
        server.close()
        log.info("Successfully sent report mail to '{}'.".format(receiver_email))
    except Exception as err:
        log.error("Failed to sent report mail to '{}', cause: {}.".format(receiver_email, str(err)))
        raise CrawlerException("Failed to sent report mail to '{}', cause: {}.".format(receiver_email, str(err)))


def get_email_password():
    if "VFBCRAWLER_EMAIL_PASS" in os.environ:
        return os.getenv("VFBCRAWLER_EMAIL_PASS")
    else:
        raise CrawlerException("vfbcrawler email password is not defined in the environment variables. !!!")


def get_email_user():
    if "VFBCRAWLER_EMAIL_USER" in os.environ:
        return os.getenv("VFBCRAWLER_EMAIL_USER")
    else:
        raise CrawlerException("vfbcrawler email user is not defined in the environment variables. !!!")
