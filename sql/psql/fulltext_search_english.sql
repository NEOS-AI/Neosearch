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
