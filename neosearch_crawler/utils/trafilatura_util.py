from copy import deepcopy
import trafilatura
from trafilatura.settings import DEFAULT_CONFIG
from trafilatura.spider import focused_crawler, is_still_navigation
from typing import Union


def init_trafilatura_config():
    my_config = deepcopy(DEFAULT_CONFIG)

    #TODO see more options in <https://trafilatura.readthedocs.io/en/latest/settings.html>

    return my_config


def run_focused_crawler(
    url: str,
    max_seen_urls: int = 10,
    max_known_urls: int = 100000,
    todo: Union[list, None] = None,
    known_links: Union[list, None] = None,
    lang: Union[str, None] = None
) -> tuple[list[str], list[str], bool]:
    """

    Args:
        max_seen_urls: the maximum number of pages to visit (default: 10)
        max_known_urls: the maximum number of pages to “know” about (default: 100000)
        todo: provide a previously generated list of pages to visit (i.e. a crawl frontier)
        known_links: provide a list of previously known pages
        lang: try to target links according to language heuristics (two-letter code)

    Returns:
        tuple: Returns the snapshot of the current state of the crawler.
        - to_visit: the list of pages to visit (next visited)
        - known_links: the list of known (list of know links)
        - navigatable: whether the crawler is still navigatable
    """
    # `to_visit` variable keeps track of what is ahead
    # `known_links` variable ensures that the same pages are not visited twice
    to_visit, known_links = focused_crawler(
        url,
        max_seen_urls=max_seen_urls,
        max_known_urls=max_known_urls,
        todo=todo,
        known_links=known_links,
        lang=lang,
    )

    navigatable = is_still_navigation(to_visit)

    return to_visit, known_links, navigatable


def extract_url_content(
    url,
    output_format: Union[str, None] = "markdown",
    include_tables: bool = True,
    deduplicate: bool = False
):
    if output_format not in {"json", "xml", "markdown"}:
        output_format = None

    downloaded = trafilatura.fetch_url(url)

    # get metadata and description from the downloaded content
    metadata = trafilatura.extract_metadata(downloaded)
    description = metadata.description
    title = metadata.title

    if output_format is None:
        content =  trafilatura.extract(
            downloaded,
            include_tables=include_tables,
            deduplicate=deduplicate
        )
    else:
        content = trafilatura.extract(
            downloaded,
            deduplicate=deduplicate,
            output_format=output_format,
            include_tables=include_tables
        )

    return {
        "url":url,
        "content":content,
        "description":description,
        "title": title,
    }
