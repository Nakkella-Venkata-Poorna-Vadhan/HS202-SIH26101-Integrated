#!/usr/bin/env bash
set -euo pipefail

# Fail-fast validation of required environment credentials
if [ -z "${SIH_PG_MIGRATOR_PASSWORD:-}" ]; then
    echo "FATAL: SIH_PG_MIGRATOR_PASSWORD (or DB_MIGRATOR_PASSWORD) is required for Docker PostgreSQL initialization." >&2
    exit 1
fi

if [ -z "${SIH_PG_PASSWORD:-}" ]; then
    echo "FATAL: SIH_PG_PASSWORD (or DB_APP_PASSWORD) is required for Docker PostgreSQL initialization." >&2
    exit 1
fi

DEV_DB="${DB_DEV_NAME:-sih26101_dev}"
TEST_DB="${DB_TEST_NAME:-sih26101_test}"

echo "Starting SIH26101 Docker database initialization..."
echo "Configuring roles (sih_migrator, sih_app_user) and databases (${DEV_DB}, ${TEST_DB})..."

# 1. Provision cluster roles and databases safely using psql variables and quoted heredoc
psql -v ON_ERROR_STOP=1 \
     -v migrator_password="$SIH_PG_MIGRATOR_PASSWORD" \
     -v app_password="$SIH_PG_PASSWORD" \
     -v dev_db="$DEV_DB" \
     -v test_db="$TEST_DB" \
     --username "$POSTGRES_USER" \
     --dbname "$POSTGRES_DB" <<'EOSQL'
    CREATE ROLE sih_migrator WITH LOGIN PASSWORD :'migrator_password' NOSUPERUSER NOCREATEDB NOCREATEROLE;
    CREATE ROLE sih_app_user WITH LOGIN PASSWORD :'app_password' NOSUPERUSER NOCREATEDB NOCREATEROLE;
    CREATE DATABASE :"dev_db" OWNER sih_migrator;
    CREATE DATABASE :"test_db" OWNER sih_migrator;
EOSQL

# 2. Configure schema ownership and least-privilege permissions in each database exactly once
for TARGET_DB in "$DEV_DB" "$TEST_DB"; do
    echo "Configuring schema and permissions for ${TARGET_DB} from /tmp/sih26101_init.sql..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$TARGET_DB" -f /tmp/sih26101_init.sql
done

echo "SIH26101 Docker database initialization completed successfully."
