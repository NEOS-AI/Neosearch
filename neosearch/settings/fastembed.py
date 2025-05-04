import os
from llama_index.core.settings import Settings


def init_fastembed(
    model_name: str = "BAAI/bge-m3",
    max_length: int = 512,
    threads: int = 4,
):
    try:
        from llama_index.embeddings.fastembed import FastEmbedEmbedding
    except ImportError:
        raise ImportError(
            "FastEmbed support is not installed. Please install it with `poetry add llama-index-embeddings-fastembed`"
        )

    embedding_model = os.getenv("FASTEMBED_EMBEDDING_MODEL", model_name)
    if embedding_model is None:
        raise ValueError("EMBEDDING_MODEL environment variable is not set")

    # This will download the model automatically if it is not already downloaded
    Settings.embed_model = FastEmbedEmbedding(
        model_name=embedding_model,
        max_length=max_length,
        threads=threads,
    )
