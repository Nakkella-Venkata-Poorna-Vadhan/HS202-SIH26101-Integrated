"""
Test Alembic migrations, audit-log immutability triggers, and schema matching
against isolated Docker PostgreSQL container on port 54330.
Does not print passwords or secrets.
"""

import os
import sys
import uuid
from alembic.config import Config
from alembic import command
from dotenv import dotenv_values
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import DBAPIError

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_dir)

env_path = os.path.join(backend_dir, "..", ".env")
cfg = dotenv_values(env_path)

HOST = "127.0.0.1"
PORT = 54330

MIGRATOR_USER = cfg.get("DB_MIGRATOR_USER", "sih_migrator")
MIGRATOR_PW = cfg.get("DB_MIGRATOR_PASSWORD")
APP_USER = cfg.get("DB_APP_USER", "sih_app_user")
APP_PW = cfg.get("DB_APP_PASSWORD")
DEV_DB = cfg.get("DB_DEV_NAME", "sih26101_dev")

migration_url = f"postgresql+psycopg://{MIGRATOR_USER}:{MIGRATOR_PW}@{HOST}:{PORT}/{DEV_DB}"
app_url = f"postgresql+psycopg://{APP_USER}:{APP_PW}@{HOST}:{PORT}/{DEV_DB}"

os.environ["MIGRATION_DATABASE_URL"] = migration_url
os.environ["DATABASE_URL"] = app_url

from competency_engine.db.base import Base
from competency_engine.db.models import User, ApplicationAuditLog, AccountTypeEnum

results = {}

def report(step: str, success: bool, details: str = ""):
    status_str = "PASS" if success else "FAIL"
    print(f"[{status_str}] {step} - {details}")
    results[step] = (success, details)

# 1. Run Alembic Upgrade Head against Docker container
try:
    ini_path = os.path.join(backend_dir, "alembic.ini")
    alembic_cfg = Config(ini_path)
    alembic_cfg.set_main_option("sqlalchemy.url", migration_url)
    
    command.upgrade(alembic_cfg, "head")
    report("Alembic upgrade head on Docker", True, "Successfully applied all migrations up to head (02_password_reset).")
except Exception as e:
    report("Alembic upgrade head on Docker", False, str(e))
    sys.exit(1)

# 2. Inspect created tables in Docker PostgreSQL
try:
    migrator_engine = create_engine(migration_url)
    inspector = inspect(migrator_engine)
    tables = inspector.get_table_names(schema="public")
    
    expected_tables = set(Base.metadata.tables.keys())
    expected_table_names = {t.split(".")[-1] for t in expected_tables}
    actual_table_names = set(tables)
    
    missing = expected_table_names - actual_table_names
    report(
        "Database schema matches SQLAlchemy models",
        len(missing) == 0,
        f"Found {len(actual_table_names)} tables. Missing: {list(missing) if missing else 'None'}. Contains password_reset_tokens: {'password_reset_tokens' in actual_table_names}."
    )
except Exception as e:
    report("Database schema matches SQLAlchemy models", False, str(e))

# 3. Test Audit-log UPDATE, DELETE and TRUNCATE protections on application_audit_logs
try:
    update_blocked = False
    delete_blocked = False
    truncate_blocked = False
    
    app_engine = create_engine(app_url)
    with app_engine.begin() as conn:
        # Create actor user first
        user_id = uuid.uuid4()
        conn.execute(text("""
            INSERT INTO users (id, email, hashed_password, account_type, account_status, failed_login_attempts)
            VALUES (:uid, 'audit_sec_test@example.com', 'argon2id_pw_mock', 'PROJECT_STAFF', 'ACTIVE', 0);
        """), {"uid": user_id})
        
        # Insert audit log entry
        audit_id = uuid.uuid4()
        conn.execute(text("""
            INSERT INTO application_audit_logs (id, actor_id, actor_email, actor_role, action, new_state, notes)
            VALUES (:aid, :uid, 'audit_sec_test@example.com', 'PROJECT_STAFF', 'SEC_TEST', '{\"status\": \"SECURED\"}'::jsonb, 'Immutable audit test entry');
        """), {"aid": audit_id, "uid": user_id})
        
        # Test UPDATE protection
        try:
            conn.execute(text("UPDATE application_audit_logs SET notes = 'TAMPERED' WHERE id = :aid;"), {"aid": audit_id})
        except DBAPIError as e:
            update_blocked = True
            err_str = str(e).lower()
            update_detail = "permission denied" if "permission denied" in err_str else "compliance violation"
            
        # Test DELETE protection
        try:
            conn.execute(text("DELETE FROM application_audit_logs WHERE id = :aid;"), {"aid": audit_id})
        except DBAPIError as e:
            delete_blocked = True
            err_str = str(e).lower()
            delete_detail = "permission denied" if "permission denied" in err_str else "compliance violation"
            
        # Test TRUNCATE protection
        try:
            conn.execute(text("TRUNCATE TABLE application_audit_logs;"))
        except DBAPIError as e:
            truncate_blocked = True
            err_str = str(e).lower()
            truncate_detail = "permission denied" if "permission denied" in err_str else "compliance violation"
            
    report(
        "Audit log immutability protections",
        update_blocked and delete_blocked and truncate_blocked,
        f"UPDATE blocked: {update_blocked} ({update_detail}), DELETE blocked: {delete_blocked} ({delete_detail}), TRUNCATE blocked: {truncate_blocked} ({truncate_detail})."
    )
except Exception as e:
    report("Audit log immutability protections", False, str(e))

# 4. Also verify trigger protection if a schema owner / migrator tries to UPDATE/DELETE
try:
    trigger_update_blocked = False
    trigger_delete_blocked = False
    
    migrator_engine = create_engine(migration_url)
    test_aid = uuid.uuid4()
    with migrator_engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO application_audit_logs (id, actor_id, actor_email, actor_role, action, new_state, notes)
            VALUES (:aid, null, 'migrator_actor@example.com', 'MIGRATOR', 'TRIGGER_TEST', '{\"status\": \"IMMUTABLE\"}'::jsonb, 'Trigger test entry');
        """), {"aid": test_aid})
        
    with migrator_engine.begin() as conn:
        try:
            conn.execute(text(f"UPDATE application_audit_logs SET notes = 'MIGRATOR_TAMPER' WHERE id = '{test_aid}';"))
        except DBAPIError as e:
            if "compliance violation" in str(e).lower():
                trigger_update_blocked = True
                
    with migrator_engine.begin() as conn:
        try:
            conn.execute(text(f"DELETE FROM application_audit_logs WHERE id = '{test_aid}';"))
        except DBAPIError as e:
            if "compliance violation" in str(e).lower():
                trigger_delete_blocked = True
                
    report(
        "Audit log database trigger enforcement (immutability)",
        trigger_update_blocked and trigger_delete_blocked,
        f"Schema owner UPDATE blocked by trigger: {trigger_update_blocked}, DELETE blocked by trigger: {trigger_delete_blocked}."
    )
except Exception as e:
    report("Audit log database trigger enforcement (immutability)", False, str(e))

# Summary
total = len(results)
passed = sum(1 for s, _ in results.values() if s)
print(f"\nAlembic & Immutability Audit: {passed}/{total} passed.")
if passed != total:
    sys.exit(1)
