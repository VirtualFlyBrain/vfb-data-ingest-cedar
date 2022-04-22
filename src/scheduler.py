import logging
import os
import json

import schedule
import time
from datetime import datetime
from cedar import crawler

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
    crawling_types = json.loads(os.getenv("CRAWL_TYPE", "[Dataset, Neuron]"))
    log.info(">>>>> Crawler started {} for types: ''".format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), str(crawling_types)))
    status = crawler.crawl(crawling_types)
    log.info(">>>>> Crawling completed {} for types: ''".format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), str(crawling_types)))
    if status:
        log.info('SUCCESS')
    else:
        log.info('FAILURE')


if __name__ == "__main__":
    main()
    # schedule_crawler()
