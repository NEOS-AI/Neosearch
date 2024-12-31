import os
from llama_index.postprocessor.cohere_rerank import CohereRerank


api_key = os.getenv("COHERE_API_KEY", None)


def get_cohere_rerank(top_n: int = 2):
    if api_key is None:
        raise ValueError("COHERE_API_KEY is not set")
    return CohereRerank(api_key=api_key, top_n=top_n)
