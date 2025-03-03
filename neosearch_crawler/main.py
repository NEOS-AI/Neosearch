from pathlib import Path
import sys

sys.path.append("..")

# custom modules
from constants import (
    BASE_WEB_CRAWL_AGENT_MODE,
    COMMON_CRAWL_RUNNER_MODE,
    PARSE_WIKI_TO_PARADEDB_MODE,
    FOR_TEST,
)
from engine.agent.web_corpus_collector import run_web_corpus_collect_agent
from engine.agent.wikidump_parser import run_wiki_dump_parser
from engine.runner.common_crawl import run_common_crawl
from utils import extract_url_content
from utils.logger import Logger


logger = Logger()

def url_crawl_test(output_format: str = "markdown"):
    url = "https://namu.wiki/w/%EC%95%84%EB%9D%BC%ED%95%98%EC%8B%9C%20%ED%83%80%EB%B9%84"
    print(extract_url_content(url, output_format=output_format))


def main(mode: str):
    #TODO add support for scrapegraphai
    print(f"Running in mode: {mode}")

    if mode == BASE_WEB_CRAWL_AGENT_MODE:
        return run_web_corpus_collect_agent()

    if mode == PARSE_WIKI_TO_PARADEDB_MODE:
        path_str = "./data/wiki-articles.json"
        path = Path(path_str)
        abs_path = path.resolve()
        abs_path_str = str(abs_path)
        return run_wiki_dump_parser(abs_path_str)

    if mode == COMMON_CRAWL_RUNNER_MODE:
        return run_common_crawl()

    # if no matching mode is found, run the test
    url_crawl_test()


if __name__ == "__main__":
    if FOR_TEST:
        url_crawl_test()
    else:
        main(BASE_WEB_CRAWL_AGENT_MODE)
