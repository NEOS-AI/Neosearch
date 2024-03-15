from abc import ABC, abstractmethod

# custom module
from neosearch.app.utils.singleton import Singleton


class BaseVectorStore(ABC, metaclass=Singleton):
    @abstractmethod
    def _build_vector_store(self):
        pass

    @abstractmethod
    def get_store(self):
        pass

    @abstractmethod
    def refresh(self):
        pass
