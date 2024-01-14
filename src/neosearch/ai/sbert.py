from concurrent.futures import ProcessPoolExecutor
from sentence_transformers import SentenceTransformer
import torch
import ray
from ray import serve

# custom modules
from neosearch.utils import Singleton


class SentenceBert(metaclass=Singleton):
    def __init__(self) -> None:
        self.init_model()
        self.pool = None

    def init_model(self) -> None:
        device = torch.deivce(
            "cuda" if torch.cuda.is_available() else (
                "metal" if torch.metal.is_available() else "cpu"
            )
        )
        self.model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1').to(device)

    async def __call__(self, request):
        text = await request.body()
        with torch.no_grad():
            vector = self.model.encode(text)
        return {"vector": vector.tolist()}

    def get_model(self) -> SentenceTransformer:
        if self.model is None:
            self.init_model()
        return self.model

    def get_process_pool(self) -> ProcessPoolExecutor:
        if self.pool is None:
            self.pool = ProcessPoolExecutor(max_workers=1, initializer=self.get_model)
        return self.pool


def init_sbert_ray_serve(init_ray:bool = True):
    if init_ray:
        ray.init()
        serve.start()
    serve.create_backend("sbert", SentenceBert)
    serve.create_endpoint("sbert", backend="sbert", route="/sbert")
