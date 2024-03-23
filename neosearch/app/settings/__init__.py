from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.settings import Settings
import os

# custom modules
from neosearch.app.utils.configs import Config

from .openai import init_openai
from .ollama import init_ollama
from .llamacpp import init_llamacpp


config = Config()

# key-value pair for LLM settings
LLM_SETTINGS_KV = {
    "openai": init_openai,
    "ollama": init_ollama,
    "llama.cpp": init_llamacpp,
}


def init_llm_settings() -> None:
    llm_config = config.get_llm_configs()
    llm_type = llm_config.get("type", "openai")

    if llm_type in LLM_SETTINGS_KV:
        LLM_SETTINGS_KV[llm_type]()
    else:
        raise ValueError(f"Invalid LLM type: {llm_type}")


def init_settings() -> None:
    init_llm_settings()

    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    Settings.embed_model = OpenAIEmbedding(
        model=embedding_model,
        embed_batch_size=100
    )
    Settings.chunk_size = 1024
    Settings.chunk_overlap = 20
