from ray import serve

from starlette.requests import Request

# custom modules
from .embeddings import get_embedding_model


@serve.deployment
class EmbeddingDeployment:
    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        self.embedding_model = get_embedding_model(model_name)

    def _embed(self, text: str):
        return self.embedding_model.get_text_embedding(text)

    def _embed_batch(self, texts: list[str]):
        return self.embedding_model.get_text_embeddings(texts)


    async def _aembed(self, text):
        return self.embedding_model.aget_text_embedding(text)


    async def __call__(self, request: Request):
        payload = await request.json()
        contents = payload.get("contents", [])
        if len(contents) == 0:
            return {"code": 1, "error": "No contents provided."}

        if len(contents) == 1:
            embedding = await self._aembed(contents[0])
            embeddings = [embedding]
        else:
            embeddings = self._embed_batch(contents)
        return {"code": 0, "embeddings": embeddings}
