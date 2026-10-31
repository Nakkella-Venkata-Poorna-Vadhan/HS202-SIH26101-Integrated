# SIH26101 — Phase 1.4 Implementation: SQL Credential Hardening & Encryption-Key Audit

**Document Version:** 1.4  
**Status:** Completed, Hardened & Validated  
**Architecture Reference:** `docs/FINAL_ARCHITECTURE_PLAN_v2.7.md`  
**Working Copy Branch:** `phase1/database-foundation`  
**Working Copy Location:** `D:\Projects\SIH26101\SIH26101-Integrated-Phase1`  

---

## 1. Executive Summary

Phase 1 establishes the relational database foundation for the **Official Statistics Competency Intelligence and Adaptive Learning Platform (SIH26101)**. In Phase 1.2, all remaining security gaps, credential hygiene concerns, and verification requirements were comprehensively resolved:

1. **Docker Credential Hygiene:** Removed hardcoded passwords from `init_docker_postgres.sql`, introduced `init_docker_postgres.sh` with fail-fast environment variable validation, and updated `docker-compose.yml` with strict `${VAR:?error}` syntax.
2. **Elimination of Passwordless Administrator Fallback:** `connect_admin()` in `setup_postgres_db.py` strictly requires valid administrator credentials and stops immediately with a diagnostic error upon failure, never attempting passwordless connection or weakening cluster authentication.
3. **Strict Migration Role Separation:** `MIGRATION_DATABASE_URL` and `TEST_MIGRATION_DATABASE_URL` in `config.py` require distinct migration credentials and raise an explicit `ValueError` if missing, completely eliminating silent fallbacks to runtime application URLs.
4. **Actual Autonomous Audit Testing & Trust Boundary Documentation:** `test_08` tests the actual `get_audit_db()` generator implementation. Transparently documented that the audit session operates under the runtime role (`sih_app_user`) with table-level privilege restrictions and trigger enforcement, providing transaction-level isolation rather than an independent database user.
5. **Rotated Development Credentials:** All database passwords (postgres superuser, migrator, application user) and encryption keys (JWT secret, document KEK, vault key) were freshly rotated using high-entropy URL-safe characters without exposing secrets in logs or reports.
6. **Workspace Preservation Verified:** All 26 baseline files (including the 12 untracked baseline files and 14 tracked modifications) were verified via SHA-256 hash comparison between the original repository and Phase 1 working copy with a 100% match.
7. **Full Verification:** All 20 PostgreSQL integration tests pass, all 280 backend tests pass, frontend TypeScript emits 0 errors, and production Vite bundle builds cleanly in under 10 seconds.

---

## 2. Docker Credential Hygiene & Container Initialization

### Prior Vulnerability
Previously, `init_docker_postgres.sql` contained hardcoded plaintext passwords (`DockerMigratorPass2026!` / `DockerAppUserPass2026!`), and `docker-compose.yml` lacked fail-fast enforcement for missing environment variables.

### Phase 1.2 Hardening
1. **Variable Substitution in SQL (`init_docker_postgres.sql`):**
   ```sql
   \set ON_ERROR_STOP on
   CREATE ROLE sih_migrator WITH LOGIN PASSWORD :'migrator_password' NOSUPERUSER NOCREATEDB NOCREATEROLE;
   CREATE ROLE sih_app_user WITH LOGIN PASSWORD :'app_password' NOSUPERUSER NOCREATEDB NOCREATEROLE;
   ```
2. **Container Entrypoint Script (`init_docker_postgres.sh`):**
   Validates `SIH_PG_MIGRATOR_PASSWORD` and `SIH_PG_PASSWORD`. If either is empty or missing, the initialization script aborts immediately with an informative fatal error code:
   ```bash
   if [ -z "${SIH_PG_MIGRATOR_PASSWORD:-}" ] || [ -z "${SIH_PG_PASSWORD:-}" ]; then
       echo "FATAL: SIH_PG_MIGRATOR_PASSWORD and SIH_PG_PASSWORD are required." >&2
       exit 1
   fi
   ```
