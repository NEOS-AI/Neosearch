import asyncio
from ray import serve
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import torch
import psutil
import logging
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
from pydantic import BaseModel

# custom modules
try:
    from neosearch_ai.configs.embedding_param_manager import (
        ServerParameterManager, RayParameterManager, EmbeddingModelConfig
    )
except ImportError:
    from configs.embedding_param_manager import (
        ServerParameterManager, RayParameterManager, EmbeddingModelConfig
    )


# FastAPI app (for ingress control)
app: FastAPI = FastAPI(
    title="NeoSearch AI Embeddings",
    version="0.3.0",
)

logger = logging.getLogger(__name__)

# Env variables for server
SERVER_MANAGER = ServerParameterManager()
RAY_MANAGER = RayParameterManager()

# Embedding model configuration
EMBEDDING_CONFIG = EmbeddingModelConfig(
    force_torch_single_thread=os.getenv("FORCE_TORCH_SINGLE_THREAD", "False").lower() == "true",
    dynamic_quantization=os.getenv("DYNAMIC_QUANTIZATION", "False").lower() == "true",
    dynamic_quantization_dtype=os.getenv("DYNAMIC_QUANTIZATION_DTYPE", None),
)


class BatchEmbeddings(BaseModel):
    contents: list[str]


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
@serve.ingress(app)
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
        if EMBEDDING_CONFIG.force_torch_single_thread:
            logger.info(
                "FORCE_TORCH_SINGLE_THREAD is enabled. Setting torch to use a single thread."
            )
            num_threads = 1
        torch.set_num_threads(num_threads)
        logger.info(f"Torch is running on {num_threads} threads.")

        logger.info(f"DEVICE: {device}")
        self.device = device
        self.max_batch_size = max_batch_size

        logger.info(f"PRECISION: {precision}")
        self.precision = precision

        self.model_name = model_name
        self.embedding_model = SentenceTransformer(model_name)
        self.embedding_model.to(self.device)

        # Set precision if specified
        if EMBEDDING_CONFIG.dynamic_quantization:
            logger.info(
                f"Dynamic quantization is enabled with dtype: {EMBEDDING_CONFIG.dynamic_quantization_dtype}"
            )
            if EMBEDDING_CONFIG.dynamic_quantization_dtype:
                self.embedding_model = torch.quantization.quantize_dynamic(
                    self.embedding_model,
                    {torch.nn.Linear},
                    dtype=getattr(torch, EMBEDDING_CONFIG.dynamic_quantization_dtype),
                )
            else:
                self.embedding_model = torch.quantization.quantize_dynamic(
                    self.embedding_model, {torch.nn.Linear}
                )

        # thread pool executor for async embedding
        self.executor = ThreadPoolExecutor(max_workers=1)


    def _embed(self, text: str):
        # reference: <https://huggingface.co/sentence-transformers>
        return self.embedding_model.encode(text)

    async def _aembed(self, text: str):
        # reference: <https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor>
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._embed, text)

    def _embed_batch(self, texts: list[str]):
        # reference: <https://huggingface.co/sentence-transformers>
        return self.embedding_model.encode(texts)

    async def _aembed_batch(self, texts: list[str]):
        # reference: <https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor>
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._embed_batch, texts)


    @app.post("/embed/batch")
    async def embed(self, payload: BatchEmbeddings):
        contents = payload.contents
        if len(contents) == 0:
            return {"code": 1, "error": "No contents provided."}
        if len(contents) > self.max_batch_size:
            return {
                "code": 1,
                "error": f"Batch size exceeds maximum of {self.max_batch_size}.",
            }

        if len(contents) == 1:
            embedding: np.ndarray = await self._aembed(contents[0])
            embedding = embedding.tolist()  # convert to list for JSON serialization
            embeddings = [embedding]
        else:
            embeddings = await self._aembed_batch(contents)
            embeddings = embeddings.tolist()  # convert to list for JSON serialization
        return {"code": 0, "embeddings": embeddings}


    def __del__(self):
        # Clean up the model to free up resources
        del self.embedding_model
