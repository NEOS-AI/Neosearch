from typing import Any, Coroutine, Union
# from llama_index.core.base.response.schema import AsyncStreamingResponse, PydanticResponse, Response, StreamingResponse
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.query_engine import CustomQueryEngine, TransformQueryEngine
from llama_index.core import get_response_synthesizer
from llama_index.core.response_synthesizers import BaseSynthesizer
from llama_index.llms.openai import OpenAI
from llama_index.core import ChatPromptTemplate, PromptTemplate
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.retrievers import VectorIndexAutoRetriever
from llama_index.core.vector_stores import VectorStoreInfo
from llama_index.core.indices.query.query_transform import HyDEQueryTransform


# custom modules
from neosearch.engine.index import get_index
from neosearch.engine.retriever.base import get_base_retriever
from neosearch.app.rag import get_rag_searcher, RagSearcher
from neosearch.constants.rag_search import rag_query_text, base_rag_query_text
from neosearch.constants.retriever import (
    VECTOR_INDEX_SIM_TOP_K,
    VECTOR_INDEX_EMPTY_QUERY_TOP_K,
    VECTOR_INDEX_VERBOSE
)
from neosearch.utils.logging import Logger


logger = Logger()


def get_search_query_engine(use_hyde: bool = True) -> CustomQueryEngine:
    logger.log_debug(f"Creating search query engine (with_hyde={use_hyde})")
    engine = RAGStringQueryEngine(use_base_retriever=False, use_search_results=True)
    if use_hyde:
        hyde = HyDEQueryTransform(include_original=True)
        engine = TransformQueryEngine(engine, hyde)
    return engine


def get_query_engine(
    use_hyde: bool = True,
    use_str_formatted_query_engine: bool = True
) -> CustomQueryEngine:
    logger.log_debug(f"Creating query engine (with_hyde={use_hyde}, use_str_formatted_query_engine={use_str_formatted_query_engine})")  # noqa: E501
    if use_str_formatted_query_engine:
        return get_string_query_engine(use_hyde)

    query_engine = RAGQueryEngine()
    if use_hyde:
        hyde = HyDEQueryTransform(include_original=True)
        query_engine = TransformQueryEngine(query_engine, hyde)
    return query_engine

def get_string_query_engine(use_hyde: bool = True) -> CustomQueryEngine:
    logger.log_debug(f"Creating string query engine (with_hyde={use_hyde})")
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
        logger.log_debug(f"RAGQueryEngine.custom_query :: Querying for: <QUERY>{query_str}</QUERY>")
        nodes = self.retriever.retrieve(query_str)
        response_obj = self.response_synthesizer.synthesize(query_str, nodes)
        return response_obj


    async def acustom_query(self, query_str: str):
        logger.log_debug(f"RAGQueryEngine.acustom_query :: Querying for: <QUERY>{query_str}</QUERY>")
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
        vector_store_info: Union[VectorStoreInfo, None] = None,
        use_search_results: bool = False,
    ):
        if use_base_retriever:
            logger.log_debug("RAGStringQueryEngine :: Using base retriever")
            self.retriever = get_base_retriever()
        else:
            if vector_store_info is None:
                raise ValueError("vector_store_info must be provided if use_base_retriever is False.")

            logger.log_debug(f"RAGStringQueryEngine :: Using vector retriever ({vector_store_info})")
            self.retriever = VectorIndexAutoRetriever(
                get_index(),
                vector_store_info=vector_store_info,
                similarity_top_k=VECTOR_INDEX_SIM_TOP_K,
                empty_query_top_k=VECTOR_INDEX_EMPTY_QUERY_TOP_K,  # if only metadata filters are specified, this is the limit
                verbose=VECTOR_INDEX_VERBOSE,
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
        self.use_search_results = use_search_results

        # rag searcher (should not be shared across instances)
        self.rag_searcher: RagSearcher = get_rag_searcher()


    def _build_search_prompt(self, query_str: str, rag_context_str: str) -> ChatPromptTemplate:
        search_contexts = self.rag_searcher.search(query_str)
        system_prompt = rag_query_text.format(
            context="\n\n".join(
                [f"[[citation:{i+1}]] {c['snippet']}" for i, c in enumerate(search_contexts)]
            )
        )
        base_rag_query_text_str = base_rag_query_text.format(
            context_str=rag_context_str,
            query_str=query_str,
        )

        search_chat_message = ChatMessage(
            content=(system_prompt),
            role=MessageRole.SYSTEM,
        )
        rag_context_message = ChatMessage(
            content=(base_rag_query_text_str),
            role=MessageRole.USER,
        )
        return ChatPromptTemplate(
            message_templates=[search_chat_message, rag_context_message]
        )


    def custom_query(self, query_str: str) -> str:
        nodes = self.retriever.retrieve(query_str)

        context_str = "\n\n".join([n.node.get_content() for n in nodes])
        if self.use_search_results:
            prompt = self._build_search_prompt(query_str, context_str)
            prompt_str = str(prompt)
            response = self.llm.complete(prompt_str)
        else:
            response = self.llm.complete(
                self.qa_prompt.format(context_str=context_str, query_str=query_str)
            )

        return str(response)


    async def acustom_query(self, query_str: str) -> Coroutine[Any, Any, str]:
        nodes = await self.retriever.aretrieve(query_str)

        context_str = "\n\n".join([n.node.get_content() for n in nodes])
        if self.use_search_results:
            prompt = self._build_search_prompt(query_str, context_str)
            prompt_str = str(prompt)
            response = await self.llm.acomplete(prompt_str)
        else:
            response = await self.llm.acomplete(
                self.qa_prompt.format(
                    context_str=context_str, query_str=query_str
                )
            )

        return str(response)
