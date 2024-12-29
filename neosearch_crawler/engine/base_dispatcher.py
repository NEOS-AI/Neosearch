from typing import Any

# custom modules
from neosearch_crawler.crawlers.github import GithubCrawler
from neosearch_crawler.crawlers.linkedin import LinkedInCrawler
from neosearch_crawler.crawlers.medium import MediumCrawler
from neosearch_crawler.mongo_db.documents import UserDocument
from neosearch_crawler.utils.logger import Logger
from neosearch_crawler.dispatchers.base import CrawlerDispatcher
from neosearch_crawler.dispatchers.lib import user_to_names


logger = Logger()

_dispatcher = CrawlerDispatcher()
_dispatcher.register("medium", MediumCrawler)
_dispatcher.register("linkedin", LinkedInCrawler)
_dispatcher.register("github", GithubCrawler)


def handler(event) -> dict[str, Any]:
    first_name, last_name = user_to_names(event.get("user"))

    user = UserDocument.get_or_create(first_name=first_name, last_name=last_name)

    link = event.get("link")
    logger.log_debug(f"Processing link: {link}")
    crawler = _dispatcher.get_crawler(link)
    logger.log_debug(f"Processing link: {link}")

    try:
        crawler.extract(link=link, user=user)

        return {"statusCode": 200, "body": "Link processed successfully"}
    except Exception as e:
        return {"statusCode": 500, "body": f"An error occurred: {str(e)}"}


if __name__ == "__main__":
    event = {
        "user": "Paul Iuztin",
        "link": "https://www.linkedin.com/in/vesaalexandru/",
    }
    handler(event)
