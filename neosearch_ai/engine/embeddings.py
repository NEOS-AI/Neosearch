from ray import serve
from sentence_transformers import SentenceTransformer
from starlette.requests import Request
import os
import torch
import psutil

# custom modules
from neosearch_ai.utils.logger import Logger
from .param_manager import ServerParameterManager, RayParameterManager


logger = Logger()

# Env variables for server
SERVER_MANAGER = ServerParameterManager()
RAY_MANAGER = RayParameterManager()


@serve.deployment(
    ray_actor_options={
        "num_gpus": (
            RAY_MANAGER.num_gpus
            if (
                SERVER_MANAGER.device == "cuda"
            )
            else 0
        )
    },
    autoscaling_config={
        "min_replicas": RAY_MANAGER.min_replicas,
        "max_replicas": RAY_MANAGER.max_replicas,
    },
)
class EmbeddingDeployment:
    def __init__(
        self,
        model_name: str = SERVER_MANAGER.model_name,
        device: str = SERVER_MANAGER.device,
        precision: str | int | torch.dtype = SERVER_MANAGER.precision,
        max_batch_size: int = SERVER_MANAGER.max_batch_size,
        **kwargs,
    ):
        num_threads = os.getenv("TORCH_NUM_THREADS", psutil.cpu_count(logical=False))
        torch.set_num_threads(num_threads)
        logger.log_info(f"Torch is running on {num_threads} threads.")

        logger.log_info(f"DEVICE: {device}")
        self.device = device
        self.max_batch_size = max_batch_size

        logger.log_info(f"PRECISION: {precision}")
        self.precision = precision

        self.model_name = model_name
        self.embedding_model = SentenceTransformer(model_name)


    def _embed(self, text: str):
        return self.embedding_model.get_text_embedding(text)

    async def _aembed(self, text: str):
        return self._embed(text)

    def _embed_batch(self, texts: list[str]):
        return self.embedding_model.get_text_embeddings(texts)


    async def __call__(self, request: Request):
        payload = await request.json()
        contents = payload.get("contents", [])
        if len(contents) == 0:
            return {"code": 1, "error": "No contents provided."}
        if len(contents) > self.max_batch_size:
            return {
                "code": 1,
                "error": f"Batch size exceeds maximum of {self.max_batch_size}.",
            }

        if len(contents) == 1:
            embedding = await self._aembed(contents[0])
            embeddings = [embedding]
        else:
            embeddings = self._embed_batch(contents)
        return {"code": 0, "embeddings": embeddings}
