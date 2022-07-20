import os
import smtplib
import logging
import json
from typing import List

from exception.crawler_exception import CrawlerException, TechnicalException, ContentException
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
        self.error_type = None
        self.created_entity = created_entity

    def set_error(self, message):
        self.is_success = False
        self.error_message = message

    def set_error_type(self, error_type):
        self.is_success = False
        self.error_type = error_type


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
    sender_email = get_crawler_email()
    password = get_crawler_email_password()

    user_reports = dict()
    for report in reports:
        if report.editor in user_reports:
            user_reports[report.editor].append(report)
        else:
            user_reports[report.editor] = [report]

    failed_reports = send_user_reports(password, sender_email, user_reports)
    send_failure_reports(sender_email, password, reports, type(TechnicalException).__name__, get_tech_support_emails())
    send_failure_reports(sender_email, password, reports, type(ContentException).__name__, get_editor_support_emails())
    return failed_reports


def send_user_reports(password, sender_email, user_reports):
    """
    Sends crawling results to the users.
    Args:
        password: mail sender password
        sender_email: mail sender email
        user_reports: crawling reports aggregated per user
    Returns:
        Failure reports if any of the send operation failed.
    """
    failed_reports = list()
    for user in user_reports:
        user_orcid = user
        if not str(user_orcid).startswith(ORCID_ID_PREFIX):
            user_orcid = ORCID_ID_PREFIX + user_orcid
        user_info = get_user_details(user_orcid)
        if "email" not in user_info or not user_info["email"]:
            log.error("User email doesn't exist in the VFB :" + user_orcid)
            failed_reports.append(
                FailureReport(user_orcid, "User email doesn't exist in the VFB :" + user_orcid, user_reports[user]))
        else:
            receiver_email = user_info["email"]
            try:
                send_email(sender_email, password, receiver_email, generate_report_content(user_reports[user]))
            except Exception as err:
                log.error("Failed to sent report mail to '{}', cause: {}.".format(receiver_email, str(err)))
                failed_reports.append(
                    FailureReport(user_orcid, "Failed to sent report mail to '{}', cause: {}.".format(receiver_email,
                                                                                                      str(err)),
                                  user_reports[user]))
    return failed_reports


def send_failure_reports(sender_email, password, reports, error_type, recipients):
    """
    Sends crawling results failed due to given error type to the tech team.
    Args:
        sender_email: mail sender email
        password: mail sender password
        reports: all crawling reports
        error_type: type of the errors to consider for reporting
        recipients: list of email recipients
    """
    error_report = "The following failures occurred during crawling: \n \n"
    error_counter = 1

    for report in reports:
        if report.error_message and report.error_type == error_type:
            error_report += str(error_counter) + "- Error occurred while processing: " + CEDAR_SITE + \
                            report.template_instance + ".\n"
            error_report += "\t User: " + report.editor + "\n"
            error_report += "\t Cause: " + report.error_message + "\n\n"
            error_counter += 1

    if error_counter > 1:
        try:
            send_email(sender_email, password, recipients, error_report)
        except Exception as err:
            log.error("Failed to sent report mail to '{}', cause: {}.".format(str(recipients), str(err)))


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
            if report.error_type == type(TechnicalException).__name__:
                error_report += "\t (Internal error details are sent to the support team as well)\n"
            error_counter += 1
        else:
            success_report += str(success_counter) + "- CEDAR form crawled: " + CEDAR_SITE + \
                              report.template_instance + "\n"
            success_report += "\t- Created entity: " + report.created_entity + "\n\n"
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
    sender_email = get_crawler_email()
    password = get_crawler_email_password()
    send_email(sender_email, password, get_tech_support_emails(), failure_message, subject="VFB Crawler Error")


def send_failure_report_to_support(failed_reports: list):
    """
    Sends reports that cannot be sent to the related users (for any reason, user don't have email, gmail error etc.) to
    the technical support team
    """
    if failed_reports:
        try:
            sender_email = get_crawler_email()
            password = get_crawler_email_password()
            send_email(sender_email, password, get_tech_support_emails(), generate_failure_report_content(failed_reports))
        except Exception as err:
            log.error("Failed to sent failure report mail to the support team '{}', cause: {}.".format(
                get_tech_support_emails(), str(err)))


def send_email(sender_email, password, receiver_email, message, subject=REPORT_SUBJECT):
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (sender_email, receiver_email, subject, message)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
    server.close()
    log.info("Successfully send mail to '{}'.".format(receiver_email))


def get_crawler_email_password():
    if "VFBCRAWLER_EMAIL_PASS" in os.environ:
        return os.getenv("VFBCRAWLER_EMAIL_PASS")
    else:
        raise CrawlerException("vfbcrawler email password is not defined in the environment variables. !!!")


def get_crawler_email():
    if "VFBCRAWLER_EMAIL_USER" in os.environ:
        return os.getenv("VFBCRAWLER_EMAIL_USER")
    else:
        raise CrawlerException("vfbcrawler email user is not defined in the environment variables. !!!")


def get_tech_support_emails():
    if "TECH_SUPPORT_EMAIL" in os.environ:
        return json.loads(os.getenv("TECH_SUPPORT_EMAIL"))
    else:
        raise CrawlerException("Tech support email is not defined in the environment variables. !!!")


def get_editor_support_emails():
    if "EDITOR_SUPPORT_EMAIL" in os.environ:
        return json.loads(os.getenv("EDITOR_SUPPORT_EMAIL"))
    else:
        raise CrawlerException("Tech support email is not defined in the environment variables. !!!")
