from copy import deepcopy
import polars as pl

# custom modules
from neosearch_crawler.utils.trafilatura_util import (
    init_trafilatura_config,
    run_focused_crawler,
    extract_url_content,
)
from neosearch_crawler.constants.crawl_seeds import INITIAL_SEEDS

from .base import BaseAgent, BaseArgs


class WebCorpusCollectArgs(BaseArgs):
    load_from_file: bool = False


class WebCorpusCollectAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.config = init_trafilatura_config()
        self.seed_urls = deepcopy(INITIAL_SEEDS)

    def run(self, args: WebCorpusCollectArgs):
        if args.load_from_file:
            known_urls = self.read_file_and_load_know_urls()
        else:
            known_urls = self.gather_urls(args)
        self.extract_contents(args, known_urls)


    def read_file_and_load_know_urls(self):
        with open("known_urls.txt", "r") as f:
            known_urls = f.readlines()
            known_urls = [url.strip() for url in known_urls]
        return known_urls


    def gather_urls(self, args: WebCorpusCollectArgs):
        known_url_list = []

        # crawl urls by links
        for url in self.seed_urls:
            print(f"Running focused crawler on {url}")
            to_visit, known_urls, navigatable = run_focused_crawler(
                url,
                max_seen_urls=20,
                max_known_urls=100000,
                known_links=None,
            )
            known_url_list.extend(known_urls)

            if navigatable:
                print(f"Running focused crawler on {to_visit[0]} (base_url: {url})")
                url_ = to_visit.pop(0)
                to_visit_, known_urls, navigatable = run_focused_crawler(
                    url_,
                    max_seen_urls=20,
                    max_known_urls=100000,
                    known_links=known_urls,
                )
                to_visit.extend(to_visit_)
                known_url_list.extend(known_urls)

        # remove duplicates
        known_url_list = list(set(known_url_list))

        # save know_urls to file
        with open("known_urls.txt", "w") as f:
            for url in known_url_list:
                f.write(f"{url}\n")

        return known_url_list


    def extract_contents(self, args: WebCorpusCollectArgs, known_urls: list):
        data_list = []
        for url in known_urls:
            try:
                data = extract_url_content(
                    url,
                    output_format="markdown",
                    include_tables=True,
                    deduplicate=True
                )

                if data is None:
                    #TODO pdf, docx, etc.
                    continue

                data_list.append(data)
            except ValueError as ve:
                print(f"Failed to extract content from {url}. Error: {ve}")

        # save data to file
        df = pl.DataFrame(data_list)
        df.write_parquet("web_corpus.parquet")


def run_web_corpus_collect_agent():
    agent = WebCorpusCollectAgent()
    args = WebCorpusCollectArgs(
        id="web_corpus_collect_agent",
        load_from_file=True,
    )
    agent.run(args)
