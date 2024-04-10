from sentence_transformers import SentenceTransformer
import torch
from ray import serve
import starlette.requests


@serve.deployment
class SentenceBert:
    def __init__(self, model_name: str) -> None:
        self.init_model(model_name)
        self.pool = None

    def init_model(self, model_name) -> None:
        device = torch.deivce(
            "cuda" if torch.cuda.is_available() else (
                "metal" if torch.metal.is_available() else "cpu"
            )
        )
        self.model = SentenceTransformer(model_name).to(device)

    async def __call__(self, request: starlette.requests.Request):
        text = await request.body()
        with torch.no_grad():
            vector = self.model.encode(text)
        return {"vector": vector.tolist()}

    def get_model(self) -> SentenceTransformer:
        if self.model is None:
            self.init_model()
        return self.model


def get_sbert_app(model_name: str = "multi-qa-MiniLM-L6-cos-v1"):
    sbert_app = SentenceBert.bind(model_name)
    return sbert_app
