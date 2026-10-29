#!/bin/sh
# Creates the application database next to n8n's own database.
# Tables are created by Alembic: cd backend && alembic upgrade head
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOSQL
CREATE DATABASE "$APP_DB";
EOSQL
