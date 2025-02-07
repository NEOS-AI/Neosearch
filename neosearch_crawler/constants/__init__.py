from dotenv import load_dotenv
import os

# custom modules
from .modes import (
    BASE_WEB_CRAWL_AGENT_MODE,
    COMMON_CRAWL_RUNNER_MODE,
    PARSE_WIKI_TO_PARADEDB_MODE,
)


# Load the environment variables
load_dotenv()

FOR_TEST = os.getenv("FOR_TEST", "0") == "1"

__all__ = [
    # __init__.py
    "FOR_TEST",
    # modes.py
    "BASE_WEB_CRAWL_AGENT_MODE",
    "COMMON_CRAWL_RUNNER_MODE",
    "PARSE_WIKI_TO_PARADEDB_MODE",
]