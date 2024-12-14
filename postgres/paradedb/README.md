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

## HA Support

ParadeDB supports high availability (HA) using [CloudNativePG](https://cloudnative-pg.io/).

1. Installing the CloudNativePG operator:
```bash
helm repo add cnpg https://cloudnative-pg.github.io/charts
helm upgrade --install cnpg \
--namespace cnpg-system \
--create-namespace \
cnpg/cloudnative-pg
```

2. Setting up a ParadeDB CNPG Cluster (using default values `values.yaml`, you can customize the values as needed):
```bash
helm repo add paradedb https://paradedb.github.io/charts
helm upgrade --install paradedb \
--namespace paradedb-database \
--create-namespace \
--values values.yaml \
paradedb/paradedb
```

If you want to customize the values, please refer [ParadeDB Docs](https://github.com/paradedb/charts/tree/main/charts/paradedb).

For more information, please refer to the [ParadeDB github repo](https://github.com/paradedb/charts).

## See details of Stored Procedures

ParadeDB provides a set of stored procedures for searching and indexing.
In psql, you could run `\df+ <function_name> ` to see the details of the stored procedure.

Also, you could run the query below to print out all stored procedures in the database:
```bash
sudo docker exec paradedb psql -U postgres -d postgres -c "
SELECT
    n.nspname as schema_name,
    p.proname as procedure_name,
    pg_get_functiondef(p.oid) as definition
FROM pg_proc p
INNER JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
AND p.prokind = 'f'  -- Only select normal functions (not aggregate or window functions)
ORDER BY schema_name, procedure_name;" > ./procedures_paradedb.sql
```
