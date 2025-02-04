from llama_index.core.retrievers import (
    BaseRetriever,
    VectorIndexRetriever,
    RouterRetriever,
)
from llama_index.core.tools import RetrieverTool
from llama_index.core.settings import Settings

# custom modules
from neosearch.datastore import engine, async_engine, get_session, get_async_session


class ParadeDBRetriever(BaseRetriever):
    def __init__(self):
        super().__init__()
        self.engine = engine
        self.async_engine = async_engine

    def _retrieve(self, query: str, **kwargs) -> list:
        session = get_session(self.engine)
        return []


    async def _aretrieve(self, query, **kwargs) -> list:
        session = get_async_session(self.async_engine)
        return []


    def create_router_retriever(self):
        retriever_tools = [
            RetrieverTool.from_defaults(
                retriever=self,
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
