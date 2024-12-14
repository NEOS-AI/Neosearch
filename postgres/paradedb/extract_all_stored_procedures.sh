# Extract all stored procedures
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