3. **Fail-Fast Compose Schema (`docker-compose.yml`):**
   Uses Compose variable interpolation assertions (`${VAR:?error}`) so that running `docker compose up` without configured credentials in `.env` halts before starting the PostgreSQL service:
   ```yaml
   POSTGRES_PASSWORD: ${POSTGRES_ADMIN_PASSWORD:?POSTGRES_ADMIN_PASSWORD must be provided in .env}
   SIH_PG_MIGRATOR_PASSWORD: ${DB_MIGRATOR_PASSWORD:?DB_MIGRATOR_PASSWORD must be provided in .env}
   SIH_PG_PASSWORD: ${DB_APP_PASSWORD:?DB_APP_PASSWORD must be provided in .env}
   ```

---

## 3. Administrator Connection Security

### Removal of Insecure Fallback (`setup_postgres_db.py`)
Previously, `connect_admin()` caught exceptions and attempted a fallback connection without a password. In Phase 1.2, this fallback was eliminated:

```python
def connect_admin() -> psycopg.Connection:
    if not POSTGRES_ADMIN_PASSWORD:
        raise ValueError("POSTGRES_ADMIN_PASSWORD must be configured in environment.")
    try:
        return psycopg.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_ADMIN_USER,
            password=POSTGRES_ADMIN_PASSWORD,
            dbname="postgres",
            autocommit=True,
        )
    except Exception as e:
        print(f"FATAL: Administrator authentication failed for '{POSTGRES_ADMIN_USER}': {e}", file=sys.stderr)
        print("Stopping provisioning: Valid administrator credentials are required. No passwordless retry.", file=sys.stderr)
        raise
```
Tested and validated by integration test `test_20_admin_connect_requires_valid_credentials_without_passwordless_fallback`.

---

## 4. Migration vs. Runtime Role Separation

### Configuration Enforcement (`config.py`)
`MIGRATION_DATABASE_URL` and `TEST_MIGRATION_DATABASE_URL` now enforce migration credentials and strictly reject falling back to `DATABASE_URL`:
```python
if not mig_pw:
    raise ValueError(
        "MIGRATION_DATABASE_URL or DB_MIGRATOR_PASSWORD is not configured. "
        "Schema migrations strictly require distinct migration credentials (sih_migrator) "
        "and cannot fall back to runtime application credentials."
    )
```
- Ordinary application code connects as `sih_app_user` (least-privilege DML).
- Alembic migrations (`backend/migrations/env.py`) connect as `sih_migrator` (schema owner).
- Tested and validated by integration test `test_19_migration_urls_require_migration_credentials_and_never_fallback`.

---

## 5. Autonomous Audit Implementation & Accurate Trust Boundary

