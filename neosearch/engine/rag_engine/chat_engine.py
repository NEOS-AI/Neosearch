from llama_index.core import PromptTemplate
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.indices.query.query_transform import HyDEQueryTransform
from llama_index.core.query_engine import TransformQueryEngine
from llama_index.core.retrievers import BaseRetriever

# custom module
from neosearch.engine.index import get_index


def _use_hyde(chat_engine, use_hyde: bool = True):
    if use_hyde:
        hyde = HyDEQueryTransform(include_original=True)
        return TransformQueryEngine(chat_engine, hyde)
    return chat_engine


def get_chat_engine(use_hyde: bool = True):
    chat_engine = get_index().as_chat_engine(
        similarity_top_k=3,
        chat_mode="condense_plus_context"
    )
    return _use_hyde(chat_engine, use_hyde)


def get_custom_chat_engine(last_msg: str, chat_history: list, verbose: bool = False, use_hyde: bool = True):
    index = get_index()
    query_engine = index.as_query_engine()

    system_prompt_str = """Answer in same language as the question. If you think the question is ambiguous, please ask for clarification.
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

    return _use_hyde(chat_engine, use_hyde)


def get_retrieval_chat_engine(last_msg, chat_history: list, llm, use_hyde: bool = True):
    llm = get_index().as_llm() #TODO
    retriever: BaseRetriever = get_index().as_retriever() #TODO

    system_prompt_str = """Answer in same language as the question. If you think the question is ambiguous, please ask for clarification.
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
