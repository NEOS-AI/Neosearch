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


    def _retrieve(self, query, **kwargs) -> list:
        #TODO searxng API call -> use circuit breaker!
        return []


    async def _aretrieve(self, query, **kwargs) -> list:
        #TODO searxng API call -> use circuit breaker!
        return []


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