### Audit Session Architecture (`session.py`)
`get_audit_db()` yields a dedicated session with its own connection from the pool.
```python
def get_audit_db(db_url: str | None = None) -> Generator[Session, None, None]:
    engine = get_engine(db_url)
    session_factory = get_session_factory(engine)
    session: Session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

### Trust Boundary & Role Isolation Disclosure
- **Role Isolation:** The audit session connects under `sih_app_user`. It does **NOT** use a separate database user role.
- **Permission Boundary:** Under Phase 1 grants, `sih_app_user` is permitted `SELECT` and `INSERT` on `application_audit_logs`, while `UPDATE`, `DELETE`, and `TRUNCATE` are revoked and guarded by triggers.
- **Transaction Isolation:** `get_audit_db()` provides **transaction-level isolation**. Because it operates on an independent connection, its `commit()` persists even when the enclosing business transaction fails and issues `rollback()`.
- Validated in `test_08_audit_log_survives_failed_business_transaction`.

---

## 6. Integration Test Suite Matrix (20 Tests)

All 20 tests run against native PostgreSQL 18.6 on port 54329:

| Test ID | Test Function | Purpose / Validation Focus | Result |
|---|---|---|---|
| 01 | `test_01_database_connection_and_health` | Pool health probe (`SELECT 1`) | **PASSED** |
| 02 | `test_02_database_isolation` | Dev vs Test database physical isolation | **PASSED** |
| 03 | `test_03_authentication_fails_without_valid_credentials` | Rejection of bad/missing credentials under SCRAM-SHA-256 | **PASSED** |
| 04 | `test_04_runtime_user_cannot_create_database` | Rejection of `CREATE DATABASE` by runtime role | **PASSED** |
| 05 | `test_05_runtime_user_cannot_create_or_drop_schema_objects` | Rejection of DDL (`CREATE/DROP TABLE`) by runtime role | **PASSED** |
| 06 | `test_06_runtime_user_audit_log_update_delete_truncate_rejection` | Rejection of `UPDATE`, `DELETE`, `TRUNCATE` on audit logs | **PASSED** |
| 07 | `test_07_runtime_user_can_perform_ordinary_application_operations` | Standard DML (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) on app entities | **PASSED** |
| 08 | `test_08_audit_log_survives_failed_business_transaction` | Actual `get_audit_db()` audit persistence across business rollback | **PASSED** |
| 09 | `test_09_migration_role_can_manage_schema` | Verification of schema DDL authority for `sih_migrator` | **PASSED** |
| 10 | `test_10_foreign_key_restricts` | Foreign key referential integrity constraints | **PASSED** |
| 11 | `test_11_geographic_level_integrity_valid_scopes` | NATIONAL, ZONE, STATE, STATION geographic scopes | **PASSED** |
| 12 | `test_12_geographic_level_integrity_invalid_scope_rejected` | Rejection of invalid geographic hierarchy combinations | **PASSED** |
| 13 | `test_13_composite_application_employee_reference` | Multi-column composite foreign key integrity | **PASSED** |
| 14 | `test_14_partial_unique_index_single_pending_application` | Partial unique index restricting pending applications | **PASSED** |
| 15 | `test_15_unique_nulls_not_distinct_on_scopes` | PostgreSQL 15+ `UNIQUE NULLS NOT DISTINCT` on scopes | **PASSED** |
| 16 | `test_16_independent_appeal_reviewer_check_constraint` | *Nemo judex in causa sua* check constraint | **PASSED** |
| 17 | `test_17_single_active_assignment_per_employee` | Single active supervisory assignment partial unique index | **PASSED** |
| 18 | `test_18_document_crypto_shredding_metadata` | Cryptographic erasure metadata manipulation | **PASSED** |
| 19 | `test_19_migration_urls_require_migration_credentials_and_never_fallback` | Enforces explicit migration credentials without fallback | **PASSED** |
| 20 | `test_20_admin_connect_requires_valid_credentials_without_passwordless_fallback` | Rejects bad admin passwords and halts without trust fallback | **PASSED** |

---

## 7. Baseline Preservation Verification (SHA-256)

Comparison of all 26 baseline files between `D:\Projects\SIH26101\SIH26101-Integrated` and `D:\Projects\SIH26101\SIH26101-Integrated-Phase1`:

| File Relative Path | Type | SHA-256 Hash | Status |
|---|---|---|---|
| `backend/data/uploads/documents/SRC-UP-20261026064238-BEA04BE9_MoSPI_Official_Statistics_Training_Note.txt` | Untracked baseline | `45521bc8172fd0a0...` | **MATCH** |
| `backend/data/uploads/documents/SRC-UP-20261026064303-203762CA_MoSPI_Official_Statistics_Training_Note.txt` | Untracked baseline | `45521bc8172fd0a0...` | **MATCH** |
| `backend/data/uploads/extracted/SRC-UP-20261026064238-BEA04BE9.json` | Untracked baseline | `85d0729b90e8a9bd...` | **MATCH** |
| `backend/data/uploads/extracted/SRC-UP-20261026064303-203762CA.json` | Untracked baseline | `e9e6fb916adb22b0...` | **MATCH** |
| `docs/FEATURE_LEDGER.md` | Untracked baseline | `6977bc6c51becb53...` | **MATCH** |
| `docs/FINAL_ARCHITECTURE_PLAN_v2.2.md` | Untracked baseline | `55fe05d389788248...` | **MATCH** |
| `docs/FINAL_ARCHITECTURE_PLAN_v2.3.md` | Untracked baseline | `5c9fac8779e69262...` | **MATCH** |
| `docs/FINAL_ARCHITECTURE_PLAN_v2.4.md` | Untracked baseline | `26db7f36e71e74d0...` | **MATCH** |
| `docs/FINAL_ARCHITECTURE_PLAN_v2.5.md` | Untracked baseline | `be65a64e4035fe50...` | **MATCH** |
| `docs/FINAL_ARCHITECTURE_PLAN_v2.6.md` | Untracked baseline | `0527e6d9cc3d3444...` | **MATCH** |
| `docs/FINAL_ARCHITECTURE_PLAN_v2.7.md` | Untracked baseline | `c5fdcc7663589058...` | **MATCH** |
| `docs/FINAL_VERIFICATION_REPORT.md` | Untracked baseline | `1c414b8db1d57a79...` | **MATCH** |
| `docs/FRONTEND_BACKEND_INTEGRATION_AUDIT.md` | Untracked baseline | `434607bd32264933...` | **MATCH** |
| `docs/REGRESSION_REPORT.md` | Untracked baseline | `7437ffd928ce1339...` | **MATCH** |
| `backend/competency_engine/api.py` | Tracked baseline mod | `acdc43009e4f13dc...` | **MATCH** |
| `backend/data/interim/evaluation_metrics_stage47.json` | Tracked baseline mod | `f8efdc504f307966...` | **MATCH** |
| `backend/data/interim/recommendation_evaluation_metrics.json` | Tracked baseline mod | `0b644692734897dc...` | **MATCH** |
| `backend/data/interim/recommendation_evaluation_metrics_v2.json` | Tracked baseline mod | `0b644692734897dc...` | **MATCH** |
| `backend/data/interim/source_citation_verification.json` | Tracked baseline mod | `722c9ab3170447e8...` | **MATCH** |
| `backend/data/learners/learning_activities.json` | Tracked baseline mod | `14a5f32802888bfe...` | **MATCH** |
| `backend/data/questions/draft_questions.json` | Tracked baseline mod | `d05c24830ec56505...` | **MATCH** |
| `backend/data/uploads/registry.json` | Tracked baseline mod | `5a6b8111ef127d5b...` | **MATCH** |
| `backend/tests/test_dynamic_assessment.py` | Tracked baseline mod | `96be8ebbacf4d732...` | **MATCH** |
| `frontend/src/components/weekly/WeekSelector.tsx` | Tracked baseline mod | `ec0946d08a52c9fe...` | **MATCH** |
| `frontend/src/context/AppContext.tsx` | Tracked baseline mod | `99a163a1ee3b7043...` | **MATCH** |
| `frontend/src/pages/WeeklyProgressPage.tsx` | Tracked baseline mod | `d54025ac18aa0990...` | **MATCH** |

---

## 8. Summary of Verification Status

| Deliverable | Implementation Status | Evidence |
|---|---|---|
| Docker Credential Hygiene | Complete | `init_docker_postgres.sql`, `init_docker_postgres.sh`, `docker-compose.yml` |
| Admin Passwordless Fallback | Removed | `setup_postgres_db.py` raises on invalid password; `test_20` passes |
| Migration Role Separation | Enforced | `config.py` raises on missing migration credentials; `test_19` passes |
| Autonomous Audit Testing | Complete | `test_08` tests actual `get_audit_db()`; documents `sih_app_user` isolation |
| Rotated Credentials | Complete | URL-safe high-entropy credentials generated; uncommitted `.env` |
| Integration Tests | Complete | 20/20 tests pass in 1.46s |
| Backend Regression | Complete | 280/280 tests pass in 10.28s |
| Frontend Verification | Complete | `tsc --noEmit` (0 errors), `npm run build` (built in 9.67s) |
| Workspace Preservation | Verified | 26/26 baseline files match 100% via SHA-256; original repo untouched |
| Phase 2 Boundary | Respected | Zero Phase 2 APIs or workflows implemented |

**Phase 1.2 is complete and verified. Awaiting authorization before proceeding to Phase 2.**


---

## 11. Phase 1.3 Docker Execution Order Fix & Key Safety Verification

### A. Docker Double-Execution Resolution
In PostgreSQL official Docker images, all executable scripts and SQL files in `/docker-entrypoint-initdb.d/` are executed automatically. If both a wrapper shell script and the SQL script are mounted in `/docker-entrypoint-initdb.d/`, the SQL file executes twice (once explicitly via the shell wrapper and once directly by the entrypoint).
- **Fix:** `init_docker_postgres.sql` is mounted to `/tmp/sih26101_init.sql:ro` (outside `/docker-entrypoint-initdb.d/`).
- **Entrypoint:** Only `init_docker_postgres.sh` is mounted inside `/docker-entrypoint-initdb.d/01_init_roles.sh:ro`.
- **Dynamic Database Names:** `01_init_roles.sh` reads `DB_DEV_NAME` and `DB_TEST_NAME`, provisions both databases, and iterates over each database to execute `/tmp/sih26101_init.sql` exactly once per database.
- **Host Availability:** Docker Desktop / CLI is not installed on the current host. YAML syntax was validated via PyYAML and SQL schema operations were validated against native PostgreSQL 18.

### B. Encryption-Key Rotation Safety Evidence
- `employee_documents` record count in `sih26101_dev`: **0**.
- `employee_documents` record count in `sih26101_test`: **0**.
- Number of `.enc` files across the workspace: **0**.
- Non-empty application tables in the database: **0** (only `alembic_version` has 1 record for schema versioning).
- **Conclusion:** Zero existing records or uploaded files depend on previous encryption keys. Key rotation in Phase 1.2 was completely safe and caused zero data loss or orphan ciphertext.


---

## 12. Phase 1.4 SQL Credential Hardening & Encryption-Key Audit

### A. Secure SQL Variable Handling (`init_docker_postgres.sh`)
Direct shell variable interpolation into raw SQL heredocs was eliminated. The initialization script now uses secure `psql` command-line variable binding:
- **String Literals (Passwords):** Passed via `-v migrator_password=... -v app_password=...` and referenced as `:'migrator_password'` and `:'app_password'`. PostgreSQL's `psql` parser automatically sanitizes and escapes string literals, preventing syntax breakage and SQL injection even with passwords containing single quotes (`'`), double quotes (`"`), dollar signs (`$`), or ampersands (`&`).
- **SQL Identifiers (Database Names):** Passed via `-v dev_db=... -v test_db=...` and referenced as `:"dev_db"` and `:"test_db"`.
- **Quoted Heredoc Delimiter:** `<<'EOSQL'` instructs the shell to treat the body as literal text without bash parameter expansion.
- **Empirical Validation:** Tested against native PostgreSQL 18 with passwords containing special characters (single quotes, quotes, special symbols); role creation and database provisioning executed cleanly with exit code 0 and zero secret exposure in logs.

