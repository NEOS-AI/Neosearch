# Hybrid Search

## ParadeDB

With ParadeDB, you can create a hybrid search engine that combines the BM25 algorithm with the vector search algorithm ([reference](https://docs.paradedb.com/documentation/guides/hybrid)).

Sample:
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
