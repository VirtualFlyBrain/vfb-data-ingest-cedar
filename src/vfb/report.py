import os
import smtplib
import logging
from exception.crawler_exception import CrawlerException
from vfb.ingest_api_client import get_user_details

logging.basicConfig()
logging.root.setLevel(logging.INFO)
log = logging.getLogger(__name__)

ORCID_ID_PREFIX = "https://orcid.org/"


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

    failed_reports = list()
    for report in reports:
        editor = report.editor
        if not str(editor).startswith(ORCID_ID_PREFIX):
            editor = ORCID_ID_PREFIX + editor
        user_info = get_user_details(editor)
        if "email" not in user_info:
            failed_reports.append("User email doesn't exist in the VFB :" + editor)
        receiver_email = user_info["email"]
        message = """\
        Subject: Hi there
    
        This message is sent from Python."""
        send_email(sender_email, password, receiver_email, message)

    return failed_reports


def send_email(sender_email, password, receiver_email, message):
    subject = "VFB data ingestion report"
    text = message

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (sender_email, receiver_email, subject, text)
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
