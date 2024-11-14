# Search Tutorials

This tutorial is based on the [ParadeDB Search Quickstart](https://docs.paradedb.com/search/quickstart).
All credits to @paradedb team.

## Table of Contents

* [1. Full Text Search](#1-full-text-search)
    * [1-1. Full Text Search](#1-1-full-text-search)
    * [1-2. n-gram Tokenization](#1-2-n-gram-tokenization)
    * [1-3. Snippet](#1-3-snippet)
* [2. Similarity Search](#2-similarity-search)
* [3. Hybrid Search](#3-hybrid-search)

## 1. Full Text Search

### 1-1. Full Text Search

ParadeDB comes with a helpful procedure that creates a table populated with mock data to help you get started.
Once connected with psql, run the following commands to create and inspect this table.

```sql
CALL paradedb.create_bm25_test_table(
  schema_name => 'public',
  table_name => 'mock_items'
);


SELECT * FROM mock_items LIMIT 3;
```

outputs:
```
 id |       description        | rating |  category   | in_stock |                     metadata                     |     created_at      | last_updated_date | latest_available_time
----+--------------------------+--------+-------------+----------+--------------------------------------------------+---------------------+-------------------+-----------------------
  1 | Ergonomic metal keyboard |      4 | Electronics | t        | {"color": "Silver", "location": "United States"} | 2023-05-01 09:12:34 | 2023-05-03        | 09:12:34
  2 | Plastic Keyboard         |      4 | Electronics | f        | {"color": "Black", "location": "Canada"}         | 2023-04-15 13:27:09 | 2023-04-16        | 13:27:09
  3 | Sleek running shoes      |      5 | Footwear    | t        | {"color": "Blue", "location": "China"}           | 2023-04-28 10:55:43 | 2023-04-29        | 10:55:43
(3 rows)
```

Next, let’s create a BM25 index called `search_idx` on this table.
We’ll index the `description` and `category` fields and configure the tokenizer on the description field.

```sql
CALL paradedb.create_bm25(
    index_name => 'search_idx',
    schema_name => 'public',
    table_name => 'mock_items',
    key_field => 'id',
    text_fields => paradedb.field('description', tokenizer => paradedb.tokenizer('en_stem')) || paradedb.field('category'),
    numeric_fields => paradedb.field('rating')
);
```

Note the mandatory `key_field` option.
Every BM25 index needs a `key_field`, which should be the name of a column that will function as a row’s unique identifier within the index.
Usually, the `key_field` can just be the name of your table’s primary key column.

Now you could view the index has been created by running the following command:
```sql
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'mock_items';
```

outputs:
```
       indexname       |                                                                                                                                                                      indexdef
-----------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 mock_items_pkey       | CREATE UNIQUE INDEX mock_items_pkey ON public.mock_items USING btree (id)
 search_idx_bm25_index | CREATE INDEX search_idx_bm25_index ON public.mock_items USING bm25 (id, description, rating, category) WITH (key_field=id, text_fields='{"category":{},"description":{"tokenizer":{"type":"en_stem"}}}', numeric_fields='{"rating":{}}', boolean_fields='{}', json_fields='{}', datetime_fields='{}', uuid='d4a8bf9f-c088-4456-b7e1-0c6674c20b99')
(2 rows)
```

You could also use `\d+ mock_items` to see the indexes on the table. (or `\d mock_items` for a more concise view):
```sql
\d+ mock_items;
```

outputs:
```
                                                                         Table "public.mock_items"
        Column         |            Type             | Collation | Nullable |                Default                 | Storage  | Compression | Stats target | Description
-----------------------+-----------------------------+-----------+----------+----------------------------------------+----------+-------------+--------------+-------------
 id                    | integer                     |           | not null | nextval('mock_items_id_seq'::regclass) | plain    |             |              |
 description           | text                        |           |          |                                        | extended |             |              |
 rating                | integer                     |           |          |                                        | plain    |             |              |
 category              | character varying(255)      |           |          |                                        | extended |             |              |
 in_stock              | boolean                     |           |          |                                        | plain    |             |              |
 metadata              | jsonb                       |           |          |                                        | extended |             |              |
 created_at            | timestamp without time zone |           |          |                                        | plain    |             |              |
 last_updated_date     | date                        |           |          |                                        | plain    |             |              |
 latest_available_time | time without time zone      |           |          |                                        | plain    |             |              |
Indexes:
    "mock_items_pkey" PRIMARY KEY, btree (id)
    "search_idx_bm25_index" bm25 (id, description, rating, category) WITH (key_field=id, text_fields='{"category":{},"description":{"tokenizer":{"type":"en_stem"}}}', numeric_fields='{"rating":{}}', boolean_fields='{}', json_fields='{}', datetime_fields='{}', uuid='d4a8bf9f-c088-4456-b7e1-0c6674c20b99')
Check constraints:
    "mock_items_rating_check" CHECK (rating >= 1 AND rating <= 5)
Access method: heap
```

We’re now ready to execute a full-text search.
We’ll look for rows with a rating greater than 2 where description matches keyboard or category matches electronics.

```sql
SELECT description, rating, category
FROM search_idx.search(
  '(description:keyboard OR category:electronics) AND rating:>2',
  limit_rows => 5
);
```

#### Key points for FTS

Note the usage of `limit_rows` instead of the SQL `LIMIT` clause.
For optimal performance, using `limit_rows` and `offset_rows` instead of `LIMIT` and `OFFSET` is always recommended in ParadeDB.

### 1-2. n-gram Tokenization

Next, let’s match against a partial word like blue.
To do this, we’ll create a new index that uses the `ngrams tokenizer`, which splits text into chunks of size `n`.

```sql
CALL paradedb.create_bm25(
        index_name => 'ngrams_idx',
        schema_name => 'public',
        table_name => 'mock_items',
        key_field => 'id',
        text_fields => paradedb.field('description', tokenizer => paradedb.tokenizer('ngram', min_gram => 4, max_gram => 4, prefix_only => false)) ||
                       paradedb.field('category')
);

SELECT description, rating, category FROM ngrams_idx.search('description:blue');
```

output:
```
        description        | rating |  category
---------------------------+--------+-------------
 Bluetooth-enabled speaker |      3 | Electronics
(1 row)
```

### 1-3. Snippet

Finally, let’s use the snippet function to examine the BM25 scores and generate highlighted snippets for our results.

```sql
WITH snippet AS (
    SELECT * FROM ngrams_idx.snippet(
      'description:blue',
      highlight_field => 'description'
    )
)
SELECT description, snippet, score_bm25
FROM snippet
LEFT JOIN mock_items ON snippet.id = mock_items.id;
```

output:
```
        description        |             snippet              | score_bm25
---------------------------+----------------------------------+------------
 Bluetooth-enabled speaker | <b>Blue</b>tooth-enabled speaker |  2.9903657
(1 row)
```

## 2. Similarity Search

For vector similarity search, let’s first generate a vector embeddings column.
For the sake of this tutorial, we’ll randomly generate these embeddings.

```sql
ALTER TABLE mock_items ADD COLUMN embedding vector(3);

UPDATE mock_items m
SET embedding = ('[' ||
    ((m.id + 1) % 10 + 1)::integer || ',' ||
    ((m.id + 2) % 10 + 1)::integer || ',' ||
    ((m.id + 3) % 10 + 1)::integer || ']')::vector;

SELECT description, rating, category, embedding
FROM mock_items
LIMIT 3;
```

output:
```
       description        | rating |  category   | embedding
--------------------------+--------+-------------+-----------
 Ergonomic metal keyboard |      4 | Electronics | [3,4,5]
 Plastic Keyboard         |      4 | Electronics | [4,5,6]
 Sleek running shoes      |      5 | Footwear    | [5,6,7]
(3 rows)
```

Next, let’s create an `HNSW` index on the embedding column of our table.
While not required, an `HNSW` index can drastically improve query performance over very large datasets.

```sql
CREATE INDEX on mock_items USING hnsw (embedding vector_l2_ops);
```

Next, let’s query our table with a vector and order the results by L2 distance:

```sql
SELECT description, category, rating, embedding
FROM mock_items
ORDER BY embedding <-> '[1,2,3]'
LIMIT 3;
```

output:
```
       description       |  category  | rating | embedding
-------------------------+------------+--------+-----------
 Artistic ceramic vase   | Home Decor |      4 | [1,2,3]
 Modern wall clock       | Home Decor |      4 | [1,2,3]
 Designer wall paintings | Home Decor |      5 | [1,2,3]
(3 rows)
```

## 3. Hybrid Search

Finally, let’s implement hybrid search, which combines BM25-based full text scores with vector-based similarity scores.
Hybrid search is especially useful in scenarios where you want to match by both exact keywords and semantic meaning.

The `score_hybrid` function accepts a BM25 query and a similarity query.
It applies minmax normalization to the BM25 and similarity scores and combines them using a weighted average.

```sql
SELECT * FROM search_idx.score_hybrid(
    bm25_query => 'description:keyboard OR category:electronics',
    similarity_query => '''[1,2,3]'' <-> embedding',
    bm25_weight => 0.9,
    similarity_weight => 0.1
) LIMIT 5;
```

output:
```
 id | score_hybrid
----+--------------
  2 |   0.95714283
  1 |    0.8490507
 29 |          0.1
 39 |          0.1
  9 |          0.1
(5 rows)
```

As we can see, results with the word keyboard scored higher than results with an embedding of [1,2,3] because we placed a weight of 0.9 on the BM25 scores.

### Performance Improvements

In the [section 1-1](#key-points-for-fts), we mentioned the importance of using `limit_rows` and `offset_rows` instead of `LIMIT` and `OFFSET`.
For the Hybrid search query above, you might be tempted to use `LIMIT` to limit the number of results.

Clearly, ParadeDB provides an argument `bm25_limit_n` and `similarity_limit_n` to limit the number of results for BM25 and similarity queries respectively.
Default values are 100 for both arguments.
By tuning these arguments, you can improve the performance of your hybrid search queries.

```sql
SELECT * FROM search_idx.score_hybrid(
    bm25_query => 'description:keyboard OR category:electronics',
    similarity_query => '''[1,2,3]'' <-> embedding',
    bm25_weight => 0.9,
    similarity_weight => 0.1,
	bm25_limit_n => 5,
	similarity_limit_n => 5
);
```

output:
```
 id | score_hybrid
----+--------------
  2 |          0.9
  1 |    0.7776221
  9 |          0.1
 39 |          0.1
 19 |          0.1
 29 |          0.1
 20 |   0.08571429
 12 |            0
 22 |            0
 32 |            0
(10 rows)
```

If you set `bm25_limit_n` as 2 in the query above, the result will be changed as below:
```
 id | score_hybrid
----+--------------
  2 |          0.9
 39 |          0.1
 29 |          0.1
  9 |          0.1
 19 |          0.1
 20 |   0.08571429
  1 |            0
(7 rows)
```

### Reciprocal Rank Fusion

Reciprocal rank fusion is a popular hybrid search algorithm that:

1. Calculates a BM25 and similarity score for the top n documents.
2. Ranks documents by their BM25 and similarity scores separately. The highest-ranked document for each score receives an r of 1.
3. Calculates a reciprocal rank for each score as 1/(k + r), where k is a constant. k is usually set to 60.
4. Calculates each document’s reciprocal rank fusion score as the sum of the BM25 and similarity reciprocal rank scores.

The following code block implements reciprocal rank fusion over the `mock_items` table. BM25 scores are calculated against the query `description:keyboard` and similarity scores are calculated against the vector [1,2,3].

```sql
WITH semantic_search AS (
    SELECT id, RANK () OVER (ORDER BY embedding <=> '[1,2,3]') AS rank
    FROM mock_items
    ORDER BY embedding <=> '[1,2,3]'
    LIMIT 20
),
bm25_search AS (
    SELECT id, RANK () OVER (ORDER BY score_bm25 DESC) as rank
    FROM search_idx.score_bm25('description:keyboard', limit_rows => 20)
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
ORDER BY score DESC
LIMIT 5;
```
