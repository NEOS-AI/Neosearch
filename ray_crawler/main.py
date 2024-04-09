import sys

sys.path.append("..")

# custom modules
from ray_crawler.utils import extract_url_content


if __name__ == "__main__":
    url = "https://namu.wiki/w/%EC%95%84%EB%9D%BC%ED%95%98%EC%8B%9C%20%ED%83%80%EB%B9%84"
    print(extract_url_content(url))
