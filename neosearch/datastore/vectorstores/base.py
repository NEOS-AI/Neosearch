from abc import abstractmethod

# custom module
from neosearch.utils.singleton import Singleton


class BaseVectorStore(metaclass=Singleton):
    @abstractmethod
    def _build_vector_store(self):
        pass

    @abstractmethod
    def get_store(self):
        pass

    @abstractmethod
    def refresh(self):
        pass
