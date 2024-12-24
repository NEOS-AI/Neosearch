-- Reference: <https://xata.io/blog/postgres-full-text-search-postgres-vs-elasticsearch>

-- websearch_to_tsquery() is a function that converts a string to a tsquery
SELECT websearch_to_tsquery('english', 'the darth vader');
-- websearch_to_tsquery
-- ---------------------
-- 'darth' & 'vader'
-- (1 row)

-- websearch_to_tsquery() with OR
SELECT websearch_to_tsquery('english', 'darth OR vader');
-- websearch_to_tsquery
-- ---------------------
-- 'darth' | 'vader'
-- (1 row)

-- websearch_to_tsquery() with exclusion
SELECT websearch_to_tsquery('english', 'darth vader -wars');
-- websearch_to_tsquery
-- ---------------------
-- 'darth' & 'vader' & !'war'
-- (1 row)


-- 
-- You can create a GIN index on a set of columns, 
-- or you can first create a column of type tsvector, 
-- to include all the searchable columns. Something like this:
ALTER TABLE movies ADD search tsvector GENERATED ALWAYS AS
(
    to_tsvector('english', Title) || ' ' ||
    to_tsvector('english', Plot) || ' ' ||
    to_tsvector('simple', Director) || ' ' ||
    to_tsvector('simple', Genre) || ' ' ||
    to_tsvector('simple', Origin) || ' ' ||
    to_tsvector('simple', Casting)
) STORED;
-- And then create the actual index:
CREATE INDEX idx_movies_search ON movies USING GIN (search);


-- Use CTE with LIMIT, so that we could minimize the number of rows to be processed by ts_rank()
-- Words like 'mix' is a common word, so it will return a lot of rows.
-- This could lead to a performance issue (ts_rank() with a huge number of rows).
-- By limiting the number of rows, we could make PostgreSQL search as fast as Elasticsearch.
WITH search_sample AS (
    SELECT title, search FROM recipes
    WHERE search @@ websearch_to_tsquery('english','mix')
    LIMIT 10000
)
SELECT title, ts_rank(search, websearch_to_tsquery('english', 'mix')) rank
FROM search_sample
ORDER BY rank DESC limit 10;
