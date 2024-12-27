from llama_index.core import PromptTemplate
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.indices.query.query_transform import HyDEQueryTransform
from llama_index.core.query_engine import TransformQueryEngine
from llama_index.core.retrievers import BaseRetriever

# custom module
from neosearch.settings import Settings
from neosearch.engine.index import get_index
from neosearch.engine.retriever.searxng_retriever import SearxngRetriever


def _use_hyde(query_engine, use_hyde: bool):
    if use_hyde:
        hyde = HyDEQueryTransform(include_original=True)
        return TransformQueryEngine(query_engine, hyde)
    return query_engine


def get_chat_engine(use_hyde: bool = False):
    index = get_index()
    query_engine = index.as_query_engine()
    query_engine = _use_hyde(query_engine, use_hyde)
    chat_engine = CondensePlusContextChatEngine.from_defaults(query_engine=query_engine)
    return chat_engine


def get_custom_chat_engine(last_msg: str, chat_history: list, verbose: bool = False, use_hyde: bool = False):
    index = get_index()
    query_engine = index.as_query_engine()
    query_engine = _use_hyde(query_engine, use_hyde)

    system_prompt_str = """As a AI based search engine, you are expected to provide the most relevant information to the user.
    Answer in same language as the question. If you think the question is ambiguous, please ask for clarification.
    If you think the question is too violent/sexual/illegal, please let the user know that you can't answer it due to policy reasons.
    """
    custom_prompt = PromptTemplate(system_prompt_str)
    user_prompt = PromptTemplate(last_msg)

    chat_engine = CondensePlusContextChatEngine.from_defaults(
        query_engine=query_engine,
        system_prompt=custom_prompt,
        condense_prompt=user_prompt,
        chat_history=chat_history,
        verbose=verbose,
    )

    return chat_engine


def get_searxng_chat_engine(last_msg, chat_history: list):
    llm = Settings.llm

    index = get_index()
    index_retriever = index.as_retriever()
    retriever: BaseRetriever = SearxngRetriever(
        vector_retriever=index_retriever,
        use_with_vector_search=True
    )

    refine_prompt_str = """Your task is to refine a query to ensure it is highly effective for retrieving relevant search results. \n
    Analyze the given input to grasp the core semantic intent or meaning. \n
    Original Query:
    \n ------- \n
    {query_str}
    """

    system_prompt_str = """As a AI based search engine, you are expected to provide the most relevant information to the user.
    Answer in same language as the question. If you think the question is ambiguous, please ask for clarification.
    If you think the question is too violent/sexual/illegal, please let the user know that you can't answer it due to policy reasons.
    """

    custom_prompt = PromptTemplate(system_prompt_str)
    refine_prompt = PromptTemplate(refine_prompt_str)

    chat_engine = CondensePlusContextChatEngine.from_defaults(
        retriever=retriever,
        llm=llm,
        context_prompt=custom_prompt,
        context_refine_prompt=refine_prompt,
        condense_prompt=custom_prompt,
        chat_history=chat_history,
    )
    return chat_engine
