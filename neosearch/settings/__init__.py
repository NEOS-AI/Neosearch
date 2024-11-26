from llama_index.core.settings import Settings
import os
from typing import Dict

# custom modules
from neosearch.utils.configs import Config

from .openai import init_openai, init_azure_openai
from .ollama import init_ollama
from .fastembed import init_fastembed
from .huggingface import init_huggingface
from .mistral import init_mistral
from .gemini import init_gemini


config = Config()


def init_settings():
    llm_config = config.get_llm_configs()
    model_type = llm_config.get("type")
    model_provider = os.getenv("MODEL_PROVIDER", model_type)

    match model_provider:
        case "openai":
            init_openai()
        case "groq":
            init_groq()
        case "ollama":
            init_ollama()
        case "anthropic":
            init_anthropic()
        case "gemini":
            init_gemini()
        case "mistral":
            init_mistral()
        case "azure-openai":
            init_azure_openai()
        case "huggingface":
            init_huggingface()
        case "t-systems":
            from .llmhub import init_llmhub

            init_llmhub()

        case _:
            raise ValueError(f"Invalid model provider: {model_provider}")

    Settings.chunk_size = int(os.getenv("CHUNK_SIZE", "1024"))
    Settings.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "20"))


def init_groq():
    try:
        from llama_index.llms.groq import Groq
    except ImportError:
        raise ImportError(
            "Groq support is not installed. Please install it with `poetry add llama-index-llms-groq`"
        )

    Settings.llm = Groq(model=os.getenv("MODEL"))
    # Groq does not provide embeddings, so we use FastEmbed instead
    init_fastembed()


def init_anthropic():
    try:
        from llama_index.llms.anthropic import Anthropic
    except ImportError:
        raise ImportError(
            "Anthropic support is not installed. Please install it with `poetry add llama-index-llms-anthropic`"
        )

    model_map: Dict[str, str] = {
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3-sonnet": "claude-3-sonnet-20240229",
        "claude-3-haiku": "claude-3-haiku-20240307",
        "claude-2.1": "claude-2.1",
        "claude-instant-1.2": "claude-instant-1.2",
    }

    Settings.llm = Anthropic(model=model_map[os.getenv("MODEL")])
    # Anthropic does not provide embeddings, so we use FastEmbed instead
    init_fastembed()
