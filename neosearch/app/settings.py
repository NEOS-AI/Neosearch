import os

from llama_index.llms.openai import OpenAI
from llama_index.llms import Ollama
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.settings import Settings

# custom module
from neosearch.app.utils.configs import Configs

config = Configs()

def init_llm_settings() -> None:
    llm_config = config.get_llm_configs()
    llm_type = llm_config.get("type", "openai")

    if llm_type == "openai":
        model = os.getenv("OPENAI_MODEL", "gpt-4")
        Settings.llm = OpenAI(model=model)
    elif llm_type == "ollama":
        model = os.getenv("OLLAMA_MODEL", "mixtral")
        Settings.llm = Ollama(model=model, request_timeout=30.0)
    else:
        raise ValueError(f"Invalid LLM type: {llm_type}")


def init_settings() -> None:
    init_llm_settings()

    Settings.embed_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        embed_batch_size=100
    )
    Settings.chunk_size = 1024
    Settings.chunk_overlap = 20
