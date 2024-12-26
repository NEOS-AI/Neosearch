from llama_index.core import PromptTemplate
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.indices.query.query_transform import HyDEQueryTransform
from llama_index.core.query_engine import TransformQueryEngine
from llama_index.core.retrievers import BaseRetriever
from llama_index.llms.openai import OpenAI

# custom module
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


def get_searxng_chat_engine(last_msg, chat_history: list, llm, use_hyde: bool = True):
    llm = OpenAI(model="gpt-4o")

    index = get_index()
    index_retriever = index.as_retriever()
    retriever: BaseRetriever = SearxngRetriever(
        vector_retriever=index_retriever,
        use_with_vector_search=True
    )

    system_prompt_str = """As a AI based search engine, you are expected to provide the most relevant information to the user.
    Answer in same language as the question. If you think the question is ambiguous, please ask for clarification.
    If you think the question is too violent/sexual/illegal, please let the user know that you can't answer it due to policy reasons.
    """
    custom_prompt = PromptTemplate(system_prompt_str)
    user_prompt = PromptTemplate(last_msg)

    chat_engine = CondensePlusContextChatEngine.from_defaults(
        retriever=retriever,
        llm=llm,
        system_prompt=custom_prompt,
        condense_prompt=user_prompt,
        chat_history=chat_history,
    )

    return _use_hyde(chat_engine, use_hyde)
