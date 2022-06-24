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
    def __init__(self, template, template_instance, editor, created_entity=""):
        self.template = template
        self.template_instance = template_instance
        self.editor = editor
        self.is_success = True
        self.error_message = None
        self.created_entity = created_entity

    def set_error(self, message):
        self.is_success = False
        self.error_message = message


class FailureReport:
    def __init__(self, editor, problem_message, unsent_reports):
        self.editor = editor
        self.problem_message = problem_message
        self.unsent_reports = unsent_reports


def send_reports(reports: list) -> List[FailureReport]:
    """
    Groups all reports based on their editor and sends a summary email to the editor. If fail to send the report,
    collects all failures and returns to be sent to the technical support team about the failure.

    Args:
        reports: all crawling result reports
    Returns:
        Failure reports if any of the send operation failed.
    """
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
        if "email" not in user_info or not user_info["email"]:
            log.error("User email doesn't exist in the VFB :" + editor_orcid)
            failed_reports.append(FailureReport(editor_orcid, "User email doesn't exist in the VFB :" + editor_orcid, user_reports[user]))
        else:
            receiver_email = user_info["email"]
            try:
                send_email(sender_email, password, receiver_email, generate_report_content(user_reports[user]))
            except Exception as err:
                log.error("Failed to sent report mail to '{}', cause: {}.".format(receiver_email, str(err)))
                failed_reports.append(
                    FailureReport(editor_orcid, "Failed to sent report mail to '{}', cause: {}.".format(receiver_email,
                                                                                                        str(err)),
                                  user_reports[user]))
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
            success_report += str(success_counter) + "- CEDAR form crawled: " + CEDAR_SITE + \
                              report.template_instance + "\n"
            success_report += "\t- Created entity: " + report.created_entity + "\n"
            success_counter += 1

    message = ""
    if error_report:
        message = """==== Failed CEDAR Forms \n""" + error_report
    if success_report:
        message += """==== Successfully Crawled CEDAR Forms \n""" + success_report

    return message


def generate_failure_report_content(failed_reports: List[FailureReport]):
    message = "The following records could not be send: \n \n"
    for failure in failed_reports:
        message += "\t- '" + failure.editor + "' : " + failure.problem_message + "\n"
        for unsent_report in failure.unsent_reports:
            message += "\t\t- " + "CEDAR form crawled: " + CEDAR_SITE + unsent_report.template_instance + "\n"

        message += "\n"

    return message


def send_failure_message_to_support(failure_message: str):
    sender_email = get_email_user()
    password = get_email_password()
    send_email(sender_email, password, get_tech_suport_email_user(), failure_message, subject="VFB Crawler Error")


def send_failure_report_to_support(failed_reports: list):
    """
    Sends reports that cannot be sent to the related users (for any reason, user don't have email, gmail error etc.) to
    the technical support team
    """
    if failed_reports:
        try:
            sender_email = get_email_user()
            password = get_email_password()
            send_email(sender_email, password, get_tech_suport_email_user(), generate_failure_report_content(failed_reports))
        except Exception as err:
            log.error("Failed to sent failure report mail to the support team '{}', cause: {}.".format(
                get_tech_suport_email_user(), str(err)))


def send_email(sender_email, password, receiver_email, message, subject=REPORT_SUBJECT):
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (sender_email, receiver_email, subject, message)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
    server.close()
    log.info("Successfully send mail to '{}'.".format(receiver_email))


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


def get_tech_suport_email_user():
    if "TECH_SUPPORT_EMAIL" in os.environ:
        return os.getenv("TECH_SUPPORT_EMAIL")
    else:
        raise CrawlerException("Tech support email is not defined in the environment variables. !!!")
