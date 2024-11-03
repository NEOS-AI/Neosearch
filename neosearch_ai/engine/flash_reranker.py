from ray import serve
from flashrank import Ranker, RerankRequest
from starlette.requests import Request
import os
import torch
import psutil
import logging

# custom modules
from neosearch_ai.configs.reranker_param_manager import (
    RerankRayParameterManager,
    RerankServerParameterManager,
)


logger = logging.getLogger(__name__)

# Env variables for server
SERVER_MANAGER = RerankServerParameterManager()
RAY_MANAGER = RerankRayParameterManager()


# model names
MODEL_NAMES = {
    "ms-marco-TinyBERT-L-2-v2",
    "ms-marco-MiniLM-L-12-v2",
    "rank-T5-flan",
    "ms-marco-MultiBERT-L-12",
    "ce-esci-MiniLM-L12-v2",
    "rank_zephyr_7b_v1_full",
    "miniReranker_arabic_v1",
}


@serve.deployment(
    ray_actor_options={
        "num_gpus": (
            RAY_MANAGER.num_gpus
            if (
                SERVER_MANAGER.device == "cuda"
            )
            else 0
        ),
    },
    autoscaling_config={
        "min_replicas": RAY_MANAGER.min_replicas,
        "max_replicas": RAY_MANAGER.max_replicas,
    },
)
class FlashRerankDeployment:
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
        logger.info(f"Torch is running on {num_threads} threads.")

        logger.info(f"DEVICE: {device}")
        self.device = device
        self.max_batch_size = max_batch_size

        logger.info(f"PRECISION: {precision}")
        self.precision = precision

        assert model_name in MODEL_NAMES, f"Model name {model_name} not found in {MODEL_NAMES}"
        self.model_name = model_name
        self.reranker = Ranker(model_name)


    def _embed(self, query: str, documents: list[str]):
        rerank_request = RerankRequest(query, documents)
        return self.reranker.rerank(rerank_request)

    async def _aembed(self, query: str, documents: list[str]):
        rerank_request = RerankRequest(query, documents)
        return self.reranker.rerank(rerank_request)

    async def _formulate_response(self, reranked_documents: list[str]):
        return {
            "code": 0,
            "reranked_documents": reranked_documents,
        }

    @serve.batch(max_batch_size=SERVER_MANAGER.max_batch_size)
    async def __call__(self, request: Request):
        payload = await request.json()
        query = payload.get("query")
        documents = payload.get("documents")

        if len(documents) == 0:
            return {"code": 1, "error": "No documents provided."}
        if not query:
            return {"code": 1, "error": "No query provided."}

        if len(documents) == 1:
            # if only one document, don't rerank
            reranked_documents = documents
            return self._formulate_response(reranked_documents)

        if len(documents) > self.max_batch_size:
            return {
                "code": 1,
                "error": f"Batch size exceeds maximum of {self.max_batch_size}.",
            }
        
        reranked_documents = await self._aembed(query, documents)
        return await self._formulate_response(reranked_documents)


    def __del__(self):
        # Clean up the model to free up resources
        del self.reranker
