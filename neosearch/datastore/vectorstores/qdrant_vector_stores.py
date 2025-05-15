import os
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore

# custom module
from neosearch.utils.singleton import Singleton

from .base import BaseVectorStore


class QdrantVectorStoreContainer(BaseVectorStore, metaclass=Singleton):
    def __init__(self):
        self._build_vector_store()

    def _build_vector_store(self):
        self.vec_db_client = QdrantClient(
            url=os.environ.get("QDRANT_URL"),
            api_key=os.environ.get("QDRANT_API_KEY")
        )
        self.store = QdrantVectorStore(self.vec_db_client)

    def get_store(self):
        return self.store

    def refresh(self):
        self._build_vector_store()
        return self.store
