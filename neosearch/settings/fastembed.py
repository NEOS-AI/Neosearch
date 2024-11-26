import os
from typing import Dict
from llama_index.core.settings import Settings


def init_fastembed():
    try:
        from llama_index.embeddings.fastembed import FastEmbedEmbedding
    except ImportError:
        raise ImportError(
            "FastEmbed support is not installed. Please install it with `poetry add llama-index-embeddings-fastembed`"
        )

    embed_model_map: Dict[str, str] = {
        # Small and multilingual
        "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
        # Large and multilingual
        "paraphrase-multilingual-mpnet-base-v2": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
    }

    embedding_model = os.getenv("EMBEDDING_MODEL")
    if embedding_model is None:
        raise ValueError("EMBEDDING_MODEL environment variable is not set")

    # This will download the model automatically if it is not already downloaded
    Settings.embed_model = FastEmbedEmbedding(
        model_name=embed_model_map[embedding_model]
    )
