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
from neosearch.app.engine.index import get_index
from neosearch.app.engine.retriever.base import get_base_retriever


def get_query_engine(use_hyde: bool = True) -> CustomQueryEngine:
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

    def __init__(self, use_base_retriever: bool = True, vector_store_info: VectorStoreInfo = None):
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


class RAGStringQueryEngine(CustomQueryEngine):
    """RAG String Query Engine."""

    retriever: BaseRetriever
    response_synthesizer: BaseSynthesizer
    llm: OpenAI
    qa_prompt: PromptTemplate

    def __init__(self, use_base_retriever: bool = True, vector_store_info: VectorStoreInfo = None):
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

    def custom_query(self, query_str: str):
        nodes = self.retriever.retrieve(query_str)

        context_str = "\n\n".join([n.node.get_content() for n in nodes])
        response = self.llm.complete(
            self.qa_prompt.format(context_str=context_str, query_str=query_str)
        )

        return str(response)
