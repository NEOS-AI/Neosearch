from dotenv import load_dotenv
import os

# custom modules
from .modes import COMMON_CRAWL_RUNNER_MODE


# Load the environment variables
load_dotenv()

FOR_TEST = os.getenv("FOR_TEST", "0") == "1"

__all__ = [
    # __init__.py
    "FOR_TEST",
    # modes.py
    "COMMON_CRAWL_RUNNER_MODE",
]