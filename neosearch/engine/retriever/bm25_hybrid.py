from llama_index.core.retrievers import (
    BaseRetriever,
    VectorIndexRetriever,
    RouterRetriever,
)
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.tools import RetrieverTool
from llama_index.core.settings import Settings


class HybridRetriever(BaseRetriever):
    """
    A retriever that combines the results of a vector retriever and a BM25 retriever.

    Attributes:
        vector_retriever (VectorIndexRetriever): A retriever that uses a vector index.
        bm25_retriever (BM25Retriever): A retriever that uses BM25.
    """
    def __init__(
        self,
        vector_retriever: VectorIndexRetriever,
        bm25_retriever: BM25Retriever,
    ):
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever
        super().__init__()

    def _retrieve(self, query, **kwargs) -> list:
        bm25_nodes = self.bm25_retriever.retrieve(query, **kwargs)
        vector_nodes = self.vector_retriever.retrieve(query, **kwargs)

        # combine the two lists of nodes
        all_nodes = []
        node_ids = set()
        for n in bm25_nodes + vector_nodes:
            if n.node.node_id not in node_ids:
                all_nodes.append(n)
                node_ids.add(n.node.node_id)
        return all_nodes


    async def _aretrieve(self, query, **kwargs) -> list:
        bm25_nodes = await self.bm25_retriever.aretrieve(query, **kwargs)
        vector_nodes = await self.vector_retriever.aretrieve(query, **kwargs)

        # combine the two lists of nodes
        all_nodes = []
        node_ids = set()
        for n in bm25_nodes + vector_nodes:
            if n.node.node_id not in node_ids:
                all_nodes.append(n)
                node_ids.add(n.node.node_id)
        return all_nodes


    def create_router_retriever(self):
        retriever_tools = [
            RetrieverTool.from_defaults(
                retriever=self.vector_retriever,
                description="Useful in most cases",
            ),
            RetrieverTool.from_defaults(
                retriever=self.bm25_retriever,
                description="Useful if searching about specific information",
            ),
        ]

        # load settings
        llm = Settings.llm

        return RouterRetriever.from_defaults(
            retriever_tools=retriever_tools,
            llm=llm,
            select_multi=True,
        )
