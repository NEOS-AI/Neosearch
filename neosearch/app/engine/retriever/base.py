from llama_index.core.retrievers import BaseRetriever

# custom modules
from neosearch.app.engine.index import get_index


def get_base_retriever() -> BaseRetriever:
    return get_index().as_retriever()
