from llama_index import ServiceContext
from ray import serve

from starlette.requests import Request

# custom modules
from ray_crawler.engine.embeddings import get_embedding_model


@serve.deployment
class EmbeddingDeployment:
    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        self.embedding_model = get_embedding_model(model_name)
        self.service_context = ServiceContext.from_defaults(embed_model=self.embedding_model)

        #TODO

    def _embed(self, text: str):
        return self.embedding_model.embed(text)

    async def __call__(self, request: Request):
        pass
