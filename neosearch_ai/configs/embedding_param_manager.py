import os
from dataclasses import dataclass
import torch


@dataclass
class ServerParameterManager:
    model_name: str = os.environ.get("MODEL_NAME", "answerdotai/ModernBERT-large")
    device: str = os.environ.get("DEVICE", "cpu")
    precision: int | str | None = os.environ.get("PRECISION", "fp32")
    retriever_batch_size: int = int(os.environ.get("RETRIEVER_BATCH_SIZE", 32))
    reader_batch_size: int = int(os.environ.get("READER_BATCH_SIZE", 32))
    max_batch_size: int = int(os.environ.get("MAX_BATCH_SIZE", 32))


class RayParameterManager:
    def __init__(self) -> None:
        self.num_gpus = int(os.environ.get("NUM_GPUS", torch.cuda.device_count()))
        self.min_replicas = int(os.environ.get("MIN_REPLICAS", 1))
        self.max_replicas = int(os.environ.get("MAX_REPLICAS", 1))
