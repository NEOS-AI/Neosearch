import sys
import multiprocessing
import os
from dotenv import load_dotenv
from datetime import datetime

sys.path.append("..")

# custom modules
from constants.modes import COMMON_CRAWL_RUNNER_MODE
from engine.runner.common_crawl import CommonCrawlRunner
from utils import extract_url_content
from utils.logger import Logger


load_dotenv()
FOR_TEST = os.getenv("FOR_TEST", "0") == "1"

logger = Logger()

def url_crawl_test(output_format: str = "markdown"):
    url = "https://namu.wiki/w/%EC%95%84%EB%9D%BC%ED%95%98%EC%8B%9C%20%ED%83%80%EB%B9%84"
    print(extract_url_content(url, output_format=output_format))


def run_common_crawl():
    runner = CommonCrawlRunner()

    logger.log_info("Setting up the Common Crawl runner.")
    # dag = runner.build_dag()
    runner.run_dag()


def main(mode: str):
    if mode == COMMON_CRAWL_RUNNER_MODE:
        return run_common_crawl()

    num_of_cpus = multiprocessing.cpu_count()

    #TODO crawl, extract, and index the content of the URL


if __name__ == "__main__":
    if FOR_TEST:
        url_crawl_test()
    else:
        main(COMMON_CRAWL_RUNNER_MODE)
