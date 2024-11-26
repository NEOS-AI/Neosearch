from llama_index.llms.ollama.base import DEFAULT_REQUEST_TIMEOUT, Ollama
from llama_index.core.settings import Settings
import os


def init_ollama():
    try:
        from llama_index.embeddings.ollama import OllamaEmbedding
    except ImportError:
        raise ImportError(
            "Ollama support is not installed. Please install it with `poetry add llama-index-llms-ollama` and `poetry add llama-index-embeddings-ollama`"
        )

    base_url = os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434"
    request_timeout = float(
        os.getenv("OLLAMA_REQUEST_TIMEOUT", DEFAULT_REQUEST_TIMEOUT)
    )
    Settings.embed_model = OllamaEmbedding(
        base_url=base_url,
        model_name=os.getenv("EMBEDDING_MODEL"),
    )
    Settings.llm = Ollama(
        base_url=base_url, model=os.getenv("MODEL"), request_timeout=request_timeout
    )
