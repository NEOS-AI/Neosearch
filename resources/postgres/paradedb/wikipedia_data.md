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

## Performance tuning

As the size of both the table and the index is large enough, the performance of the search query is not good if you use the default configuration.
You might need to tune the postgresql configuration to get better performance.

First, check the file path of the postgresql configuration file.

```sql
SHOW config_file;
```

Then, edit the configuration file.
```bash
sudo vi /opt/homebrew/var/postgresql@17/postgresql.conf
```

Edit the following configurations:

```conf
max_worker_processes = 16
max_parallel_workers = 16

...

shared_buffers = 4GB

...

maintenance_work_mem = 16GB
```

### maintenance_work_mem

In addition to improving build times, `maintenance_work_mem` also affects the number of segments created in the index.
This is because, while ParadeDB tries to maintain as many segments as CPUs, a segment that cannot fit into memory will be split into a new segment.
As a result, an insufficient `maintenance_work_mem` can lead to significantly more segments than available CPUs, which degrades search performance.
To check if the chosen `maintenance_work_mem` value is high enough, you can compare the index’s segment count with the server’s CPU count.

To check the number of segments in the index, you can use the following query:

```sql
SELECT * FROM paradedb.index_info('ftx_wiki_articles_search_idx');
```

### Parallel workers (max_parallel_workers, max_worker_processes)

The number of parallel workers depends on the server’s CPU count and certain Postgres settings in `postgresql.conf`.

`max_parallel_workers` and max_worker_processes control how many workers are available to parallel scans.
`max_worker_processes` is a global limit for the number of available workers across all connections, and `max_parallel_workers` specifies how many of those workers can be used for parallel scans.

Next, `max_parallel_workers_per_gather` must be set.
This setting is a limit for the number of parallel workers that a single parallel query can use.
The default is 2.
This setting can be set in postgresql.conf to apply to all connections, or within a connection to apply to a single session.

### Shared buffers

`shared_buffers` controls how much memory is available to the Postgres buffer cache.
While a general rule of thumb is to allocate up to 40% of total system memory to `shared_buffers`, we recommend experimenting with higher values for larger indexes.

The `pg_prewarm` extension can be used to load the BM25 index into the buffer cache after Postgres restarts.
A higher shared_buffers value allows more of the index to be stored in the buffer cache.

```sql
CREATE EXTENSION pg_prewarm;
SELECT pg_prewarm('ftx_wiki_articles_search_idx');
```

## References

- [Building Site Search With Tantivy](https://jstrong.dev/posts/2020/building-a-site-search-with-tantivy/)
- [ParadeDB Index Throughput Tuning](https://docs.paradedb.com/documentation/configuration/write)
- [ParadeDB Search Performance Tuning](https://docs.paradedb.com/documentation/configuration/parallel)
