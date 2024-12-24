# Vector Search

## pg_vector

Add pgvector v0.6.0:

```bash
cd /tmp
git clone --branch v0.6.0 https://github.com/pgvector/pgvector.git
cd pgvector
make
make install # may need sudo
```

Then, create extension for pg_vector:

```sql
CREATE EXTENSION vector;
```

## pg_embeddings

Add pg_embeddings

```bash
cd /tmp
git clone https://github.com/neondatabase/pg_embedding.git
cd pg_embedding
make
make install
```

Then, create extension for pg_embedding:

```sql
CREATE EXTENSION embedding;
```
