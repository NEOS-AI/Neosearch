from llama_index.core.settings import Settings
import os
from typing import Dict
from enum import Enum

# custom modules
from neosearch.utils.configs import Config

from .openai import init_openai, init_azure_openai, get_openai_llm, OPENAI_MODEL_SET
from .ollama import init_ollama
from .fastembed import init_fastembed
from .huggingface import init_huggingface
from .mistral import init_mistral
from .gemini import init_gemini


class LlmType(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GROQ = "groq"
    GEMINI = "gemini"
    MISTRAL = "mistral"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    AZURE_OPENAI = "azure-openai"
    T_SYSTEMS = "t-systems"


config = Config()


def get_llm_model_by_id(model_id: str):
    if Settings.llm.model == model_id:
        return Settings.llm
    if model_id in OPENAI_MODEL_SET:
        return get_openai_llm(model_id)

    # use default model if no matching model is found
    return Settings.llm

def init_settings():
    llm_config = config.get_llm_configs()
    model_type = llm_config.get("type")
    model_provider = os.getenv("MODEL_PROVIDER", model_type)

    match model_provider:
        case LlmType.OPENAI.value:
            init_openai()
        case LlmType.GROQ.value:
            init_groq()
        case LlmType.OLLAMA.value:
            init_ollama()
        case LlmType.ANTHROPIC.value:
            init_anthropic()
        case LlmType.GEMINI.value:
            init_gemini()
        case LlmType.MISTRAL.value:
            init_mistral()
        case LlmType.AZURE_OPENAI.value:
            init_azure_openai()
        case LlmType.HUGGINGFACE.value:
            init_huggingface()
        case LlmType.T_SYSTEMS.value:
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
        "claude-3.5": "claude-3-5-sonnet-20240620",
        "claude-3.7": "claude-3-7-sonnet-latest",
    }

    Settings.llm = Anthropic(model=model_map[os.getenv("ANTHROPIC_MODEL")])
    # Anthropic does not provide embeddings, so we use FastEmbed instead
    init_fastembed()
