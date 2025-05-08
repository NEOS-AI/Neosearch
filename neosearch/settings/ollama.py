from llama_index.llms.ollama.base import DEFAULT_REQUEST_TIMEOUT, Ollama
from llama_index.core.settings import Settings
import os

# custom modules
from neosearch.constants.embeddings import OLLAMA_EMBEDDING_MODEL_BASE


def init_ollama_embedding():
    try:
        from llama_index.embeddings.ollama import OllamaEmbedding
    except ImportError:
        raise ImportError(
            "Ollama support is not installed. Please install it with `poetry add llama-index-llms-ollama` and `poetry add llama-index-embeddings-ollama`"
        )
    base_url = os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434"
    Settings.embed_model = OllamaEmbedding(
        base_url=base_url,
        model_name=os.getenv("OLLAMA_EMBEDDING_MODEL", OLLAMA_EMBEDDING_MODEL_BASE),
    )


def init_ollama():
    base_url = os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434"
    request_timeout = float(
        os.getenv("OLLAMA_REQUEST_TIMEOUT", DEFAULT_REQUEST_TIMEOUT)
    )
    init_ollama_embedding()
    Settings.llm = Ollama(
        base_url=base_url, model=os.getenv("OLLAMA_MODEL"), request_timeout=request_timeout
    )
