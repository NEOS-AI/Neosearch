import sys

sys.path.append("..")

# custom modules
from constants import (
    BASE_WEB_CRAWL_AGENT_MODE,
    COMMON_CRAWL_RUNNER_MODE,
    FOR_TEST,
)
from engine.runner.common_crawl import run_common_crawl
from utils import extract_url_content
from utils.logger import Logger


logger = Logger()

def url_crawl_test(output_format: str = "markdown"):
    url = "https://namu.wiki/w/%EC%95%84%EB%9D%BC%ED%95%98%EC%8B%9C%20%ED%83%80%EB%B9%84"
    print(extract_url_content(url, output_format=output_format))


def main(mode: str):
    if mode == BASE_WEB_CRAWL_AGENT_MODE:
        #TODO crawl, extract, and index the content of the URL
        pass
    if mode == COMMON_CRAWL_RUNNER_MODE:
        return run_common_crawl()

    # if no matching mode is found, run the test
    url_crawl_test()


if __name__ == "__main__":
    if FOR_TEST:
        url_crawl_test()
    else:
        main(BASE_WEB_CRAWL_AGENT_MODE)
