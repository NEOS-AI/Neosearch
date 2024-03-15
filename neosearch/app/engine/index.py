from llama_index.core.indices.vector_store import VectorStoreIndex

# custom module
from neosearch.app.engine.utils import init_pg_vector_store_from_env
from neosearch.app.utils.logging import Logger

logger = Logger()


def get_pg_index():
    logger.log_info("Connecting to index from PGVector...")
    store = init_pg_vector_store_from_env()
    index = VectorStoreIndex.from_vector_store(store, use_async=True)
    logger.log_info("Finished connecting to index from PGVector.")
    return index

def get_index(vector_store_type: str = "pg") -> VectorStoreIndex:
    if vector_store_type == "pg":
        return get_pg_index()
    else:
        raise ValueError(f"Invalid vector store type: {vector_store_type}")
