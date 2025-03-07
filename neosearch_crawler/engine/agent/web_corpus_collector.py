from copy import deepcopy
import orjson
import threading
from sqlalchemy import text

# custom modules
from neosearch_crawler.utils.trafilatura_util import (
    init_trafilatura_config,
    run_focused_crawler,
    extract_url_content,
)
from neosearch_crawler.utils.pdf_util import extract_pdf_from_url
from neosearch_crawler.constants.crawl_seeds import INITIAL_SEEDS
from neosearch_crawler.datastore.database import engine, get_session

from .base import BaseAgent, BaseArgs


class WebCorpusCollectArgs(BaseArgs):
    load_from_file: bool = False


class WebCorpusCollectAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.engine = engine
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

        # for all urls, apply _map_url_refinement_rules
        known_url_list = [self._map_url_refinement_rules(url) for url in known_url_list]

        # remove duplicates (since _map_url_refinement_rules may introduce duplicates)
        known_url_list = list(set(known_url_list))

        # save know_urls to file
        with open("known_urls.txt", "w") as f:
            for url in known_url_list:
                f.write(f"{url}\n")

        return known_url_list

    def _map_url_refinement_rules(self, url: str):
        # if url is arxiv pdf, then replace it with arxiv abstract page
        if "https://arxiv.org/pdf/" in url:
            return url.replace("https://arxiv.org/pdf/", "https://arxiv.org/abs/")

        return url


    def extract_contents(self, args: WebCorpusCollectArgs, known_urls: list):
        data_list = []

        # split known_urls into 4 parts
        len_ = len(known_urls)
        part = len_ // 4
        chunk_1 = known_urls[:part]
        chunk_2 = known_urls[part:2*part]
        chunk_3 = known_urls[2*part:3*part]
        chunk_4 = known_urls[3*part:]

        threads: list[threading.Thread] = []

        # extract contents in parallel
        for chunk in [chunk_1, chunk_2, chunk_3, chunk_4]:
            thread = threading.Thread(
                target=self._extract_contents,
                args=(args, chunk, data_list)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # save data to file (as jsonl)
        with open("web_corpus.jsonl", "w") as f:
            for data in data_list:
                data_str = orjson.dumps(data).decode("utf-8")
                f.write(f"{data_str}\n")


    def _extract_contents(self, args: WebCorpusCollectArgs, known_urls: list, data_list: list):
        for url in known_urls:
            try:
                data = extract_url_content(
                    url,
                    output_format="markdown",
                    include_tables=True,
                    deduplicate=True
                )

                # if the content is not HTML (PDF, etc) then data will be None (since trafilatura builds element tree from "web content")
                if data is None:
                    # extract pdf
                    try:
                        data_ = extract_pdf_from_url(url)
                        data_list.append(data_)
                    except Exception as e:
                        print(f"Failed to extract pdf from {url}. Error: {e}")
                    continue

                data_list.append(data)
            except ValueError as ve:
                print(f"Failed to extract content from {url}. Error: {ve}")


    def save_data_to_db(self):
        with open("web_corpus.jsonl", "r") as f:
            with next(get_session(self.engine)) as session:
                insert_query = """INSERT INTO web_data (title, url, body, description, metadata) VALUES (:title, :url, :body, :description, :metadata)"""
                for line in f:
                    data = orjson.loads(line)
                    title = data.get("title", "")
                    content = data["content"]
                    url = data["url"]
                    description = data.get("description", "")
                    title = data.get("title", "")
                    metadata_str = data.get("metadata", "")

                    insert_query = """INSERT INTO web_corpus (title, url, body) VALUES (:title, :url, :body)"""
                    query = text(insert_query)
                    args = {"title": title, "url": url, "body": content, "description": description, "metadata": metadata_str}
                    session.execute(query, args)
                    session.commit()


def run_web_corpus_collect_agent():
    agent = WebCorpusCollectAgent()
    args = WebCorpusCollectArgs(
        id="web_corpus_collect_agent",
        load_from_file=True,
    )
    agent.run(args)
