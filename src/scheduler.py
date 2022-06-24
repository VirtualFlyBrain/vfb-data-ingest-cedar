import logging
import os
import json

import schedule
import time
from datetime import datetime
from cedar import crawler
from vfb.report import send_reports, send_failure_report_to_support, send_failure_message_to_support
from exception.crawler_exception import TechnicalException, ContentException

logging.basicConfig()
logging.root.setLevel(logging.INFO)
log = logging.getLogger(__name__)


def schedule_crawler():
    schedule.every().hour.do(main)
    # schedule.every(10).seconds.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    try:
        crawling_types = json.loads(os.getenv("CRAWL_TYPE", "[Dataset, Neuron, Split, SplitDriver]"))
        log.info(">>>>> Crawler started {} for types: '{}'".format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), str(crawling_types)))
        reports = crawler.crawl(crawling_types)
        log.info(">>>>> Crawling completed {} for types: '{}'".format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), str(crawling_types)))
        failed_reports = send_reports(reports)
        send_failure_report_to_support(failed_reports)
        if get_execution_status(reports, failed_reports):
            log.info('SUCCESS')
        else:
            log.info('FAILURE')
    except TechnicalException as err:
        log.error(err, exc_info=True)
        send_failure_message_to_support("VFB Crawler failed: " + str(err.message))
        log.info('FAILURE')
    except ContentException as err:
        log.error(err, exc_info=True)
        send_failure_message_to_support("VFB Crawler failed: " + str(err.message))
        log.info('FAILURE')
    except Exception as err:
        log.error(err, exc_info=True)
        send_failure_message_to_support("VFB Crawler failed: " + str(err))
        log.info('FAILURE')


def get_execution_status(reports, failed_reports):
    """
    If any of the crawling reports contain error message, status is fail (False). Success (True) otherwise.

    Args:
        reports: crawling status reports.
        failed_reports: list of report sending failures
    Returns:
        True if all success, False otherwise.
    """
    if failed_reports:
        return False

    status = True
    for report in reports:
        if report.error_message:
            status = False
    return status


if __name__ == "__main__":
    main()
    # schedule_crawler()
