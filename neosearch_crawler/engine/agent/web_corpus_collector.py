from copy import deepcopy

# custom modules
from neosearch_crawler.utils.trafilatura_util import (
    init_trafilatura_config,
    run_focused_crawler,
)
from neosearch_crawler.constants.crawl_seeds import INITIAL_SEEDS

from .base import BaseAgent, BaseArgs


class WebCorpusCollectAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.config = init_trafilatura_config()
        self.seed_urls = deepcopy(INITIAL_SEEDS)

    def run(self, args: BaseArgs):
        known_url_list = []

        #TODO crawl urls by links
        for url in self.seed_urls:
            to_visit, known_urls, navigatable = run_focused_crawler(
                url,
                max_seen_urls=20,
                max_known_urls=100000,
                known_links=None,
            )
            known_url_list.extend(known_urls)

            while navigatable:
                url_ = to_visit.pop(0)
                to_visit_, known_urls, navigatable = run_focused_crawler(
                    url_,
                    max_seen_urls=20,
                    max_known_urls=100000,
                    known_links=known_url_list,
                )
                to_visit.extend(to_visit_)
                known_url_list.extend(known_urls)

                if not navigatable and len(to_visit) != 0:
                    navigatable = True

        # remove duplicates
        known_url_list = list(set(known_url_list))

        # save know_urls to file
        with open("known_urls.txt", "w") as f:
            for url in known_url_list:
                f.write(f"{url}\n")

        #TODO


def run_web_corpus_collect_agent():
    agent = WebCorpusCollectAgent()
    args = BaseArgs(id="web_corpus_collect_agent")
    agent.run(args)
