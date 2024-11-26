from llama_index.llms.openai import OpenAI
from llama_index.core.settings import Settings
import os
from llama_index.core.constants import DEFAULT_TEMPERATURE
from llama_index.embeddings.openai import OpenAIEmbedding


def init_openai():
    max_tokens = os.getenv("LLM_MAX_TOKENS")
    if max_tokens == '':
        max_tokens = None

    Settings.llm = OpenAI(
        model=os.getenv("MODEL", "gpt-4o-mini"),
        temperature=float(os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE)),
        max_tokens=int(max_tokens) if max_tokens is not None else None,
    )

    dimensions = os.getenv("EMBEDDING_DIM")
    #TODO Settings.embed_model = OpenAIEmbedding(
    Settings._embed_model = OpenAIEmbedding(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        dimensions=int(dimensions) if dimensions is not None else None,
    )


def init_azure_openai():
    try:
        from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
        from llama_index.llms.azure_openai import AzureOpenAI
    except ImportError:
        raise ImportError(
            "Azure OpenAI support is not installed. Please install it with `poetry add llama-index-llms-azure-openai` and `poetry add llama-index-embeddings-azure-openai`"
        )

    llm_deployment = os.environ["AZURE_OPENAI_LLM_DEPLOYMENT"]
    embedding_deployment = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
    max_tokens = os.getenv("LLM_MAX_TOKENS")
    temperature = os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE)
    dimensions = os.getenv("EMBEDDING_DIM")

    azure_config = {
        "api_key": os.environ["AZURE_OPENAI_API_KEY"],
        "azure_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"],
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION")
        or os.getenv("OPENAI_API_VERSION"),
    }

    Settings.llm = AzureOpenAI(
        model=os.getenv("MODEL"),
        max_tokens=int(max_tokens) if max_tokens is not None else None,
        temperature=float(temperature),
        deployment_name=llm_deployment,
        **azure_config,
    )

    Settings.embed_model = AzureOpenAIEmbedding(
        model=os.getenv("EMBEDDING_MODEL"),
        dimensions=int(dimensions) if dimensions is not None else None,
        deployment_name=embedding_deployment,
        **azure_config,
    )
