# pgvectorscale

[pgvectorscale](https://github.com/timescale/pgvectorscale) is a complement to pgvector for high performance, cost efficient vector search on large workloads.
It provides StreamingDiskANN, which is a PostgreSQL implementation of [Microsoft's DiskANN](https://www.microsoft.com/en-us/research/publication/diskann-fast-accurate-billion-point-nearest-neighbor-search-on-a-single-node).

## StreamingDiskANN: A Scalable, High-Performance, Cost-efficient Index for Pgvector Data

### Implementing a DiskANN-inspired index for pgvector

Inspired by Microsoft’s DiskANN (also referred to as Vamana), pgvectorscale adds a third approximate nearest neighbor (ANN) search algorithm, StreamingDiskANN, to pgvector.
This comes in addition to pgvector's existing IVFFlat (inverted file flat) and HNSW (hierarchical navigable small world) vector search indexes.

StreamingDiskANN is optimized for storing the index on disk as opposed to in-memory indexes like HNSW, making it more cost-efficient to run and scale as vector workloads grow.
This vastly decreases the cost of storing and searching over large amounts of vectors since SSDs are much cheaper than RAM.

The StreamingDiskANN index uses the pgvector vector data type, so developers already using pgvector don’t need to migrate data or use a different type.
All that’s needed is creating a new index on the embeddings column.

The Pinecone Graph Algorithm is also based on DiskANN, meaning developers can now use a similar search algorithm as Pinecone in PostgreSQL without using a standalone vector database.

### Support for streaming filtering

TimescalDB team call pgvectorscale’s index StreamingDiskANN as it supports streaming filtering, which allows for accurate retrieval even when secondary filters are applied during similarity search.
This scenario is common in production RAG (retrieval-augmented generation) applications, where, for example, documents are often associated with a set of tags, and you may want to constrain your similarity search by requiring a match of the tags as well as high vector similarity.

One pitfall of the HNSW index in pgvector is that it retrieves a pre-set number of records (set by the hnsw.ef_search parameter) before applying secondary filters.
Therefore, if the filters exclude all the vectors fetched from the index, the HNSW index would fail to retrieve data for the search with high accuracy. This scenario is common when searching through large datasets of vectors.

Pgvectorscale’s StreamingDiskANN index has no "ef_search" type cutoff. Instead, it uses a streaming model that allows the index to continuously retrieve the "next closest" item for a given query, potentially even traversing the entire graph.
The Postgres execution system will continuously ask for the "next closet" item until it has matched the LIMIT N items that satisfy the additional filters.
This form of post-filtering suffers absolutely no accuracy degradation.

### StreamingDiskANN query-time parameters

You can also set two parameters to control the accuracy vs. query speed trade-off at query time.
We suggest adjusting `diskann.query_rescore` to fine-tune accuracy.

| Parameter name | Description | Default value |
| --- | --- | --- |
| diskann.query_search_list_size | The number of additional candidates considered during the graph search. | 100 |
| diskann.query_rescore | The number of elements rescored (0 to disable rescoring) | 50 |

You can set the value by using SET before executing a query. For example:

```sql
SET diskann.query_rescore = 400;
```

Note the SET command applies to the entire session (database connection) from the point of execution.
You can use a transaction-local variant using LOCAL which will be reset after the end of the transaction:

```sql
BEGIN;
SET LOCAL diskann.query_search_list_size= 10;
SELECT * FROM document_embedding ORDER BY embedding <=> $1 LIMIT 10
COMMIT;
```

## References

- [pgvectorscale](https://github.com/timescale/pgvectorscale)
- [Timescale: pgvector is now as fast as pinecone at 75% less cost](https://www.timescale.com/blog/pgvector-is-now-as-fast-as-pinecone-at-75-less-cost/amp/)
