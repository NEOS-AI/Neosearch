from llama_index.core.retrievers import BaseRetriever
from llama_index.core.indices.query.embedding_utils import get_top_k_embeddings
from llama_index.core import QueryBundle, VectorStoreIndex
from llama_index.core.schema import NodeWithScore
from llama_index.core.storage.docstore import SimpleDocumentStore
from typing import Any, Optional


class DocHybridRetriever(BaseRetriever):
    """Hybrid retriever."""

    def __init__(
        self,
        vector_index: VectorStoreIndex,
        docstore: SimpleDocumentStore,
        similarity_top_k: int = 2,
        out_top_k: Optional[int] = None,
        alpha: float = 0.5,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        super().__init__(**kwargs)
        self._vector_index = vector_index
        self._embed_model = vector_index._embed_model
        self._retriever = vector_index.as_retriever(
            similarity_top_k=similarity_top_k
        )

        self.simiarity_top_k = similarity_top_k
        self.out_top_k = out_top_k

        self._out_top_k = out_top_k or similarity_top_k
        self._docstore = docstore
        self._alpha = alpha


    def _retrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        """Retrieve nodes given query."""

        # first retrieve chunks
        nodes = self._retriever.retrieve(query_bundle.query_str)

        # get documents, and embedding similiaryt between query and documents

        ## get doc embeddings
        docs = [self._docstore.get_document(n.node.index_id) for n in nodes]
        doc_embeddings = [d.embedding for d in docs]
        query_embedding = self._embed_model.get_query_embedding(
            query_bundle.query_str
        )

        ## compute doc similarities
        doc_similarities, doc_idxs = get_top_k_embeddings(
            query_embedding, doc_embeddings
        )

        ## compute final similarity with doc similarities and original node similarity
        result_tups = []
        for doc_idx, doc_similarity in zip(doc_idxs, doc_similarities):
            node = nodes[doc_idx]
            # weight alpha * node similarity + (1-alpha) * doc similarity
            full_similarity = (self._alpha * node.score) + (
                (1 - self._alpha) * doc_similarity
            )
            print(
                f"Doc {doc_idx} (node score, doc similarity, full similarity): {(node.score, doc_similarity, full_similarity)}"
            )
            result_tups.append((full_similarity, node))

        result_tups = sorted(result_tups, key=lambda x: x[0], reverse=True)
        # update scores
        for full_score, node in result_tups:
            node.score = full_score

        return [n for _, n in result_tups][:self._out_top_k]
