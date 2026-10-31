"""
PostgreSQL Role Provisioning and Security Hardening Script for SIH26101.
Establishes two distinct roles following the principle of least privilege:
1. sih_migrator: Schema owner authorized to run Alembic DDL migrations.
2. sih_app_user: Runtime application role with DML permissions (no CREATEDB, no DDL).
Configures SCRAM-SHA-256 authentication and restricts cluster access.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg
from psycopg import sql

# Locate and load .env from workspace
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "54329")
POSTGRES_ADMIN_USER = os.getenv("POSTGRES_ADMIN_USER", "postgres")
POSTGRES_ADMIN_PASSWORD = os.getenv("POSTGRES_ADMIN_PASSWORD")
DB_MIGRATOR_USER = os.getenv("DB_MIGRATOR_USER", "sih_migrator")
DB_MIGRATOR_PASSWORD = os.getenv("DB_MIGRATOR_PASSWORD")
DB_APP_USER = os.getenv("DB_APP_USER", "sih_app_user")
DB_APP_PASSWORD = os.getenv("DB_APP_PASSWORD")
DB_DEV_NAME = os.getenv("DB_DEV_NAME", "sih26101_dev")
DB_TEST_NAME = os.getenv("DB_TEST_NAME", "sih26101_test")

if not DB_MIGRATOR_PASSWORD or not DB_APP_PASSWORD or not POSTGRES_ADMIN_PASSWORD:
    print("ERROR: Required passwords are not set in environment (.env).")
    print("Ensure POSTGRES_ADMIN_PASSWORD, DB_MIGRATOR_PASSWORD, and DB_APP_PASSWORD are provided.")
    sys.exit(1)


def connect_admin() -> psycopg.Connection:
    """
    Connect to postgres administrative database using administrator credentials.
    Requires valid credentials; never falls back to passwordless authentication.
    """
    if not POSTGRES_ADMIN_PASSWORD:
        raise ValueError("POSTGRES_ADMIN_PASSWORD must be configured in environment.")
    try:
        conn = psycopg.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_ADMIN_USER,
            password=POSTGRES_ADMIN_PASSWORD,
            dbname="postgres",
            autocommit=True,
        )
        return conn
    except Exception as e:
        print(f"FATAL: Administrator authentication failed for '{POSTGRES_ADMIN_USER}': {e}", file=sys.stderr)
        print("Stopping provisioning: Valid administrator credentials are required. No passwordless retry.", file=sys.stderr)
        raise
def setup_roles_and_databases():
    print(f"Connecting to PostgreSQL on {POSTGRES_HOST}:{POSTGRES_PORT} as {POSTGRES_ADMIN_USER}...")
    with connect_admin() as conn:
        with conn.cursor() as cur:
            # 1. Update postgres admin password
            print("Securing postgres superuser with SCRAM-SHA-256 password...")
            cur.execute(
                sql.SQL("ALTER ROLE {} WITH PASSWORD {}").format(
                    sql.Identifier(POSTGRES_ADMIN_USER),
                    sql.Literal(POSTGRES_ADMIN_PASSWORD),
                )
            )

            # 2. Provision sih_migrator (Schema owner, no superuser, no createdb)
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (DB_MIGRATOR_USER,))
            if not cur.fetchone():
                print(f"Creating role {DB_MIGRATOR_USER} (Schema Migrator)...")
                cur.execute(
                    sql.SQL("CREATE ROLE {} WITH LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE").format(
                        sql.Identifier(DB_MIGRATOR_USER),
                        sql.Literal(DB_MIGRATOR_PASSWORD),
                    )
                )
            else:
                print(f"Updating role {DB_MIGRATOR_USER} permissions and password...")
                cur.execute(
                    sql.SQL("ALTER ROLE {} WITH LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE").format(
                        sql.Identifier(DB_MIGRATOR_USER),
                        sql.Literal(DB_MIGRATOR_PASSWORD),
                    )
                )

            # 3. Provision sih_app_user (Runtime user, strictly least-privilege)
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (DB_APP_USER,))
            if not cur.fetchone():
                print(f"Creating role {DB_APP_USER} (Runtime User)...")
                cur.execute(
                    sql.SQL("CREATE ROLE {} WITH LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE").format(
                        sql.Identifier(DB_APP_USER),
                        sql.Literal(DB_APP_PASSWORD),
                    )
                )
            else:
                print(f"Updating role {DB_APP_USER} permissions (stripping CREATEDB/CREATEROLE)...")
                cur.execute(
                    sql.SQL("ALTER ROLE {} WITH LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE").format(
                        sql.Identifier(DB_APP_USER),
                        sql.Literal(DB_APP_PASSWORD),
                    )
                )

            # 4. Provision databases owned by sih_migrator
            for dbname in [DB_DEV_NAME, DB_TEST_NAME]:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
                if not cur.fetchone():
                    print(f"Creating database {dbname} owned by {DB_MIGRATOR_USER}...")
                    cur.execute(
                        sql.SQL("CREATE DATABASE {} OWNER {}").format(
                            sql.Identifier(dbname),
                            sql.Identifier(DB_MIGRATOR_USER),
                        )
                    )
                else:
                    print(f"Ensuring database {dbname} is owned by {DB_MIGRATOR_USER}...")
                    cur.execute(
                        sql.SQL("ALTER DATABASE {} OWNER TO {}").format(
                            sql.Identifier(dbname),
                            sql.Identifier(DB_MIGRATOR_USER),
                        )
                    )

    # 5. Configure schema permissions and default privileges in each database
    for dbname in [DB_DEV_NAME, DB_TEST_NAME]:
        print(f"Configuring schema and least-privilege grants in {dbname}...")
        with psycopg.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_ADMIN_USER,
            password=POSTGRES_ADMIN_PASSWORD,
            dbname=dbname,
            autocommit=True,
        ) as db_conn:
            with db_conn.cursor() as cur:
                # Revoke all public schema permissions from PUBLIC
                cur.execute("REVOKE ALL ON SCHEMA public FROM PUBLIC;")
                # Ensure sih_migrator owns and has all privileges on schema public
                cur.execute(sql.SQL("ALTER SCHEMA public OWNER TO {}").format(sql.Identifier(DB_MIGRATOR_USER)))
                cur.execute(sql.SQL("GRANT ALL ON SCHEMA public TO {}").format(sql.Identifier(DB_MIGRATOR_USER)))

                # Grant USAGE on schema public to runtime user, but strictly NO CREATE
                cur.execute(sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(sql.Identifier(DB_APP_USER)))
                cur.execute(sql.SQL("REVOKE CREATE ON SCHEMA public FROM {}").format(sql.Identifier(DB_APP_USER)))

                # Configure default privileges for future tables created by sih_migrator
                cur.execute(
                    sql.SQL(
                        "ALTER DEFAULT PRIVILEGES FOR ROLE {} IN SCHEMA public "
                        "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {}"
                    ).format(sql.Identifier(DB_MIGRATOR_USER), sql.Identifier(DB_APP_USER))
                )
                cur.execute(
                    sql.SQL(
                        "ALTER DEFAULT PRIVILEGES FOR ROLE {} IN SCHEMA public "
                        "GRANT USAGE, SELECT ON SEQUENCES TO {}"
                    ).format(sql.Identifier(DB_MIGRATOR_USER), sql.Identifier(DB_APP_USER))
                )

                # Grant on existing tables if any
                cur.execute(
                    sql.SQL("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {}").format(
                        sql.Identifier(DB_APP_USER)
                    )
                )
                cur.execute(
                    sql.SQL("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {}").format(
                        sql.Identifier(DB_APP_USER)
                    )
                )

                # Specifically harden application_audit_logs if table exists
                cur.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'application_audit_logs'")
                if cur.fetchone():
                    print("Hardening application_audit_logs privileges for runtime user...")
                    cur.execute(
                        sql.SQL("REVOKE UPDATE, DELETE, TRUNCATE ON application_audit_logs FROM {}").format(
                            sql.Identifier(DB_APP_USER)
                        )
                    )
                    cur.execute(
                        sql.SQL("GRANT SELECT, INSERT ON application_audit_logs TO {}").format(
                            sql.Identifier(DB_APP_USER)
                        )
                    )

    print("Role separation and permissions configured successfully.")


def harden_pg_hba_and_config():
    """Update postgresql.conf and pg_hba.conf for SCRAM-SHA-256 authentication."""
    pgdata = ROOT_DIR / "backend" / "data" / "pgdata"
    if not pgdata.exists():
        print(f"Warning: {pgdata} not found; skipping native configuration file updates.")
        return

    hba_path = pgdata / "pg_hba.conf"
    conf_path = pgdata / "postgresql.conf"

    # 1. Update postgresql.conf
    if conf_path.exists():
        conf_text = conf_path.read_text(encoding="utf-8")
        if "password_encryption = scram-sha-256" not in conf_text:
            conf_text += "\n# Explicit SCRAM-SHA-256 configuration\npassword_encryption = scram-sha-256\n"
            conf_path.write_text(conf_text, encoding="utf-8")
            print("Updated postgresql.conf with password_encryption = scram-sha-256.")

    # 2. Update pg_hba.conf
    if hba_path.exists():
        hba_content = """# PostgreSQL Client Authentication Configuration File (Hardened)
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     scram-sha-256
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
"""
        hba_path.write_text(hba_content, encoding="utf-8")
        print("Updated pg_hba.conf to enforce scram-sha-256 on loopback addresses.")

    # 3. Reload PostgreSQL configuration
    with connect_admin() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_reload_conf();")
            print("Reloaded PostgreSQL configuration.")


def verify_connections():
    """Verify SCRAM-SHA-256 authentication and least-privilege constraints."""
    print("Verifying connections...")

    # 1. Test valid connection as sih_migrator
    migrator_conn = f"host={POSTGRES_HOST} port={POSTGRES_PORT} user={DB_MIGRATOR_USER} password={DB_MIGRATOR_PASSWORD} dbname={DB_DEV_NAME}"
    with psycopg.connect(migrator_conn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_user, session_user;")
            user_info = cur.fetchone()
            print(f"Verified connection for {user_info[0]} ({DB_MIGRATOR_USER}) on {DB_DEV_NAME}")

    # 2. Test valid connection as sih_app_user
    app_conn = f"host={POSTGRES_HOST} port={POSTGRES_PORT} user={DB_APP_USER} password={DB_APP_PASSWORD} dbname={DB_DEV_NAME}"
    with psycopg.connect(app_conn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_user, session_user;")
            user_info = cur.fetchone()
            print(f"Verified connection for {user_info[0]} ({DB_APP_USER}) on {DB_DEV_NAME}")

    # 3. Test unauthenticated connection is rejected
    unauth_conn = f"host={POSTGRES_HOST} port={POSTGRES_PORT} user={DB_APP_USER} dbname={DB_DEV_NAME}"
    try:
        with psycopg.connect(unauth_conn) as conn:
            pass
        print("ERROR: Unauthenticated connection succeeded unexpectedly!")
        sys.exit(1)
    except Exception as e:
        print(f"Verified unauthenticated access is rejected as expected: {type(e).__name__}")

    # 4. Test wrong password is rejected
    wrong_conn = f"host={POSTGRES_HOST} port={POSTGRES_PORT} user={DB_APP_USER} password=WRONG_PASSWORD dbname={DB_DEV_NAME}"
    try:
        with psycopg.connect(wrong_conn) as conn:
            pass
        print("ERROR: Wrong password connection succeeded unexpectedly!")
        sys.exit(1)
    except Exception as e:
        print(f"Verified wrong password is rejected as expected: {type(e).__name__}")

    print("All connection validations passed successfully!")


if __name__ == "__main__":
    setup_roles_and_databases()
    harden_pg_hba_and_config()
    verify_connections()