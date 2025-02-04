from llama_index.core.retrievers import (
    BaseRetriever,
    VectorIndexRetriever,
    RouterRetriever,
)
from llama_index.core.tools import RetrieverTool
from llama_index.core.settings import Settings


class ParadeDBRetriever(BaseRetriever):
    def __init__(self):
        super().__init__()


    def _retrieve(self, query: str, **kwargs) -> list:
        #TODO
        return []


    async def _aretrieve(self, query, **kwargs) -> list:
        #TODO
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
