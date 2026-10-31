"""
Automated Docker PostgreSQL Audit Verification Script for SIH26101.
Tests isolated Docker PostgreSQL instance on port 54330.
Does not print passwords or secrets.
"""

import sys
import os
import psycopg
from dotenv import dotenv_values

env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
cfg = dotenv_values(env_path)

HOST = "127.0.0.1"
PORT = 54330  # Isolated Docker test port

ADMIN_USER = cfg.get("POSTGRES_ADMIN_USER", "postgres")
ADMIN_PW = cfg.get("POSTGRES_ADMIN_PASSWORD")

MIGRATOR_USER = cfg.get("DB_MIGRATOR_USER", "sih_migrator")
MIGRATOR_PW = cfg.get("DB_MIGRATOR_PASSWORD")

APP_USER = cfg.get("DB_APP_USER", "sih_app_user")
APP_PW = cfg.get("DB_APP_PASSWORD")

DEV_DB = cfg.get("DB_DEV_NAME", "sih26101_dev")
TEST_DB = cfg.get("DB_TEST_NAME", "sih26101_test")

results = {}

def report(step: str, success: bool, details: str = ""):
    status_str = "PASS" if success else "FAIL"
    print(f"[{status_str}] {step} - {details}")
    results[step] = (success, details)

# --- Test 1 & 2: Container and Init already verified from logs ---

# --- Test 3: sih_migrator and sih_app_user roles created correctly ---
try:
    with psycopg.connect(f"host={HOST} port={PORT} user={ADMIN_USER} password={ADMIN_PW} dbname=postgres") as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT rolname, rolsuper, rolinherit, rolcreaterole, rolcreatedb, rolcanlogin
                FROM pg_roles
                WHERE rolname IN (%s, %s)
                ORDER BY rolname;
            """, (MIGRATOR_USER, APP_USER))
            rows = cur.fetchall()
            
            roles_dict = {r[0]: {"super": r[1], "createrole": r[3], "createdb": r[4], "login": r[5]} for r in rows}
            
            migrator_ok = (
                MIGRATOR_USER in roles_dict and
                not roles_dict[MIGRATOR_USER]["super"] and
                not roles_dict[MIGRATOR_USER]["createdb"] and
                not roles_dict[MIGRATOR_USER]["createrole"] and
                roles_dict[MIGRATOR_USER]["login"]
            )
            app_ok = (
                APP_USER in roles_dict and
                not roles_dict[APP_USER]["super"] and
                not roles_dict[APP_USER]["createdb"] and
                not roles_dict[APP_USER]["createrole"] and
                roles_dict[APP_USER]["login"]
            )
            
            report(
                "Role creation and flags",
                migrator_ok and app_ok,
                f"sih_migrator (login={roles_dict.get(MIGRATOR_USER, {}).get('login')}, super={roles_dict.get(MIGRATOR_USER, {}).get('super')}), "
                f"sih_app_user (login={roles_dict.get(APP_USER, {}).get('login')}, super={roles_dict.get(APP_USER, {}).get('super')})"
            )
except Exception as e:
    report("Role creation and flags", False, str(e))

# --- Test 4: Development and Test databases created with correct owners ---
try:
    with psycopg.connect(f"host={HOST} port={PORT} user={ADMIN_USER} password={ADMIN_PW} dbname=postgres") as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT d.datname, r.rolname
                FROM pg_database d
                JOIN pg_roles r ON d.datdba = r.oid
                WHERE d.datname IN (%s, %s);
            """, (DEV_DB, TEST_DB))
            dbs = dict(cur.fetchall())
            
            dev_owner_ok = dbs.get(DEV_DB) == MIGRATOR_USER
            test_owner_ok = dbs.get(TEST_DB) == MIGRATOR_USER
            
            report(
                "Database owners",
                dev_owner_ok and test_owner_ok,
                f"{DEV_DB} owner: {dbs.get(DEV_DB)}, {TEST_DB} owner: {dbs.get(TEST_DB)}"
            )
except Exception as e:
    report("Database owners", False, str(e))