### B. Complete Encryption-Key Usage Audit
A comprehensive codebase audit was conducted across all files, database tables, and directories:
1. **Key References in Executable Code:**
   - `DOCUMENT_ENCRYPTION_KEK`: **Not used by any executable application code** in Phase 1. Only defined in `.env` / `.env.example` as a placeholder setting and described in architectural documentation (`FINAL_ARCHITECTURE_PLAN_v2.7.md`).
   - `VAULT_ENCRYPTION_KEY`: **Not used by any executable application code** in Phase 1. Only defined in `.env` / `.env.example` as a placeholder setting and described in architectural documentation.
2. **Cryptographic Functions & AES-GCM:**
   - No AES-GCM encryption or decryption routines are currently implemented in application code. Document envelope encryption is specified for Phase 2 implementation.
3. **Ciphertext Storage Locations:**
   - Table `employee_documents` columns (`encrypted_dek_b64`, `iv_nonce_b64`, `auth_tag_b64`): Currently has **0 records** across both `sih26101_dev` and `sih26101_test`.
   - Filesystem / Vault storage: **0 `.enc` files** exist across the workspace; no vault directories exist.
4. **Data Dependency on Old Keys:**
   - **Zero existing data depends on the old keys.** All application tables in the development database are empty (only `alembic_version` has 1 row for migration tracking).
5. **Rotation Safety:**
   - Key rotation in Phase 1.2 was safe and caused no data loss or orphaned ciphertext.

### C. Docker Testing Status
- Docker Engine / Docker Desktop is not installed on this host environment.
- As required by strict reporting guidelines, Docker startup has not been claimed as verified at runtime.
- Configuration validity has been verified via PyYAML schema parsing and direct PostgreSQL execution of all provisioning SQL statements.
