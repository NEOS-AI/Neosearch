# ParadeDB

[ParadeDB](https://github.com/paradedb/paradedb) is an Elasticsearch alternative built on Postgres.
It uses [tantivy](https://github.com/quickwit-oss/tantivy), a Rust-based Lucene alternative, for indexing and searching.

## Run with Docker

To quickly get a ParadeDB instance up and running, simply pull and run the latest Docker image:
```bash
docker run --name paradedb -e POSTGRES_PASSWORD=password paradedb/paradedb
```

This will start a ParadeDB instance with default user postgres and password `password`.
You can then connect to the database using psql:
```bash
docker exec -it paradedb psql -U postgres
```

To install ParadeDB locally or on-premise, we recommend using the ParadeDB's `docker-compose.yml` file.
Alternatively, you can pass the appropriate environment variables to the `docker run` command, replacing the <> with your desired values:
```bash
docker run \
    --name paradedb \
    -e POSTGRES_USER=<user> \
    -e POSTGRES_PASSWORD=<password> \
    -e POSTGRES_DB=<dbname> \
    -v paradedb_data:/var/lib/postgresql/data/ \
    -p 5432:5432 \
    -d \
    paradedb/paradedb:latest
```

This will start a ParadeDB instance with non-root user `<user>` and password `<password>`.
The `-v` flag enables your ParadeDB data to persist across restarts in a Docker volume named `paradedb_data`.

You can then connect to the database using psql:
```bash
docker exec -it paradedb psql -U <user> -d <dbname> -p 5432 -W
```

ParadeDB collects anonymous telemetry to help the ParadeDB team understand how many people are using the project.
You can opt out of telemetry using configuration variables within Postgres:
```sql
ALTER SYSTEM SET paradedb.pg_search_telemetry TO 'off';
ALTER SYSTEM SET paradedb.pg_analytics_telemetry TO 'off';
```

## CJK Support

ParadeDB supports CJK (Chinese, Japanese, Korean) tokenizers.
By choosing the suitable tokenizer (`korean_lindera` for Korean, `japanese_lindera` for Japanese, etc), you can index and search CJK text.
For more information, see the [ParadeDB documentation](https://docs.paradedb.com/search/full-text/index#tokenizers).