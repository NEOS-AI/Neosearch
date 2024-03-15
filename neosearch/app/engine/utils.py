
# custom module
from neosearch.app.engine.vectorstores.pg_vector_stores import PgVectorStoreContainer


def init_pg_vector_store_from_env():
    # use singleton to ensure only one instance of the vector store is created
    vectorstore = PgVectorStoreContainer()
    return vectorstore.get_store()
