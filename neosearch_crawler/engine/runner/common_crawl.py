import os
from uuid import uuid4
import polars as pl
import csv
import gc

# custom modules
from neosearch_crawler.utils.trafilatura_util import extract_url_content
from neosearch_crawler.utils.domain_name_utils import reverse_domain
from neosearch_crawler.utils.logger import Logger
from neosearch_crawler.engine.runner import BaseRunner, step
from neosearch_crawler.utils.singleton import Singleton

logger = Logger()


class CommonCrawlRunner(BaseRunner, metaclass=Singleton):
    """Runner for parsing Common Crawl data, and extracting content from the URLs."""

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.uuid_str = str(uuid4())

        cwd = os.getcwd()
        if 'data' not in os.listdir(cwd):
            logger.log_debug("Creating data directory.")
            os.makedirs(f"{cwd}/data")

        self.vertex_file_path = kwargs.get('vertex_file_path', f"{cwd}/data/cc-main-domain-vertices.txt")
        self.edge_file_path = kwargs.get('edge_file_path', f"{cwd}/data/cc-main-domain-edges.txt")
        if not self._check_if_files_exist():
            raise FileNotFoundError("Vertex or edge file does not exist.")
        self.start_index = kwargs.get('start_index', 0)
        self.end_index = kwargs.get('end_index', -1)
        self.start_index_for_edge = kwargs.get('start_index_for_edge', 0)
        self.end_index_for_edge = kwargs.get('end_index_for_edge', -1)


    def _check_if_files_exist(self):
        return os.path.exists(self.vertex_file_path) and os.path.exists(self.edge_file_path)


    @step(1)
    def preprocess_vertices(self):
        start_index = self.start_index
        end_index = self.end_index
        logger.log_debug(f"Preprocessing vertices from {start_index} to {end_index} (uuid={self.uuid_str}).")

        with open(self.vertex_file_path, 'r') as f:
            with open(f"{os.getcwd()}/data/vertices_{self.uuid_str}.csv", 'w') as out_f:
                out_f.write("id,domain,num_of_hosts\n")
                for i, line in enumerate(f):
                    # start from the start_index
                    if i < start_index:
                        continue
                    # break if end_index is set and reached
                    if end_index > 0 and i > end_index:
                        break

                    # split the line into parts
                    parts = line.split()
                    if len(parts) != 3:
                        continue

                    id, domain, num_of_hosts = parts
                    out_f.write(f"{id},{domain},{num_of_hosts}\n")
        logger.log_debug(f"Preprocessing vertices completed (uuid={self.uuid_str}).")


    @step(1)
    def preprocess_edges(self):
        start_index = self.start_index_for_edge
        end_index = self.end_index_for_edge
        logger.log_debug(f"Preprocessing edges from {start_index} to {end_index} (uuid={self.uuid_str}).")

        with open(self.edge_file_path, 'r') as f:
            with open(f"{os.getcwd()}/data/edges_{self.uuid_str}.csv", 'w') as out_f:
                out_f.write("source,target\n")
                for i, line in enumerate(f):
                    # start from the start_index
                    if i < start_index:
                        continue
                    # break if end_index is set and reached
                    if end_index > 0 and i > end_index:
                        break

                    # split the line into parts
                    parts = line.split()
                    if len(parts) != 2:
                        continue

                    source, target = parts
                    out_f.write(f"{source},{target}\n")
        logger.log_debug(f"Preprocessing edges completed (uuid={self.uuid_str}).")


    @step(2)
    def crawl_and_verify_vertices(self):
        # use polars to read the vertex file
        vertex_df = pl.read_csv(f"{os.getcwd()}/data/vertices_{self.uuid_str}.csv")

        with open(f"{os.getcwd()}/data/uri_and_contents_{self.uuid_str}.csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'uri', 'content', 'num_of_hosts'])

            # iterate over the vertices and extract the content
            for i in range(len(vertex_df)):
                id = vertex_df['id'][i]
                domain = vertex_df['domain'][i]
                num_of_hosts = vertex_df['num_of_hosts'][i]

                uri = reverse_domain(domain)

                try:
                    # verify the domain name
                    data = extract_url_content(uri)
                    content = data['content']
                except Exception as e:
                    logger.log_debug(f"Failed to extract content from {domain} (uuid={self.uuid_str}). Reason: {e}")
                    continue
                if content is None:
                    logger.log_debug(f"Failed to extract content from {domain} (uuid={self.uuid_str}).")
                    continue
                logger.log_debug(f"Content extracted from {domain} (uuid={self.uuid_str}).")

                safe_content = content.encode('utf-8').decode('utf-8')
                writer.writerow([id, uri, safe_content, f"{num_of_hosts}"])
                logger.log_debug(f"Content written to file for {domain} (uuid={self.uuid_str}).")

        del vertex_df
        gc.collect()


    @step(3)
    def drop_unverified_edges(self):
        edges_df = pl.read_csv(f"{os.getcwd()}/data/edges_{self.uuid_str}.csv")
        uri_and_contents_df = pl.read_csv(f"{os.getcwd()}/data/uri_and_contents_{self.uuid_str}.csv")
        uri_ids = uri_and_contents_df['id'].to_list()
        uri_id_set = set(uri_ids)

        with open(f"{os.getcwd()}/data/filtered_edges_{self.uuid_str}.csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['source', 'target'])

            for i in range(len(edges_df)):
                source = edges_df['source'][i]
                target = edges_df['target'][i]

                if source not in uri_id_set or target not in uri_id_set:
                    logger.log_debug(f"Edge between {source} and {target} is dropped (uuid={self.uuid_str}).")
                    continue

                writer.writerow([source, target])
                logger.log_debug(f"Edge between {source} and {target} is kept (uuid={self.uuid_str}).")

        del edges_df, uri_and_contents_df, uri_ids, uri_id_set
        gc.collect()


    @step(4)
    def save_data_to_db(self):
        #TODO
        pass
