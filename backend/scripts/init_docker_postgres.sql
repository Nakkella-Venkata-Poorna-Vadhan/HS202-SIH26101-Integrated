-- Schema and Least-Privilege Permissions Configuration for SIH26101
-- This file is mounted to /tmp/sih26101_init.sql (OUTSIDE /docker-entrypoint-initdb.d/)
-- It is executed per-database exactly once by /docker-entrypoint-initdb.d/01_init_roles.sh

\set ON_ERROR_STOP on

-- 1. Revoke all privileges from public pseudo-role
REVOKE ALL ON SCHEMA public FROM PUBLIC;

-- 2. Establish sih_migrator as owner of public schema
ALTER SCHEMA public OWNER TO sih_migrator;
GRANT ALL ON SCHEMA public TO sih_migrator;

-- 3. Grant runtime user USAGE on schema public, strictly NO CREATE
GRANT USAGE ON SCHEMA public TO sih_app_user;
REVOKE CREATE ON SCHEMA public FROM sih_app_user;

-- 4. Configure default privileges for future objects created by sih_migrator
ALTER DEFAULT PRIVILEGES FOR ROLE sih_migrator IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO sih_app_user;

ALTER DEFAULT PRIVILEGES FOR ROLE sih_migrator IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO sih_app_user;
