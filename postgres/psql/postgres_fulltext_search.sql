-- CREATE EXTENSION unaccent;: This line loads the unaccent extension, which is a text search dictionary that removes accents (diacritic signs) from lexemes.
CREATE EXTENSION unaccent;


-- ALTER TABLE client ADD COLUMN full_text_search VARCHAR;: This line adds a new column full_text_search to the client table.
-- This column will be used to store the searchable content.
ALTER TABLE client ADD COLUMN full_text_search VARCHAR;


-- Do an initial update and apply the UNACCENT function searchable content
--
-- The UPDATE client statement is used to populate the full_text_search column with the concatenated and unaccented values of the name, notes, and location_address columns.
-- The COALESCE function is used to handle NULL values by replacing them with an empty string.
UPDATE client SET full_text_search = tsvector_to_array(to_tsvector('english', UNACCENT(name || ' ' || COALESCE(notes, ' ') || ' ' || COALESCE(location_address, ' '))));


-- Create an AFTER INSERT OR UPDATE trigger (to maintain the column data for inserted/updated rows)
--
-- The CREATE OR REPLACE FUNCTION client_full_text_search_refresh() creates a function
-- that updates the full_text_search column whenever a new row is inserted or an existing row is updated in the client table.
CREATE OR REPLACE FUNCTION client_full_text_search_refresh() RETURNS trigger LANGUAGE plpgsql AS $function$
BEGIN
    IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
    	NEW.full_text_search := (tsvector_to_array(to_tsvector('english', UNACCENT(NEW.name || ' ' || COALESCE(NEW.notes, ' ') || ' ' || COALESCE(NEW.location_address, ' ')))));
    END IF;
RETURN NEW;
END;
$function$;


-- The CREATE TRIGGER client_full_text_search_refresh statement creates a trigger
-- that calls the client_full_text_search_refresh() function before an insert or update operation is performed on the name, notes, or location_address columns.
CREATE TRIGGER client_full_text_search_refresh
BEFORE INSERT OR UPDATE OF name, notes, location_address
ON public.client
FOR EACH ROW
WHEN (pg_trigger_depth() < 1)
EXECUTE PROCEDURE client_full_text_search_refresh();


-- Add GIN index
--
-- This line creates a GIN (Generalized Inverted Index) index on the full_text_search column to speed up full-text search queries.
CREATE INDEX client_search_gin_idx ON client USING GIN (full_text_search gin_trgm_ops);


-- Function (required for Hasura: https://hasura.io/docs/latest/graphql/core/databases/postgres/schema/custom-functions.html)
--
-- The CREATE FUNCTION search_client(search text) statement creates a function that returns a set of client rows that match the search text.
-- The <% operator is used to perform a fuzzy search, and the SIMILARITY function is used to order the results by their similarity to the search text.
CREATE FUNCTION search_client(search text)
    RETURNS SETOF client
    AS $$
    SELECT
        *
    FROM
        client
    WHERE
        -- full_text_search column already has UNACCENT applied to it, so we don't have to re-apply
        UNACCENT(search) <% full_text_search
    ORDER BY
        SIMILARITY (search, (full_text_search)) DESC;
$$
LANGUAGE sql
STABLE;
