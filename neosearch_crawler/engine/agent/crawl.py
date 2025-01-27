from neosearch_crawler.constants.crawl_seeds import INITIAL_SEEDS
from .base import BaseAgent, BaseArgs


class CrawlingAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.seeds = INITIAL_SEEDS

    def run(self, args: BaseArgs):
        #TODO crawl the contents from the web
        pass
