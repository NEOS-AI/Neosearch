import sys
import ray
from ray import serve
import torch

sys.path.append("..")

# custom modules
from engine.embeddings import EmbeddingDeployment
from utils.config import NeosAiConfig


def deploy_embedding_server(
    blocking: bool = False,
    name: str = "embedding_server",
    route_prefix: str = "/embed"
) -> None:
    # Deploy the Ray Serve application.
    deployment = EmbeddingDeployment.bind()
    serve.run(
        deployment,
        blocking=blocking,
        name=name,
        route_prefix=route_prefix
    )


def init_and_deploy_hpc_nodes(
    num_cpus: int = 2,
    num_gpus: int = 0,
    avoid_thread_contention: bool = True
) -> None:
    if avoid_thread_contention:
        # Set PyTorch internal threads to 1 to avoid thread contention.
        torch.set_num_threads(1)

    # init ray with the custom configuration
    ray.init(
        num_cpus=num_cpus,
        num_gpus=num_gpus,
    )

    deploy_embedding_server()


if __name__ == "__main__":
    config = NeosAiConfig()
    if config.cuda_available:
        if config.use_llm2vec:
            #TODO use vllm to serve the model
            pass

        # get num of gpus
        num_of_gpus = torch.cuda.device_count()
        init_and_deploy_hpc_nodes(
            num_cpus=config.num_of_cpus,
            num_gpus=num_of_gpus,
            avoid_thread_contention=config.avoid_thread_contention
        )
    else:
        init_and_deploy_hpc_nodes(
            num_cpus=config.num_of_cpus,
            avoid_thread_contention=config.avoid_thread_contention
        )
