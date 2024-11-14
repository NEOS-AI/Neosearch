# Advanced RAG

## Hybrid Search

A relatively old idea that you could take the best from both worlds — keyword-based old school search — sparse retrieval algorithms like tf-idf or search industry standard BM25 — and modern semantic or vector search and combine it in one retrieval result.

The only trick here is to properly combine the retrieved results with different similarity scores — this problem is usually solved with the help of the Reciprocal Rank Fusion algorithm, reranking the retrieved results for the final output.

By using [ParadeDB](https://www.paradedb.com/), you could achieve this within a single SQL query (using CTE for both vector search and BM25 FTS, and combine them) with custom ranking weights:
```sql
WITH semantic_search AS (
    SELECT id, RANK () OVER (ORDER BY embedding <=> '[1,2,3]') AS rank
    FROM mock_items ORDER BY embedding <=> '[1,2,3]' LIMIT 20
),
bm25_search AS (
    SELECT id, RANK () OVER (ORDER BY paradedb.score(id) DESC) as rank
    FROM mock_items WHERE description @@@ 'keyboard' LIMIT 20
)
SELECT
    COALESCE(semantic_search.id, bm25_search.id) AS id,
    COALESCE(1.0 / (60 + semantic_search.rank), 0.0) +
    COALESCE(1.0 / (60 + bm25_search.rank), 0.0) AS score,
    mock_items.description,
    mock_items.embedding
FROM semantic_search
FULL OUTER JOIN bm25_search ON semantic_search.id = bm25_search.id
JOIN mock_items ON mock_items.id = COALESCE(semantic_search.id, bm25_search.id)
ORDER BY score DESC, description
LIMIT 5;
```
For more information about paradedb hybrid search, refer to [here](https://docs.paradedb.com/documentation/guides/hybrid).

## 12 RAG Pain Points

* [Pain Point 1: Missing Content](https://towardsdatascience.com/12-rag-pain-points-and-proposed-solutions-43709939a28c#777a)
* [Pain Point 2: Missed the Top Ranked Documents](https://towardsdatascience.com/12-rag-pain-points-and-proposed-solutions-43709939a28c#4dae)
* [Pain Point 3: Not in Context — Consolidation Strategy Limitations](https://towardsdatascience.com/12-rag-pain-points-and-proposed-solutions-43709939a28c#f3dd)
* [Pain Point 4: Not Extracted](https://towardsdatascience.com/12-rag-pain-points-and-proposed-solutions-43709939a28c#c43d)
* [Pain Point 5: Wrong Format](https://towardsdatascience.com/12-rag-pain-points-and-proposed-solutions-43709939a28c#71d0)
* [Pain Point 6: Incorrect Specificity](https://towardsdatascience.com/12-rag-pain-points-and-proposed-solutions-43709939a28c#4bd3)
* [Pain Point 7: Incomplete](https://towardsdatascience.com/12-rag-pain-points-and-proposed-solutions-43709939a28c#cea4)
* [Pain Point 8: Data Ingestion Scalability](https://towardsdatascience.com/12-rag-pain-points-and-proposed-solutions-43709939a28c#b0a5)
* [Pain Point 9: Structured Data QA](https://towardsdatascience.com/12-rag-pain-points-and-proposed-solutions-43709939a28c#d3bc)
* [Pain Point 10: Data Extraction from Complex PDFs](https://towardsdatascience.com/12-rag-pain-points-and-proposed-solutions-43709939a28c#93c0)
* [Pain Point 11: Fallback Model(s)](https://towardsdatascience.com/12-rag-pain-points-and-proposed-solutions-43709939a28c#c20e)
* [Pain Point 12: LLM Security](https://towardsdatascience.com/12-rag-pain-points-and-proposed-solutions-43709939a28c#31f8)

## References

- [Advanced RAG Techniques: an Illustrated Overview](https://pub.towardsai.net/advanced-rag-techniques-an-illustrated-overview-04d193d8fec6)
- [A Guide on 12 Tuning Strategies for Production-Ready RAG Applications](https://towardsdatascience.com/a-guide-on-12-tuning-strategies-for-production-ready-rag-applications-7ca646833439)
- [12 RAG Pain Points and Proposed Solutions](https://towardsdatascience.com/12-rag-pain-points-and-proposed-solutions-43709939a28c)
