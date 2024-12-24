# Using PostgreSQL to Create an Efficient Search Engine

## Various types of search queries

Generally, most databases do not support the acceleration of search queries for the query types 4, 5, 6, and 7 shown below.
However, given its powerful capabilities, PostgreSQL can easily support the acceleration of all of the query types given below, including types 4, 5, 6, and 7.
This is because, for PostgreSQL, query and write operations are not in conflict with one another, and the relevant indexes can be built in real-time.

Typically with search engines, you do not need to synchronize data before performing queries.
As a result, the search engine can only support full-text searches and cannot implement regexp, similarity and prefix/suffix fuzzy queries.

However, with PostgreSQL, you can significantly simplify your overall search engine architecture, reducing the cost of development while also ensuring the capability of real-time data queries.

### 1.  Prefix + fuzzy query.

For this type, `B-tree` indexes can be used. Consider the following example expressions:
```sql
-- "like" is the string pattern matching operator.
select * from tbl where col like 'ab%';

-- "~" is the regular expression match operator.
select * from tbl where col ~ '^ab';
```

### 2.  Suffix + fuzzy query.

For this type, both the `reverse(col)` expression and `B-tree` indexes can be used. Again, consider the following examples:
```sql
-- "like" is the string pattern matching operator.
select * from tbl where col like '%ab';

-- "~" is the regular expression match operator.
select * from tbl where col ~ 'ab$';

-- Use the reverse function to search for suffixes with the "like" operator (reverse the column).
select * from tbl where reverse(col) like 'ba%';

-- Use the reverse function to search for suffixes with the "~" operator (reverse the column).
select * from tbl where reverse(col) ~ '^ba';
```

### 3. Prefix and/or suffix + fuzzy query

For these, both the `pg_trgm` and `GIN` indexes can be used.
```sql
select * from tbl where col like '%ab%';

select * from tbl where col ~ 'ab';
```

To create `pg_trgm` indexes, use the following SQL:
```sql
create extension pg_trgm;

create index idx_tbl_col on tbl using gin (col gin_trgm_ops);
```

### 4. Full-text search

For full-text search, the `GIN` or `RUM` indexes can be used.
```sql
select * from tbl where tsvector_col @@ 'postgres & china | digoal:A' order by ts_rank(tsvector_col, 'postgres & china | digoal:A') limit xx;  
```

To create a GIN index, use the following SQL:
```sql
create index idx_tbl_tsvector_col on tbl using gin (tsvector_col);
```

To create a RUM index, use the following SQL:
```sql
create extension rum;

create index idx_tbl_tsvector_col on tbl using rum (tsvector_col);
```

### 5. Regexp query

For this type, both pg_trgm and GIN indexes can be used.

```sql

select * from tbl where col ~ '^a[0-9]{1,5}\ +digoal$';
```

### 6. Similarity query

`pg_trgm` and `GIN` indexes can be used.

```sql
select * from tbl order by similarity(col, 'postgre') desc limit 10;  
```

### 7. Ad Hoc queries (queries based on a combination of fields)

This category of queries can be implemented by using indexes such as a bloom index, multi-index bitmap scan, or GIN-index bitmap scan.
```sql
select * from tbl where a=? and b=? or c=? and d=? or e between ? and ? and f in (?);
```

## Limitations of FTS with PostgreSQL

Now that we have looked at the core features of full-text search, in addition to some additional special features, now it's time to consider some of the limitations of this query type. First, among other limitations of this query type, there is the fact that the length of each lexeme must be less than 2K bytes.
Furthermore, the length of a tsvector (lexemes + positions) must be less than 1 megabyte.

In a tsvector, the number of lexemes must be less than 2^64 (which happens to be 18446744073709551616).

Another limitation is that the position values in tsvector must be greater than 0 and no more than 16,383.
Similarly, the match distance in a (`FOLLOWED BY`) tsquery operator cannot be more than 16,384.
And another limit is that no more than 256 positions per lexeme.
Following this, the number of nodes (lexemes + operators) in a tsquery must be less than 32,768.

In general, if you find yourself to be limited by these limitation-hitting a brick wall when conducting full-text search-you'll need to use more fields to compensate.

## References

- [Alibaba Cloud :: Using PostgreSQL to Create an Efficient Search Engine](https://www.alibabacloud.com/blog/using-postgresql-to-create-an-efficient-search-engine_595344)
- [pg_trgm](https://www.postgresql.org/docs/10/pgtrgm.html)
