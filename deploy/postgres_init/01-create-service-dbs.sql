-- Create separate databases for each service to avoid Alembic version conflicts.
-- Note: initdb scripts are only executed on FIRST initialization of the data dir
-- (i.e. when ./postgres_data is empty).

SELECT 'CREATE DATABASE nurse_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'nurse_db')\gexec

SELECT 'CREATE DATABASE administrator_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'administrator_db')\gexec
