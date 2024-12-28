import sys
import ray
import multiprocessing
import os
from dotenv import load_dotenv

sys.path.append("..")

# custom modules
from utils import extract_url_content


load_dotenv()
FOR_TEST = os.getenv("FOR_TEST", "0") == "1"


def url_crawl_test(output_format: str = "markdown"):
    url = "https://namu.wiki/w/%EC%95%84%EB%9D%BC%ED%95%98%EC%8B%9C%20%ED%83%80%EB%B9%84"
    print(extract_url_content(url, output_format=output_format))


def main():
    num_of_cpus = multiprocessing.cpu_count()

    #TODO crawl, extract, and index the content of the URL


if __name__ == "__main__":
    if FOR_TEST:
        url_crawl_test()
    else:
        main()
