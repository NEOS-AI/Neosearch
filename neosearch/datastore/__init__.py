from typing import Union

# custom modules
from neosearch.datastore import providers, vectordb
from neosearch.datastore.datastore import Client, create


Config = Union[
    providers.firestore.Config,
    providers.postgres.Config,
    providers.cloudsql_postgres.Config,
]

__ALL__ = [
    Client,
    Config,
    create,
    providers,
    vectordb
]
