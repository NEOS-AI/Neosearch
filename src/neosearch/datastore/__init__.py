from typing import Union

# custom modules
from . import providers
from .datastore import Client, create


Config = Union[
    providers.firestore.Config,
    providers.postgres.Config,
    providers.cloudsql_postgres.Config,
]

__ALL__ = [Client, Config, create, providers]
