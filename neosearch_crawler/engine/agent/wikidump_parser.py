#
# Parsing wiki dump jsonl data and converting it to paradedb schema
#
import orjson
import os
from sqlalchemy import text

# custom modules
from neosearch_crawler.datastore.database import engine, get_session

from .base import BaseAgent, BaseArgs


class WikiDumpArgs(BaseArgs):
    wiki_dump_jsonl_file: str


class WikiDumpParser:
    def __init__(self, wiki_dump_jsonl_file: str):
        self.wiki_dump_jsonl_file = wiki_dump_jsonl_file
        if not os.path.exists(self.wiki_dump_jsonl_file):
            raise FileNotFoundError(f"File not found: {self.wiki_dump_jsonl_file}")

    def parse_wiki_dump(self):
        with open(self.wiki_dump_jsonl_file, "r") as f:
            for line in f:
                data = orjson.loads(line)
                title = data["title"]
                body = data["body"]
                url = data["url"]
                yield title, body, url


class WikiDumpParserAgent(BaseAgent):
    def __init__(self, bulk_size: int = 200):
        super().__init__()
        self.engine = engine
        self.bulk_size = bulk_size

    def run(self, args: WikiDumpArgs):
        total_cnt = 0
        wiki_dump_parser = WikiDumpParser(args.wiki_dump_jsonl_file)
        _store = []
        insert_query = """INSERT INTO wiki_articles (title, url, body) VALUES (:title, :url, :body)"""
        with next(get_session(self.engine)) as session:
            for title, body, url in wiki_dump_parser.parse_wiki_dump():
                # convert to paradedb schema
                _store.append({"title": title, "url": url, "body": body})

                if len(_store) == self.bulk_size:
                    # query_to_exec = insert_query + ", ".join(_store)
                    query_to_exec = insert_query
                    query = text(query_to_exec)

                    session.execute(query, _store)
                    session.commit()
                    _store = []
                    total_cnt += self.bulk_size

                    print(f"Inserted {self.bulk_size} records into wiki_articles (total: {total_cnt})")

            if len(_store) > 0:
                query_to_exec = insert_query
                query = text(query_to_exec)

                session.execute(query, _store)
                session.commit()
                total_cnt += len(_store)

                print(f"Inserted {len(_store)} records into wiki_articles (total: {total_cnt})")


def run_wiki_dump_parser(path_to_wiki_dump_jsonl: str):
    args = WikiDumpArgs(
        wiki_dump_jsonl_file=path_to_wiki_dump_jsonl,
        id="wiki_dump_parser",
    )
    agent = WikiDumpParserAgent()
    agent.run(args)
