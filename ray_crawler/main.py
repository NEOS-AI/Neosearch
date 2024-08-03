import sys
from ray import serve

sys.path.append("..")

# custom modules
from ray_crawler.engine.deployment import EmbeddingDeployment
from ray_crawler.utils import extract_url_content


def url_crawl_test():
    url = "https://namu.wiki/w/%EC%95%84%EB%9D%BC%ED%95%98%EC%8B%9C%20%ED%83%80%EB%B9%84"
    print(extract_url_content(url))

def deploy_embedding_server():
    # Deploy the Ray Serve application.
    deployment = EmbeddingDeployment.bind()
    serve.run(
        deployment,
        blocking=False,
        name="embedding_server",
        route_prefix="/embed"
    )


def main(use_custom_server: bool = False):
    if use_custom_server:
        deploy_embedding_server()
    #TODO crawl, extract, and index the content of the URL


if __name__ == "__main__":
    main()
