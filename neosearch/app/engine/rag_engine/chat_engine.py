from llama_index.core.indices.query.query_transform import HyDEQueryTransform
from llama_index.core.query_engine import TransformQueryEngine

# custom module
from neosearch.app.engine.index import get_index


def get_chat_engine(use_hyde: bool = False):
    chat_engine = get_index().as_chat_engine(
        similarity_top_k=3,
        chat_mode="condense_plus_context"
    )
    if use_hyde:
        hyde = HyDEQueryTransform(include_original=True)
        chat_engine = TransformQueryEngine(chat_engine, hyde)
    return chat_engine
