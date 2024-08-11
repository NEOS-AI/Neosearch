from typing import Any, Coroutine, Union
# from llama_index.core.base.response.schema import AsyncStreamingResponse, PydanticResponse, Response, StreamingResponse
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.query_engine import CustomQueryEngine, TransformQueryEngine
from llama_index.core import get_response_synthesizer
from llama_index.core.response_synthesizers import BaseSynthesizer
from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate
from llama_index.core.retrievers import VectorIndexAutoRetriever
from llama_index.core.vector_stores import VectorStoreInfo
from llama_index.core.indices.query.query_transform import HyDEQueryTransform


# custom modules
from neosearch.engine.index import get_index
from neosearch.engine.retriever.base import get_base_retriever
from neosearch.app.rag import get_rag_searcher, RagSearcher


def get_search_query_engine(use_hyde: bool = True) -> CustomQueryEngine:
    engine = RAGStringQueryEngine(use_base_retriever=False, use_search_results=True)
    if use_hyde:
        hyde = HyDEQueryTransform(include_original=True)
        engine = TransformQueryEngine(engine, hyde)
    return engine


def get_query_engine(use_hyde: bool = True, use_str_formatted_query_engine: bool = True) -> CustomQueryEngine:
    if use_str_formatted_query_engine:
        return get_string_query_engine(use_hyde)

    query_engine = RAGQueryEngine()
    if use_hyde:
        hyde = HyDEQueryTransform(include_original=True)
        query_engine = TransformQueryEngine(query_engine, hyde)
    return query_engine

def get_string_query_engine(use_hyde: bool = True) -> CustomQueryEngine:
    query_engine = RAGStringQueryEngine()
    if use_hyde:
        hyde = HyDEQueryTransform(include_original=True)
        query_engine = TransformQueryEngine(query_engine, hyde)
    return query_engine


class RAGQueryEngine(CustomQueryEngine):
    """RAG Query Engine."""

    retriever: BaseRetriever
    response_synthesizer: BaseSynthesizer

    def __init__(
        self,
        use_base_retriever: bool = True,
        vector_store_info: Union[VectorStoreInfo, None] = None,
    ):
        if use_base_retriever:
            self.retriever = get_base_retriever()
        else:
            if vector_store_info is None:
                raise ValueError("vector_store_info must be provided if use_base_retriever is False.")

            self.retriever = VectorIndexAutoRetriever(
                get_index(),
                vector_store_info=vector_store_info,
                similarity_top_k=3,
                empty_query_top_k=10,  # if only metadata filters are specified, this is the limit
                verbose=True,
            )
        self.response_synthesizer = get_response_synthesizer()


    def custom_query(self, query_str: str):
        nodes = self.retriever.retrieve(query_str)
        response_obj = self.response_synthesizer.synthesize(query_str, nodes)
        return response_obj


    async def acustom_query(self, query_str: str):
        nodes = await self.retriever.aretrieve(query_str)
        response_obj = self.response_synthesizer.synthesize(query_str, nodes)
        return response_obj


class RAGStringQueryEngine(CustomQueryEngine):
    """RAG String Query Engine."""

    retriever: BaseRetriever
    response_synthesizer: BaseSynthesizer
    llm: OpenAI
    qa_prompt: PromptTemplate

    def __init__(
        self,
        use_base_retriever: bool = True,
        vector_store_info: VectorStoreInfo = None,
        use_search_results: bool = False,
    ):
        if use_base_retriever:
            self.retriever = get_base_retriever()
        else:
            if vector_store_info is None:
                raise ValueError("vector_store_info must be provided if use_base_retriever is False.")

            self.retriever = VectorIndexAutoRetriever(
                get_index(),
                vector_store_info=vector_store_info,
                similarity_top_k=2,
                empty_query_top_k=10,  # if only metadata filters are specified, this is the limit
                verbose=True,
            )

        self.llm = OpenAI()
        self.qa_prompt = PromptTemplate(
            "Context information is below.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Given the context information and not prior knowledge, "
            "answer the query.\n"
            "Query: {query_str}\n"
            "Answer: "
        )
        self.search_qa_prompt = PromptTemplate(
            "Default context information is below.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Search context information is below.\n"
            "---------------------\n"
            "{search_results_str}\n"
            "---------------------\n"
            "Given the context information and not prior knowledge, "
            "answer the query.\n"
            "Query: {query_str}\n"
            "Answer: "
        )
        self.use_search_results = use_search_results

        # rag searcher (should not be shared across instances)
        self.rag_searcher: RagSearcher = get_rag_searcher()


    def custom_query(self, query_str: str) -> str:
        nodes = self.retriever.retrieve(query_str)

        context_str = "\n\n".join([n.node.get_content() for n in nodes])
        if self.use_search_results:
            search_results = self.rag_searcher.search(query_str)
            search_results_str = "\n\n".join([str(r) for r in search_results])
            response = self.llm.complete(
                self.search_qa_prompt.format(context_str=context_str, search_results_str=search_results_str, query_str=query_str)
            )
        else:
            response = self.llm.complete(
                self.qa_prompt.format(context_str=context_str, query_str=query_str)
            )

        return str(response)


    async def acustom_query(self, query_str: str) -> Coroutine[Any, Any, str]:
        nodes = await self.retriever.aretrieve(query_str)

        context_str = "\n\n".join([n.node.get_content() for n in nodes])
        if self.use_search_results:
            search_results = await self.rag_searcher.search(query_str) #TODO async support
            search_results_str = "\n\n".join([str(r) for r in search_results])
            response = await self.llm.acomplete(
                self.search_qa_prompt.format(
                    context_str=context_str,
                    search_results_str=search_results_str,
                    query_str=query_str
                )
            )
        else:
            response = await self.llm.acomplete(
                self.qa_prompt.format(
                    context_str=context_str, query_str=query_str
                )
            )

        return str(response)
