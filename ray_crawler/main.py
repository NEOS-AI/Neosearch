import sys
from ray import serve

sys.path.append("..")

# custom modules
from ray_crawler.engine.deployment import EmbeddingDeployment
from ray_crawler.utils import extract_url_content


def url_crawl_test():
    url = "https://namu.wiki/w/%EC%95%84%EB%9D%BC%ED%95%98%EC%8B%9C%20%ED%83%80%EB%B9%84"
    print(extract_url_content(url))

def main():
    # Deploy the Ray Serve application.
    deployment = EmbeddingDeployment.bind()
    serve.run(deployment)

if __name__ == "__main__":
    main()
