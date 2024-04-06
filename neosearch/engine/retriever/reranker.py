from llama_index.core.postprocessor import SentenceTransformerRerank


def get_base_reranker():
    reranker = SentenceTransformerRerank(
        top_n=4,
        model="BAAI/bge-reranker-base",
    )
    return reranker