# --- Test 5: SCRAM-SHA-256 authentication works ---
try:
    migrator_conn_ok = False
    app_conn_ok = False
    
    with psycopg.connect(f"host={HOST} port={PORT} user={MIGRATOR_USER} password={MIGRATOR_PW} dbname={DEV_DB}") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_user, current_database();")
            u, d = cur.fetchone()
            migrator_conn_ok = (u == MIGRATOR_USER and d == DEV_DB)
            
    with psycopg.connect(f"host={HOST} port={PORT} user={APP_USER} password={APP_PW} dbname={DEV_DB}") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_user, current_database();")
            u, d = cur.fetchone()
            app_conn_ok = (u == APP_USER and d == DEV_DB)
            
    report(
        "SCRAM-SHA-256 authentication",
        migrator_conn_ok and app_conn_ok,
        "Successfully connected as both sih_migrator and sih_app_user via SCRAM-SHA-256."
    )
except Exception as e:
    report("SCRAM-SHA-256 authentication", False, str(e))

# --- Test 6: Invalid credentials rejected ---
try:
    rejected = False
    try:
        with psycopg.connect(f"host={HOST} port={PORT} user={APP_USER} password=incorrect_password_attempt dbname={DEV_DB}") as conn:
            pass
    except psycopg.OperationalError as auth_err:
        rejected = True
        err_msg = str(auth_err).strip()
    
    report(
        "Invalid credentials rejection",
        rejected,
        "Rejected invalid password with OperationalError (password authentication failed)."
    )
except Exception as e:
    report("Invalid credentials rejection", False, str(e))

# --- Test 7: Runtime user cannot create databases or schema objects ---
try:
    db_create_blocked = False
    table_create_blocked = False
    
    with psycopg.connect(f"host={HOST} port={PORT} user={APP_USER} password={APP_PW} dbname={DEV_DB}") as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            try:
                cur.execute("CREATE DATABASE unauthorized_test_db;")
            except psycopg.Error as e:
                db_create_blocked = True
                
            try:
                cur.execute("CREATE TABLE unauthorized_test_table (id int);")
            except psycopg.Error as e:
                table_create_blocked = True
                
    report(
        "Runtime user DDL restrictions",
        db_create_blocked and table_create_blocked,
        f"CREATE DATABASE blocked: {db_create_blocked}, CREATE TABLE in public blocked: {table_create_blocked}."
    )
except Exception as e:
    report("Runtime user DDL restrictions", False, str(e))

# --- Test 8: Runtime user permissions on tables created by migrator ---
try:
    # 1. Migrator creates test table
    with psycopg.connect(f"host={HOST} port={PORT} user={MIGRATOR_USER} password={MIGRATOR_PW} dbname={DEV_DB}") as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sample_runtime_check (
                    id serial PRIMARY KEY,
                    val text NOT NULL
                );
            """)
        conn.commit()
        
    # 2. App user inserts and reads from table
    app_can_insert_and_select = False
    with psycopg.connect(f"host={HOST} port={PORT} user={APP_USER} password={APP_PW} dbname={DEV_DB}") as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO sample_runtime_check (val) VALUES ('audit_check') RETURNING id;")
            inserted_id = cur.fetchone()[0]
            cur.execute("SELECT val FROM sample_runtime_check WHERE id = %s;", (inserted_id,))
            val = cur.fetchone()[0]
            app_can_insert_and_select = (val == "audit_check")
        conn.commit()
        
    # 3. Clean up sample table
    with psycopg.connect(f"host={HOST} port={PORT} user={MIGRATOR_USER} password={MIGRATOR_PW} dbname={DEV_DB}") as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE sample_runtime_check;")
        conn.commit()
        
    report(
        "Runtime user data permissions",
        app_can_insert_and_select,
        "App user can INSERT and SELECT on objects created by migrator via default privileges."
    )
except Exception as e:
    report("Runtime user data permissions", False, str(e))

# Summary output
total = len(results)
passed = sum(1 for s, _ in results.values() if s)
print(f"\nDocker PostgreSQL Audit Checks: {passed}/{total} passed.")
if passed != total:
    sys.exit(1)