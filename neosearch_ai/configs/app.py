from dataclasses import dataclass
import torch
import multiprocessing


@dataclass
class NeosAiConfig:
    num_of_cpus: int = multiprocessing.cpu_count()
    cuda_available: bool = torch.cuda.is_available()
    use_llm2vec: bool = False
    avoid_thread_contention: bool = True
    run_monitoring: bool = True
    monitoring_port: int = 8518
