import sys
import ray
from ray import serve
import torch
import multiprocessing

sys.path.append("..")

# custom modules
from engine.embeddings import EmbeddingDeployment


def deploy_embedding_server():
    # Deploy the Ray Serve application.
    deployment = EmbeddingDeployment.bind()
    serve.run(
        deployment,
        blocking=False,
        name="embedding_server",
        route_prefix="/embed"
    )


def main(
    use_custom_server: bool = True,
    num_cpus: int = 2,
    num_gpus: int = 0
) -> None:
    if use_custom_server:
        # Set PyTorch internal threads to 1 to avoid thread contention.
        torch.set_num_threads(1)

        # init ray with the custom configuration
        ray.init(
            num_cpus=num_cpus,
            num_gpus=num_gpus,
        )

        deploy_embedding_server()
    #TODO crawl, extract, and index the content of the URL


if __name__ == "__main__":
    num_of_cpus = multiprocessing.cpu_count()
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        # get num of gpus
        num_of_gpus = torch.cuda.device_count()
        main(num_cpus=num_of_cpus, num_gpus=num_of_gpus)
    else:
        main(num_cpus=num_of_cpus)
