from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from llama_index import LangchainEmbedding


def get_embedding_model(model_name: str = "sentence-transformers/all-mpnet-base-v2"):
    return LangchainEmbedding(HuggingFaceEmbeddings(model_name=model_name))
