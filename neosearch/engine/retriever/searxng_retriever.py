from typing import Union
from llama_index.core.retrievers import (
    BaseRetriever,
    VectorIndexRetriever,
    RouterRetriever,
)
from llama_index.core.tools import RetrieverTool
from llama_index.core.settings import Settings

# custom modules
from neosearch.exceptions.engine.retriever import VectorStoreIsNullError
from neosearch.engine.utils.searxng import SearxngAdaptor
from neosearch.constants.searxng import SEARXNG_BASE_URL


class SearxngRetriever(BaseRetriever):
    def __init__(
        self,
        vector_retriever: Union[VectorIndexRetriever, None] = None,
        use_with_vector_search: bool = False
    ):
        super().__init__()
        self.use_with_vector_search = use_with_vector_search

        if use_with_vector_search and vector_retriever is None:
            raise VectorStoreIsNullError("SearxngRetriever:: vector_retriever is None")

        self.vector_retriever = vector_retriever
        self.searxng_adaptor = SearxngAdaptor(SEARXNG_BASE_URL)


    def _retrieve(self, query: str, **kwargs) -> list:
        """
        Retrieve the query results.

        Args:
            query (str): Query string.

        Returns:
            (list): Search results. Includes vector search results as well if use_with_vector_search is True.
        """
        # searxng API call (use circuit breaker)
        search_results = self.searxng_adaptor.search(query)
        results = search_results.get("results", [])

        # we need to return list type to fulfill the inherited type checkings
        retrieval_results = [{
            "searxng": results,
            "vector_search": [],
        }]

        if not self.use_with_vector_search:
            return retrieval_results

        vector_search_results = self.vector_retriever.retrieve(query)
        retrieval_results[0]["vector_search"] = vector_search_results

        return retrieval_results


    async def _aretrieve(self, query, **kwargs) -> list:
        """
        Retrieve the query results asynchronously.

        Args:
            query (str): Query string.

        Returns:
            (list): Search results. Includes vector search results as well if use_with_vector_search is True.
        """
        # searxng API call (use circuit breaker)
        search_results = await self.searxng_adaptor.asearch(query)
        results = search_results.get("results", [])
        retrieval_results = [{
            "searxng": results,
            "vector_search": [],
        }]
        if not self.use_with_vector_search:
            return retrieval_results

        vector_search_results = await self.vector_retriever.aretrieve(query)
        retrieval_results[0]["vector_search"] = vector_search_results

        return retrieval_results


    def create_router_retriever(self):
        if not self.use_with_vector_search or self.vector_retriever is None:
            raise VectorIndexRetriever(
                "Cannot create RouterRetriever."
                "Probably, user_with_vector_search is False, or vector_retriever is None!"
            )

        retriever_tools = [
            RetrieverTool.from_defaults(
                retriever=self.vector_retriever,
                description="Useful in most cases",
            ),
        ]

        # load settings
        llm = Settings.llm

        return RouterRetriever.from_defaults(
            retriever_tools=retriever_tools,
            llm=llm,
            select_multi=True,
        )
