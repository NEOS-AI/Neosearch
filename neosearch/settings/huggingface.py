import os
from llama_index.core.settings import Settings


def init_huggingface():
    try:
        from llama_index.llms.huggingface import HuggingFaceLLM
    except ImportError:
        raise ImportError(
            "Hugging Face support is not installed. Please install it with `poetry add llama-index-llms-huggingface` and `poetry add llama-index-embeddings-huggingface`"
        )

    Settings.llm = HuggingFaceLLM(
        model_name=os.getenv("MODEL"),
        tokenizer_name=os.getenv("MODEL"),
    )
    init_huggingface_embedding()


def init_huggingface_embedding():
    try:
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    except ImportError:
        raise ImportError(
            "Hugging Face support is not installed. Please install it with `poetry add llama-index-embeddings-huggingface`"
        )

    embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    backend = os.getenv("EMBEDDING_BACKEND", "onnx")  # "torch", "onnx", or "openvino"
    trust_remote_code = (
        os.getenv("EMBEDDING_TRUST_REMOTE_CODE", "false").lower() == "true"
    )

    Settings.embed_model = HuggingFaceEmbedding(
        model_name=embedding_model,
        trust_remote_code=trust_remote_code,
        backend=backend,
    )
