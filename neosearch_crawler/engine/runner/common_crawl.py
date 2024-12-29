import os

# custom modules
# from neosearch_crawler.utils.trafilatura_util import extract_url_content

from .base import BaseRunner


class CommonCrawlRunner(BaseRunner):
    def __init__(self, *args, **kwargs):
        # super().__init__()
        cwd = os.getcwd()
        self.vertex_file_path = kwargs.get('vertex_file_path', f"{cwd}/data/cc-main-domain-vertices.txt")
        self.edge_file_path = kwargs.get('edge_file_path', f"{cwd}/data/cc-main-domain-edges.txt")
        if not self._check_if_files_exist():
            raise FileNotFoundError("Vertex or edge file does not exist.")

    def _check_if_files_exist(self):
        return os.path.exists(self.vertex_file_path) and os.path.exists(self.edge_file_path)
