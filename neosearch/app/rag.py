import os
import httpx

# custom import
from neosearch.engine.utils.rag_search import (
    search_with_wikipedia,
    search_with_bing,
    search_with_google,
    search_with_serper,
    search_with_searchapi,
)


def get_rag_searcher() -> "RagSearcher":
    """Get the RAG searcher."""
    searcher = RagSearcher()
    searcher.init()
    return searcher


class RagSearcher:
    """
    RAG searcher class.
    Uses the API call to the external search engine to get the search results.

    Attributes:
        backend (str): The backend to use for the search.
        search_function (function): The search function to use.
    """

    def __init__(self, backend: str = "WIKIPEDIA",) -> None:
        self.backend = backend

    def init(self):
        if self.backend == "WIKIPEDIA":
            self.search_function = search_with_wikipedia

        elif self.backend == "SEARCHAPI":
            self.search_api_key = os.environ["SEARCHAPI_API_KEY"]
            self.search_function = lambda query: search_with_searchapi(
                query,
                self.search_api_key,
            )
        elif self.backend == "LEPTON":
            from lepton import Client  # type: ignore
            from leptonai.api.workspace import WorkspaceInfoLocalRecord  # type: ignore

            self.leptonsearch_client = Client(
                "https://search-api.lepton.run/",
                token=os.environ.get("LEPTON_WORKSPACE_TOKEN")
                or WorkspaceInfoLocalRecord.get_current_workspace_token(),
                stream=True,
                timeout=httpx.Timeout(connect=10, read=120, write=120, pool=10),
            )
        elif self.backend == "BING":
            self.search_api_key = os.environ["BING_SEARCH_V7_SUBSCRIPTION_KEY"]
            self.search_function = lambda query: search_with_bing(
                query,
                self.search_api_key,
            )
        elif self.backend == "GOOGLE":
            self.search_api_key = os.environ["GOOGLE_SEARCH_API_KEY"]
            self.search_function = lambda query: search_with_google(
                query,
                self.search_api_key,
                os.environ["GOOGLE_SEARCH_CX"],
            )
        elif self.backend == "SERPER":
            self.search_api_key = os.environ["SERPER_SEARCH_API_KEY"]
            self.search_function = lambda query: search_with_serper(
                query,
                self.search_api_key,
            )
        else:
            raise RuntimeError("Backend must be LEPTON, BING, GOOGLE, SERPER or SEARCHAPI.")


    async def search(self, query: str) -> list:
        # search with the backend
        return self.search_function(query)
