-- Admin query to retrieve all available text search configurations
\dF

-- Check all available text search configurations
SELECT cfgname FROM pg_ts_config;
