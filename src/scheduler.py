import logging
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
    log.info('>>>>> Crawler started {}'.format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))
    crawler.crawl()
    log.info('>>>>> Crawler completed {}'.format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))


if __name__ == "__main__":
    main()
    # schedule_crawler()
