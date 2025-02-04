from llama_index.core import PromptTemplate
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.indices.query.query_transform import HyDEQueryTransform
from llama_index.core.query_engine import TransformQueryEngine
from llama_index.core.retrievers import BaseRetriever

# custom module
from neosearch.settings import Settings
from neosearch.engine.index import get_index
from neosearch.engine.retriever.searxng import SearxngRetriever
from neosearch.engine.prompts.chat import (
    DEFAULT_CONDENSE_PROMPT_TEMPLATE,
    DEFAULT_CONTEXT_PROMPT_TEMPLATE,
    DEFAULT_CONTEXT_REFINE_PROMPT_TEMPLATE,
)
from neosearch.engine.reranker.cohere import get_cohere_rerank


def _use_hyde(query_engine, use_hyde: bool):
    if use_hyde:
        hyde = HyDEQueryTransform(include_original=True)
        return TransformQueryEngine(query_engine, hyde)
    return query_engine


def get_chat_engine(use_hyde: bool = False, use_cohere_rerank: bool = False, cohere_top_n: int = 10):
    index = get_index()
    if use_cohere_rerank:
        cohere_rerank = get_cohere_rerank(top_n=cohere_top_n)
        query_engine = index.as_query_engine(
            similarity_top_k=cohere_top_n,
            node_postprocessors=[cohere_rerank],
        )
    else:
        query_engine = index.as_query_engine()
    query_engine = _use_hyde(query_engine, use_hyde)
    chat_engine = CondensePlusContextChatEngine.from_defaults(query_engine=query_engine)
    return chat_engine


def get_custom_chat_engine(llm = Settings.llm, verbose: bool = False):
    index = get_index()
    index_retriever = index.as_retriever()
    retriever: BaseRetriever = SearxngRetriever(
        vector_retriever=index_retriever,
        use_with_vector_search=True
    )

    context_prompt = PromptTemplate(DEFAULT_CONTEXT_PROMPT_TEMPLATE)
    refine_prompt = PromptTemplate(DEFAULT_CONTEXT_REFINE_PROMPT_TEMPLATE)
    condense_prompt = PromptTemplate(DEFAULT_CONDENSE_PROMPT_TEMPLATE)

    chat_engine = CondensePlusContextChatEngine.from_defaults(
        retriever=retriever,
        llm=llm,
        context_prompt=context_prompt,
        context_refine_prompt=refine_prompt,
        condense_prompt=condense_prompt,
        verbose=verbose,
    )
    return chat_engine


def get_searxng_chat_engine(verbose: bool = False):
    llm = Settings.llm

    index = get_index()
    index_retriever = index.as_retriever()
    retriever: BaseRetriever = SearxngRetriever(
        vector_retriever=index_retriever,
        use_with_vector_search=True
    )

    context_prompt = PromptTemplate(DEFAULT_CONTEXT_PROMPT_TEMPLATE)
    refine_prompt = PromptTemplate(DEFAULT_CONTEXT_REFINE_PROMPT_TEMPLATE)
    condense_prompt = PromptTemplate(DEFAULT_CONDENSE_PROMPT_TEMPLATE)

    chat_engine = CondensePlusContextChatEngine.from_defaults(
        retriever=retriever,
        llm=llm,
        context_prompt=context_prompt,
        context_refine_prompt=refine_prompt,
        condense_prompt=condense_prompt,
        verbose=verbose,
    )
    return chat_engine
