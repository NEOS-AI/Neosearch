import os
from llama_index.vector_stores.milvus import MilvusVectorStore

# custom module
from neosearch.utils.singleton import Singleton

from .base import BaseVectorStore


class PgVectorStoreContainer(BaseVectorStore, metaclass=Singleton):
    """
    A singleton class to hold the vector store instance.

    The vector store instance creates a connection pool to the database.
    So, if we create multiple instances of the vector store, we will end up creating multiple connection pools.
    This class ensures that only one instance of the vector store is created and shared across the application.

    As postgres creates a new process for each connection, we should avoid creating multiple connection pools.
    """  # noqa: E501
    def __init__(self):
        self._build_vector_store()

    def _build_vector_store(self):
        milvus_uri = os.getenv("MILVUS_URI")
        milvus_api_key = os.getenv("MILVUS_API_KEY")
        milvus_collection = os.getenv("MILVUS_COLLECTION")
        milvus_dimension = int(os.getenv("MILVUS_DIMENSION"))

        if not all([milvus_uri, milvus_api_key, milvus_collection, milvus_dimension]):
            raise ValueError("Missing required environment variables.")

        # Create MilvusVectorStore 
        self.store = MilvusVectorStore(
            uri=milvus_uri,
            token=milvus_api_key,
            collection_name=milvus_collection,
            dim=milvus_dimension, # mandatory for new collection creation
            overwrite=True, # mandatory for new collection creation 
        )

    def get_store(self):
        return self.store

    def refresh(self):
        self._build_vector_store()
        return self.store
