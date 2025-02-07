# Build Search Knowledge Base DB with Wikipedia Data

```bash
cd neosearch_crawler

mkdir data
cd data

# get wikipedia data
wget -O wiki-articles.json.bz2 https://www.dropbox.com/s/wwnfnu441w1ec9p/wiki-articles.json.bz2\?dl\=0
```

Connect to DB that has pg_search and pg_vector installed.

```bash
# connect to db
psql -h localhost -d neosearch
```

```sql
-- ensure pg_search and pg_vector are installed
CREATE EXTENSION pg_trgm;
CREATE EXTENSION pg_search;
CREATE EXTENSION vector;


-- create table
CREATE TABLE wiki_articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    url TEXT,
    body TEXT
);
```

Next, run the data ingestion python script before creating BM25 index.
I found out that the `insert` query is extremely slow after creating the BM25 index.
Even when I tried to insert rows in bulk, it was still slow.
It is much better to build the index after inserting all the rows.

```bash
cd ..

python3 main.py --mode wikiparse --data data/wiki-articles.json.bz2
```

After the data ingestion is done, create the BM25 index.
The wikipedia data is quite large, has above 5 million rows and most of the rows have long long texts, building the BM25 index will burst the CPU usage to 100%.

```sql
-- 
-- create index
-- 

CREATE INDEX ftx_wiki_articles_search_idx ON wiki_articles
USING bm25 (id, title, url, body)
WITH (key_field='id');

-- in old versions of pg_search, use:
CALL paradedb.create_bm25(
    index_name => 'ftx_wiki_articles_search_idx',
    schema_name => 'public',
    table_name => 'wiki_articles',
    key_field => 'id',
    text_fields => paradedb.field('title') || paradedb.field('body'),
    numeric_fields => '{}'
);
```

## References

- [Building Site Search With Tantivy](https://jstrong.dev/posts/2020/building-a-site-search-with-tantivy/)
