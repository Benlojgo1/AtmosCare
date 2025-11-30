#!/bin/bash
set -e

# Wait for PostgreSQL to become available
until pg_isready -q -h localhost -U $POSTGRES_USER; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing schema and seed files"

# Execute schema and seed data scripts against the target database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    \i /docker-entrypoint-initdb.d/01_schema.sql
    \i /docker-entrypoint-initdb.d/02_seed_data.sql
EOSQL

echo "Database initialization complete."