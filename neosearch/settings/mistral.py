import os
from llama_index.core.settings import Settings


def init_mistral():
    from llama_index.embeddings.mistralai import MistralAIEmbedding
    from llama_index.llms.mistralai import MistralAI

    Settings.llm = MistralAI(model=os.getenv("MODEL"))
    Settings.embed_model = MistralAIEmbedding(model_name=os.getenv("EMBEDDING_MODEL"))
