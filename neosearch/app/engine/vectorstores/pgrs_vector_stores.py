import os
from llama_index.vector_stores.pgvecto_rs import PGVectoRsStore
from urllib.parse import urlparse
from pgvecto_rs.sdk import PGVectoRs

# custom module
from neosearch.app.engine.constants import PGVECTOR_SCHEMA, PGVECTOR_TABLE
from neosearch.app.engine.vectorstores.base import BaseVectorStore
from neosearch.app.utils.singleton import Singleton


class PgRsVectorStoreContainer(BaseVectorStore, metaclass=Singleton):
    """
    A singleton class to hold the vector store instance.

    The vector store instance creates a connection pool to the database.
    So, if we create multiple instances of the vector store, we will end up creating multiple connection pools.
    This class ensures that only one instance of the vector store is created and shared across the application.

    As postgres creates a new process for each connection, we should avoid creating multiple connection pools.
    """  # noqa: E501
    def __init__(self, collection_name: str = PGVECTOR_TABLE):
        self.collection_name = collection_name
        self._build_vector_store()

    def _build_vector_store(self):
        original_conn_string = os.environ.get("PG_CONNECTION_STRING")
        if original_conn_string is None or original_conn_string == "":
            raise ValueError("PG_CONNECTION_STRING environment variable is not set.")

        # The PGVectorStore requires both two connection strings, one for psycopg2 and one for asyncpg
        # Update the configured scheme with the psycopg2 and asyncpg schemes
        original_scheme = urlparse(original_conn_string).scheme + "://"
        self.conn_string = original_conn_string.replace(
            original_scheme, "postgresql+psycopg2://"
        )
        self.async_conn_string = original_conn_string.replace(
            original_scheme, "postgresql+asyncpg://"
        )

        url = f"{self.conn_string}/{PGVECTOR_SCHEMA}"
        self.client = PGVectoRs(
            db_url=url,
            collection_name=self.collection_name,
            dimension=1536,  # Using OpenAI’s text-embedding-ada-002
        )
        self.store = PGVectoRsStore(self.client)

    def get_store(self):
        return self.store

    def refresh(self):
        self._build_vector_store()
        return self.store
