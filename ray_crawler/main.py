import sys
import ray
from ray import serve
import torch
import multiprocessing
import os
from dotenv import load_dotenv

sys.path.append("..")

# custom modules
from engine.deployment import EmbeddingDeployment
from utils import extract_url_content


load_dotenv()
FOR_TEST = os.getenv("FOR_TEST", "0") == "1"


def url_crawl_test(output_format: str = "markdown"):
    url = "https://namu.wiki/w/%EC%95%84%EB%9D%BC%ED%95%98%EC%8B%9C%20%ED%83%80%EB%B9%84"
    print(extract_url_content(url, output_format=output_format))


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


def main():
    num_of_cpus = multiprocessing.cpu_count()
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        # get num of gpus
        num_of_gpus = torch.cuda.device_count()
        init_and_deploy_hpc_nodes(
            num_cpus=num_of_cpus,
            num_gpus=num_of_gpus,
            avoid_thread_contention=True
        )
    else:
        init_and_deploy_hpc_nodes(
            num_cpus=num_of_cpus, avoid_thread_contention=True
        )

    #TODO crawl, extract, and index the content of the URL


if __name__ == "__main__":
    if FOR_TEST:
        url_crawl_test()
    else:
        main()
