"""
PostgreSQL Database Foundation Security and Integrity Integration Test Suite for SIH26101.
Validates:
1. Least-privilege role separation (sih_migrator vs sih_app_user).
2. SCRAM-SHA-256 password authentication & rejection of unauthenticated/wrong-password access.
3. DDL restrictions: runtime user cannot create databases, create tables, or drop tables.
4. Audit log security: runtime user cannot UPDATE, DELETE, or TRUNCATE audit logs.
5. Autonomous audit logging: audit entries survive failed business transaction rollbacks.
6. Permitted operations: runtime user can perform standard CRUD on application entities.
7. Architectural constraints: composite FKs, geographic hierarchy, partial unique indexes,
   UNIQUE NULLS NOT DISTINCT, and nemo judex in causa sua appeal reviewer checks.
"""

import os
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import pytest
from sqlalchemy import text, select, create_engine
from sqlalchemy.exc import IntegrityError, DBAPIError, ProgrammingError, OperationalError
from sqlalchemy.orm import Session

from competency_engine.db import (
    Base,
    get_engine,
    get_session_factory,
    get_db,
    get_audit_db,
    check_db_health,
    db_settings,
    AccountTypeEnum,
    AccountStatusEnum,
    AppStatusEnum,
    ApprovalStatusEnum,
    GeographicLevelEnum,
    RoutingSourceEnum,
    RoutingStatusEnum,
    VerificationOutcomeEnum,
    RevocationAppealStatusEnum,
    User,
    OrgMinistry,
    OrgDepartment,
    OrgCadre,
    OrgGradeBand,
    OrgDesignation,
    OrgZone,
    OrgState,
    OrgLocation,
    EmployeeProfile,
    AdministratorProfile,
    AdministratorScope,
    ProjectStaffProfile,
    EmployeeApplication,
    ApplicationRoutingHistory,
    ApplicationFieldVerification,
    ApprovalRevocationAppeal,
    AdminEmployeeAssignment,
    EmployeeDocument,
    ApplicationAuditLog,
)

TEST_APP_URL = db_settings.TEST_DATABASE_URL
TEST_MIGRATOR_URL = db_settings.TEST_MIGRATION_DATABASE_URL


@pytest.fixture(scope="module")
def migrator_engine():
    """Privileged engine bound to sih_migrator (schema owner)."""
    eng = create_engine(TEST_MIGRATOR_URL, pool_pre_ping=True)
    with eng.connect() as conn:
        conn.execute(text("SELECT 1"))
    yield eng


@pytest.fixture(scope="module")
def app_engine():
    """Least-privilege runtime engine bound to sih_app_user."""
    eng = create_engine(TEST_APP_URL, pool_pre_ping=True)
    with eng.connect() as conn:
        conn.execute(text("SELECT 1"))
    yield eng


def cleanup_test_db(migrator_engine):
    """Clean all tables in dependency-safe order using schema owner credentials."""
    with migrator_engine.begin() as conn:
        conn.execute(text("""
            DELETE FROM application_field_verifications;
            DELETE FROM application_routing_history;
            DELETE FROM approval_revocation_appeals;
            DELETE FROM admin_employee_assignments;
            DELETE FROM employee_documents;
            ALTER TABLE application_audit_logs DISABLE TRIGGER trg_audit_immutability;
            ALTER TABLE application_audit_logs DISABLE TRIGGER trg_audit_truncate_immutability;
            DELETE FROM application_audit_logs;
            ALTER TABLE application_audit_logs ENABLE TRIGGER trg_audit_immutability;
            ALTER TABLE application_audit_logs ENABLE TRIGGER trg_audit_truncate_immutability;
            DELETE FROM employee_applications;
            DELETE FROM administrator_scopes;
            DELETE FROM employee_profiles;
            DELETE FROM project_staff_profiles;
            DELETE FROM administrator_profiles;
            DELETE FROM org_locations;
            DELETE FROM org_states;
            DELETE FROM org_zones;
            DELETE FROM org_designations;
            DELETE FROM org_grade_bands;
            DELETE FROM org_cadres;
            DELETE FROM org_departments;
            DELETE FROM org_ministries;
            DELETE FROM refresh_tokens;
            DELETE FROM email_verifications;
            DELETE FROM users;
        """))


@pytest.fixture(scope="function")
def db_session(app_engine, migrator_engine):
    """
    Function-scoped transactional session for runtime application user (sih_app_user).
    Cleanup is performed by the privileged migrator_engine to respect least-privilege.
    """
    cleanup_test_db(migrator_engine)
    session_factory = get_session_factory(app_engine)
    session: Session = session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        cleanup_test_db(migrator_engine)


def create_org_hierarchy(db_session, prefix="T"):
    """Helper to create a full valid organizational hierarchy in dependency order."""
    min_obj = OrgMinistry(id=f"MIN_{prefix}", name=f"Ministry {prefix}", code=f"M_{prefix}")
    db_session.add(min_obj)
    db_session.flush()

    dept = OrgDepartment(id=f"DEP_{prefix}", ministry_id=min_obj.id, name=f"Dept {prefix}", code=f"D_{prefix}")
    cadre = OrgCadre(id=f"CAD_{prefix}", name=f"Cadre {prefix}")
    grade = OrgGradeBand(id=f"GB_{prefix}", name=f"Grade {prefix}", hierarchical_rank=1)
    db_session.add_all([dept, cadre, grade])
    db_session.flush()

    desig = OrgDesignation(id=f"DES_{prefix}", name=f"Desig {prefix}", grade_band_id=grade.id, cadre_id=cadre.id)
    zone = OrgZone(id=f"Z_{prefix}", name=f"Zone {prefix}", code=f"Z_{prefix}")
    db_session.add_all([desig, zone])
    db_session.flush()

    state = OrgState(id=f"ST_{prefix}", zone_id=zone.id, name=f"State {prefix}", code=f"S_{prefix}")
    db_session.add(state)
    db_session.flush()

    loc = OrgLocation(id=f"LOC_{prefix}", state_id=state.id, zone_id=zone.id, city=f"City {prefix}", building_name="HQ")
    db_session.add(loc)
    db_session.flush()

    return min_obj, dept, cadre, grade, desig, zone, state, loc


# ===========================================================================
# 1. Connection, Authentication & Database Isolation
# ===========================================================================

def test_01_database_connection_and_health(app_engine, migrator_engine):
    """Verify PostgreSQL connection pooling and health check probe for both roles."""
    assert check_db_health(app_engine) is True
    assert check_db_health(migrator_engine) is True


def test_02_database_isolation():
    """Verify that development and test database URLs target distinct databases."""
    dev_url = db_settings.DATABASE_URL
    test_url = db_settings.TEST_DATABASE_URL
    assert dev_url != test_url, "Development and test database URLs must be completely separate!"
    assert "test" in test_url.lower(), "Test database URL must contain 'test' for safety."


def test_03_authentication_fails_without_valid_credentials():
    """Verify SCRAM-SHA-256 rejects unauthenticated or invalid password connections."""
    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = os.getenv("POSTGRES_PORT", "54329")
    db = os.getenv("DB_TEST_NAME", "sih26101_test")

    # 1. Connection without password -> Rejected
    unauth_url = f"postgresql+psycopg://sih_app_user@{host}:{port}/{db}"
    eng_unauth = create_engine(unauth_url)
    with pytest.raises(OperationalError):
        with eng_unauth.connect() as conn:
            conn.execute(text("SELECT 1"))

    # 2. Connection with wrong password -> Rejected
    wrong_pw_url = f"postgresql+psycopg://sih_app_user:WRONG_PASSWORD_XYZ@{host}:{port}/{db}"
    eng_wrong = create_engine(wrong_pw_url)
    with pytest.raises(OperationalError):
        with eng_wrong.connect() as conn:
            conn.execute(text("SELECT 1"))


# ===========================================================================
# 2. Least-Privilege Role Hardening & DDL Restrictions
# ===========================================================================

def test_04_runtime_user_cannot_create_database(app_engine):
    """Verify that runtime role (sih_app_user) does NOT have CREATEDB privilege."""
    with pytest.raises(DBAPIError) as exc_info:
        with app_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.execute(text("CREATE DATABASE test_forbidden_db"))
    assert "permission denied to create database" in str(exc_info.value).lower()


def test_05_runtime_user_cannot_create_or_drop_schema_objects(app_engine):
    """
    Verify runtime role (sih_app_user) cannot create or drop tables in schema public.
    CREATE privilege on schema public must be strictly revoked from sih_app_user.
    """
    # 1. Attempt CREATE TABLE -> rejected
    with pytest.raises(DBAPIError) as exc_info:
        with app_engine.begin() as conn:
            conn.execute(text("CREATE TABLE forbidden_test_table (id INT PRIMARY KEY)"))
    assert "permission denied for schema public" in str(exc_info.value).lower()

    # 2. Attempt DROP TABLE on an existing table -> rejected
    with pytest.raises(DBAPIError) as exc_info:
        with app_engine.begin() as conn:
            conn.execute(text("DROP TABLE users CASCADE"))
    assert "must be owner of table" in str(exc_info.value).lower() or "permission denied" in str(exc_info.value).lower()


def test_06_runtime_user_audit_log_update_delete_truncate_rejection(db_session, app_engine, migrator_engine):
    """
    Verify audit log security:
    sih_app_user is prohibited from UPDATE, DELETE, and TRUNCATE via:
    1. Table-level privilege revocation (REVOKE UPDATE, DELETE, TRUNCATE).
    2. Row-level trigger trg_audit_immutability.
    3. Statement-level trigger trg_audit_truncate_immutability.
    """
    # Insert audit entry
    user = User(email="audit_actor_sec@example.com", hashed_password="pw", account_type=AccountTypeEnum.PROJECT_STAFF)
    db_session.add(user)
    db_session.commit()

    audit_entry = ApplicationAuditLog(
        actor_id=user.id,
        actor_email=user.email,
        actor_role="PROJECT_STAFF",
        action="SEC_TEST",
        previous_state=None,
        new_state={"status": "SECURED"},
        notes="Security test entry",
    )
    db_session.add(audit_entry)
    db_session.commit()
    entry_id = audit_entry.id

    # 1. Attempt UPDATE as runtime user -> rejected
    with pytest.raises(DBAPIError) as exc_info:
        with app_engine.begin() as conn:
            conn.execute(text("UPDATE application_audit_logs SET notes = 'TAMPERED' WHERE id = :id"), {"id": entry_id})
    err_msg = str(exc_info.value).lower()
    assert "permission denied" in err_msg or "compliance violation" in err_msg

    # 2. Attempt DELETE as runtime user -> rejected
    with pytest.raises(DBAPIError) as exc_info:
        with app_engine.begin() as conn:
            conn.execute(text("DELETE FROM application_audit_logs WHERE id = :id"), {"id": entry_id})
    err_msg = str(exc_info.value).lower()
    assert "permission denied" in err_msg or "compliance violation" in err_msg

    # 3. Attempt TRUNCATE as runtime user -> rejected by both grant and statement trigger
    with pytest.raises(DBAPIError) as exc_info:
        with app_engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE application_audit_logs"))
    err_msg = str(exc_info.value).lower()
    assert "permission denied" in err_msg or "compliance violation" in err_msg


def test_07_runtime_user_can_perform_ordinary_application_operations(db_session):
    """Verify runtime user has full read/write privileges on normal application tables."""
    min_obj, dept, cadre, grade, desig, zone, state, loc = create_org_hierarchy(db_session, "CRUD")

    user = User(
        email="ordinary_user@example.com",
        hashed_password="pw_ordinary",
        account_type=AccountTypeEnum.EMPLOYEE,
        account_status=AccountStatusEnum.ACTIVE,
    )
    db_session.add(user)
    db_session.commit()

    # Read
    fetched = db_session.execute(select(User).where(User.email == "ordinary_user@example.com")).scalar_one()
    assert fetched.id is not None

    # Update
    fetched.failed_login_attempts = 2
    db_session.commit()

    refreshed = db_session.get(User, fetched.id)
    assert refreshed.failed_login_attempts == 2

    # Delete
    db_session.delete(refreshed)
    db_session.commit()

    deleted = db_session.execute(select(User).where(User.email == "ordinary_user@example.com")).scalar_one_or_none()
    assert deleted is None


def test_08_audit_log_survives_failed_business_transaction(app_engine, migrator_engine):
    """
    Verify autonomous audit logging using the actual get_audit_db() implementation:
    An audit log entry written via get_audit_db() persists even if the enclosing business
    transaction fails and rolls back.

    Role & Trust Boundary Verification:
    - The audit session uses the runtime application role (sih_app_user).
    - Under the least-privilege model, sih_app_user has SELECT and INSERT privileges on
      application_audit_logs; UPDATE, DELETE, and TRUNCATE are revoked.
    - get_audit_db() provides TRANSACTION-LEVEL isolation (an autonomous transaction boundary
      via an independent connection from the pool). It does NOT use a separate database user.
    """
    cleanup_test_db(migrator_engine)
    test_db_url = db_settings.TEST_DATABASE_URL

    # 1. Enclosing business transaction that ultimately fails
    try:
        # Business transaction executed via actual get_db()
        business_gen = get_db(test_db_url)
        business_session = next(business_gen)

        # Add business user
        u = User(
            email="failing_business_user@example.com",
            hashed_password="pw_test",
            account_type=AccountTypeEnum.EMPLOYEE,
        )
        business_session.add(u)
        business_session.flush()

        # 2. Autonomous audit log written via the actual get_audit_db() function
        audit_gen = get_audit_db(test_db_url)
        audit_session = next(audit_gen)
        audit_entry = ApplicationAuditLog(
            actor_id=None,
            actor_email="system@example.com",
            actor_role="SYSTEM",
            action="ATTEMPT_REGISTRATION",
            previous_state=None,
            new_state={"email": "failing_business_user@example.com"},
            notes="Audit logged via actual get_audit_db prior to business failure",
        )
        audit_session.add(audit_entry)

        # Complete audit transaction - triggers session.commit() inside get_audit_db()
        try:
            next(audit_gen)
        except StopIteration:
            pass  # Expected generator completion and commit

        # 3. Simulate failure in the enclosing business transaction
        raise ValueError("Simulated business validation error triggering rollback")
    except ValueError as err:
        # Trigger business transaction rollback via get_db() generator exception handling
        try:
            business_gen.throw(err)
        except StopIteration:
            pass
        except ValueError:
            pass  # Propagated after rollback

    # 4. Verify business entity was completely rolled back
    with app_engine.connect() as conn:
        user_res = conn.execute(
            select(User).where(User.email == "failing_business_user@example.com")
        ).scalar_one_or_none()
        assert user_res is None, "Business entity must not exist (must be rolled back)."

        # 5. Verify audit log entry written via actual get_audit_db survived!
        audit_note = conn.execute(
            select(ApplicationAuditLog.notes).where(
                ApplicationAuditLog.notes == "Audit logged via actual get_audit_db prior to business failure"
            )
        ).scalar_one_or_none()
        assert audit_note is not None, "Autonomous audit log must persist despite business rollback!"
        assert audit_note == "Audit logged via actual get_audit_db prior to business failure"


def test_09_migration_role_can_manage_schema(migrator_engine):
    """Verify that sih_migrator has schema ownership and can execute DDL."""
    with migrator_engine.begin() as conn:
        conn.execute(text("CREATE TABLE public.migrator_test_table (id INT PRIMARY KEY);"))
        conn.execute(text("DROP TABLE public.migrator_test_table;"))


# ===========================================================================
# 3. Core Architectural & Integrity Constraints
# ===========================================================================

def test_10_foreign_key_restricts(db_session):
    """Verify foreign key enforcement when inserting non-existent relationships."""
    dept = OrgDepartment(
        id="DEPT_INVALID",
        ministry_id="NON_EXISTENT_MINISTRY",
        name="Invalid Dept",
        code="INV",
    )
    db_session.add(dept)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_11_geographic_level_integrity_valid_scopes(db_session):
    """Verify check constraint chk_geographic_level_integrity for valid scopes."""
    min_obj, dept, cadre, grade, desig, zone, state, loc = create_org_hierarchy(db_session, "G1")
    user = User(email="admin_scope_g1@example.com", hashed_password="pw", account_type=AccountTypeEnum.ADMINISTRATOR)
    db_session.add(user)
    db_session.flush()

    admin = AdministratorProfile(user_id=user.id, full_name="Scope Admin", official_designation="Director")
    db_session.add(admin)
    db_session.commit()

    # Valid scopes across all 4 tiers
    s_national = AdministratorScope(admin_id=admin.id, ministry_id=min_obj.id, geographic_level=GeographicLevelEnum.NATIONAL)
    s_zone = AdministratorScope(admin_id=admin.id, ministry_id=min_obj.id, geographic_level=GeographicLevelEnum.ZONE, zone_id=zone.id)
    s_state = AdministratorScope(admin_id=admin.id, ministry_id=min_obj.id, geographic_level=GeographicLevelEnum.STATE, zone_id=zone.id, state_id=state.id)
    s_station = AdministratorScope(admin_id=admin.id, ministry_id=min_obj.id, geographic_level=GeographicLevelEnum.STATION, zone_id=zone.id, state_id=state.id, location_id=loc.id)

    db_session.add_all([s_national, s_zone, s_state, s_station])
    db_session.flush()
    assert s_national.id is not None
    assert s_zone.id is not None
    assert s_state.id is not None
    assert s_station.id is not None


def test_12_geographic_level_integrity_invalid_scope_rejected(db_session):
    """Verify invalid geographic level scope definitions violate check constraint."""
    min_obj, dept, cadre, grade, desig, zone, state, loc = create_org_hierarchy(db_session, "G2")
    user = User(email="admin_scope_g2@example.com", hashed_password="pw", account_type=AccountTypeEnum.ADMINISTRATOR)
    db_session.add(user)
    db_session.flush()

    admin = AdministratorProfile(user_id=user.id, full_name="Scope Admin 2", official_designation="Director")
    db_session.add(admin)
    db_session.commit()

    invalid_national = AdministratorScope(
        admin_id=admin.id,
        ministry_id=min_obj.id,
        geographic_level=GeographicLevelEnum.NATIONAL,
        zone_id=zone.id,  # Violates chk_geographic_level_integrity
    )
    db_session.add(invalid_national)
    with pytest.raises(IntegrityError) as exc_info:
        db_session.flush()
    assert "chk_geographic_level_integrity" in str(exc_info.value)
    db_session.rollback()


def test_13_composite_application_employee_reference(db_session):
    """Verify application_field_verifications enforces composite reference (application_id, employee_id)."""
    min_obj, dept, cadre, grade, desig, zone, state, loc = create_org_hierarchy(db_session, "C1")
    u1 = User(email="comp_emp1@example.com", hashed_password="pw", account_type=AccountTypeEnum.EMPLOYEE)
    u2 = User(email="comp_emp2@example.com", hashed_password="pw", account_type=AccountTypeEnum.EMPLOYEE)
    u_admin = User(email="comp_adm1@example.com", hashed_password="pw", account_type=AccountTypeEnum.ADMINISTRATOR)
    db_session.add_all([u1, u2, u_admin])
    db_session.flush()

    e1 = EmployeeProfile(
        user_id=u1.id, employee_code="EMP_C1", full_name="Emp One", ministry_id=min_obj.id,
        department_id=dept.id, cadre_id=cadre.id, location_id=loc.id, designation_id=desig.id, experience_years=Decimal("5.0")
    )
    e2 = EmployeeProfile(
        user_id=u2.id, employee_code="EMP_C2", full_name="Emp Two", ministry_id=min_obj.id,
        department_id=dept.id, cadre_id=cadre.id, location_id=loc.id, designation_id=desig.id, experience_years=Decimal("3.0")
    )
    admin = AdministratorProfile(user_id=u_admin.id, full_name="Reviewing Admin", official_designation="Director")
    db_session.add_all([e1, e2, admin])
    db_session.commit()

    app1 = EmployeeApplication(employee_id=e1.id, submission_number=1, status=AppStatusEnum.SUBMITTED)
    db_session.add(app1)
    db_session.commit()

    mismatched_verif = ApplicationFieldVerification(
        application_id=app1.id,
        employee_id=e2.id,  # Mismatch: belongs to e1, not e2
        field_name="department_id",
        attempt_number=1,
        is_latest=True,
        employee_submitted_value={"value": dept.id},
        admin_verified_value={"value": dept.id},
        verification_outcome=VerificationOutcomeEnum.VERIFIED_MATCH,
        reviewing_admin_id=admin.id,
    )
    db_session.add(mismatched_verif)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_14_partial_unique_index_single_pending_application(db_session):
    """Verify partial unique index uq_single_pending_application_per_employee."""
    min_obj, dept, cadre, grade, desig, zone, state, loc = create_org_hierarchy(db_session, "P1")
    user = User(email="pending_app_p1@example.com", hashed_password="pw", account_type=AccountTypeEnum.EMPLOYEE)
    db_session.add(user)
    db_session.flush()

    emp = EmployeeProfile(
        user_id=user.id, employee_code="EMP_P1", full_name="Pending Tester", ministry_id=min_obj.id,
        department_id=dept.id, cadre_id=cadre.id, location_id=loc.id, designation_id=desig.id, experience_years=Decimal("2.0")
    )
    db_session.add(emp)
    db_session.commit()

    app1 = EmployeeApplication(employee_id=emp.id, submission_number=1, status=AppStatusEnum.SUBMITTED)
    db_session.add(app1)
    db_session.commit()

    app2 = EmployeeApplication(employee_id=emp.id, submission_number=2, status=AppStatusEnum.SUBMITTED)
    db_session.add(app2)
    with pytest.raises(IntegrityError) as exc_info:
        db_session.flush()
    assert "uq_single_pending_application_per_employee" in str(exc_info.value)
    db_session.rollback()

    app1 = db_session.get(EmployeeApplication, app1.id)
    app1.status = AppStatusEnum.ACCEPTED
    db_session.commit()

    app2 = EmployeeApplication(employee_id=emp.id, submission_number=2, status=AppStatusEnum.SUBMITTED)
    db_session.add(app2)
    db_session.commit()
    assert app2.id is not None


def test_15_unique_nulls_not_distinct_on_scopes(db_session):
    """Verify PostgreSQL 15+ UNIQUE NULLS NOT DISTINCT constraint on administrator_scopes."""
    min_obj = OrgMinistry(id="MIN_UNQ", name="Ministry Unq", code="MU")
    user = User(email="nulls_distinct_u@example.com", hashed_password="pw", account_type=AccountTypeEnum.ADMINISTRATOR)
    db_session.add_all([min_obj, user])
    db_session.flush()

    admin = AdministratorProfile(user_id=user.id, full_name="Nulls Admin", official_designation="Director")
    db_session.add(admin)
    db_session.commit()

    s1 = AdministratorScope(admin_id=admin.id, ministry_id=min_obj.id, geographic_level=GeographicLevelEnum.NATIONAL)
    db_session.add(s1)
    db_session.commit()

    s2 = AdministratorScope(admin_id=admin.id, ministry_id=min_obj.id, geographic_level=GeographicLevelEnum.NATIONAL)
    db_session.add(s2)
    with pytest.raises(IntegrityError) as exc_info:
        db_session.flush()
    assert "uq_admin_scope_unique" in str(exc_info.value)
    db_session.rollback()


def test_16_independent_appeal_reviewer_check_constraint(db_session):
    """Verify nemo judex in causa sua constraint chk_appeal_independent_reviewer."""
    min_obj, dept, cadre, grade, desig, zone, state, loc = create_org_hierarchy(db_session, "A1")
    u_emp = User(email="appeal_emp_a1@example.com", hashed_password="pw", account_type=AccountTypeEnum.EMPLOYEE)
    u_staff = User(email="revoking_staff_a1@example.com", hashed_password="pw", account_type=AccountTypeEnum.PROJECT_STAFF)
    db_session.add_all([u_emp, u_staff])
    db_session.flush()

    emp = EmployeeProfile(
        user_id=u_emp.id, employee_code="EMP_A1", full_name="Appealing Employee", ministry_id=min_obj.id,
        department_id=dept.id, cadre_id=cadre.id, location_id=loc.id, designation_id=desig.id, experience_years=Decimal("4.0")
    )
    db_session.add(emp)
    db_session.commit()

    invalid_appeal = ApprovalRevocationAppeal(
        employee_id=emp.id,
        revoked_by_staff_id=u_staff.id,
        appeal_reason="Revocation was unjustified.",
        status=RevocationAppealStatusEnum.APPEAL_ALLOWED_REINSTATED,
        reviewed_by_staff_id=u_staff.id,  # Same as revoked_by_staff_id!
        decision_reason="Self-reinstatement forbidden.",
    )
    db_session.add(invalid_appeal)
    with pytest.raises(IntegrityError) as exc_info:
        db_session.flush()
    assert "chk_appeal_independent_reviewer" in str(exc_info.value)
    db_session.rollback()


def test_17_single_active_assignment_per_employee(db_session):
    """Verify partial unique index uq_single_active_assignment_per_employee."""
    min_obj, dept, cadre, grade, desig, zone, state, loc = create_org_hierarchy(db_session, "AS1")
    u_emp = User(email="asg_emp@example.com", hashed_password="pw", account_type=AccountTypeEnum.EMPLOYEE)
    u_adm1 = User(email="asg_adm1@example.com", hashed_password="pw", account_type=AccountTypeEnum.ADMINISTRATOR)
    u_adm2 = User(email="asg_adm2@example.com", hashed_password="pw", account_type=AccountTypeEnum.ADMINISTRATOR)
    db_session.add_all([u_emp, u_adm1, u_adm2])
    db_session.flush()

    emp = EmployeeProfile(
        user_id=u_emp.id, employee_code="EMP_AS1", full_name="Assigned Employee", ministry_id=min_obj.id,
        department_id=dept.id, cadre_id=cadre.id, location_id=loc.id, designation_id=desig.id, experience_years=Decimal("1.5")
    )
    adm1 = AdministratorProfile(user_id=u_adm1.id, full_name="Admin One", official_designation="Director")
    adm2 = AdministratorProfile(user_id=u_adm2.id, full_name="Admin Two", official_designation="Joint Director")
    db_session.add_all([emp, adm1, adm2])
    db_session.commit()

    asg1 = AdminEmployeeAssignment(admin_id=adm1.id, employee_id=emp.id, is_active=True)
    db_session.add(asg1)
    db_session.commit()

    asg2 = AdminEmployeeAssignment(admin_id=adm2.id, employee_id=emp.id, is_active=True)
    db_session.add(asg2)
    with pytest.raises(IntegrityError) as exc_info:
        db_session.flush()
    assert "uq_single_active_assignment_per_employee" in str(exc_info.value)
    db_session.rollback()

    asg1 = db_session.get(AdminEmployeeAssignment, asg1.id)
    asg1.is_active = False
    db_session.commit()

    asg2 = AdminEmployeeAssignment(admin_id=adm2.id, employee_id=emp.id, is_active=True)
    db_session.add(asg2)
    db_session.commit()
    assert asg2.id is not None


def test_18_document_crypto_shredding_metadata(db_session):
    """Verify envelope encryption metadata and cryptographic erasure lifecycle."""
    min_obj, dept, cadre, grade, desig, zone, state, loc = create_org_hierarchy(db_session, "D1")
    user = User(email="doc_emp_d1@example.com", hashed_password="pw", account_type=AccountTypeEnum.EMPLOYEE)
    db_session.add(user)
    db_session.flush()

    emp = EmployeeProfile(
        user_id=user.id, employee_code="EMP_D1", full_name="Document Holder", ministry_id=min_obj.id,
        department_id=dept.id, cadre_id=cadre.id, location_id=loc.id, designation_id=desig.id, experience_years=Decimal("1.0")
    )
    db_session.add(emp)
    db_session.commit()

    expires = datetime.now(timezone.utc) + timedelta(days=365)
    doc = EmployeeDocument(
        employee_id=emp.id,
        original_filename="joining_order.pdf",
        mime_type="application/pdf",
        file_size_bytes=1048576,
        vault_storage_path="/vault/emp_001/doc_001.enc",
        kek_version="v1",
        encrypted_dek_b64="ENCRYPTED_DEK_SAMPLE_BASE64_STRING==",
        iv_nonce_b64="NONCE_SAMPLE_BASE64==",
        auth_tag_b64="AUTH_TAG_BASE64==",
        retention_expires_at=expires,
    )
    db_session.add(doc)
    db_session.commit()
    assert doc.encrypted_dek_b64 is not None

    # Cryptographic erasure
    doc = db_session.get(EmployeeDocument, doc.id)
    doc.encrypted_dek_b64 = None
    doc.deleted_at = datetime.now(timezone.utc)
    db_session.commit()

    refreshed_doc = db_session.get(EmployeeDocument, doc.id)
    assert refreshed_doc.encrypted_dek_b64 is None
    assert refreshed_doc.deleted_at is not None
    assert refreshed_doc.original_filename == "joining_order.pdf"


def test_19_migration_urls_require_migration_credentials_and_never_fallback():
    """
    Phase 1.2 Security Requirement:
    Verify that MIGRATION_DATABASE_URL and TEST_MIGRATION_DATABASE_URL require explicit
    migration credentials and raise a ValueError rather than falling back to application runtime URLs.
    """
    from competency_engine.db.config import DatabaseSettings

    settings = DatabaseSettings()
    old_pw = os.environ.get("DB_MIGRATOR_PASSWORD")
    old_url = os.environ.get("MIGRATION_DATABASE_URL")
    old_test_url = os.environ.get("TEST_MIGRATION_DATABASE_URL")

    try:
        # 1. Test MIGRATION_DATABASE_URL with missing credentials
        if "DB_MIGRATOR_PASSWORD" in os.environ:
            del os.environ["DB_MIGRATOR_PASSWORD"]
        if "MIGRATION_DATABASE_URL" in os.environ:
            del os.environ["MIGRATION_DATABASE_URL"]

        with pytest.raises(ValueError) as exc_info:
            _ = settings.MIGRATION_DATABASE_URL
        assert "MIGRATION_DATABASE_URL or DB_MIGRATOR_PASSWORD is not configured" in str(exc_info.value)
        assert "cannot fall back" in str(exc_info.value)

        # 2. Test TEST_MIGRATION_DATABASE_URL with missing credentials
        if "TEST_MIGRATION_DATABASE_URL" in os.environ:
            del os.environ["TEST_MIGRATION_DATABASE_URL"]

        with pytest.raises(ValueError) as exc_info:
            _ = settings.TEST_MIGRATION_DATABASE_URL
        assert "TEST_MIGRATION_DATABASE_URL or DB_MIGRATOR_PASSWORD is not configured" in str(exc_info.value)
        assert "cannot fall back" in str(exc_info.value)
    finally:
        # Restore environment variables
        if old_pw:
            os.environ["DB_MIGRATOR_PASSWORD"] = old_pw
        if old_url:
            os.environ["MIGRATION_DATABASE_URL"] = old_url
        if old_test_url:
            os.environ["TEST_MIGRATION_DATABASE_URL"] = old_test_url


def test_20_admin_connect_requires_valid_credentials_without_passwordless_fallback():
    """
    Phase 1.2 Security Requirement:
    Verify that setup_postgres_db.py requires valid administrator credentials and stops
    rather than attempting any passwordless or trust fallback.
    """
    import scripts.setup_postgres_db as setup_mod

    # Attempting to connect with an invalid password must raise an error and fail
    orig_pw = setup_mod.POSTGRES_ADMIN_PASSWORD
    setup_mod.POSTGRES_ADMIN_PASSWORD = "WRONG_ADMIN_PASSWORD_999!"

    try:
        with pytest.raises((Exception, BaseException)):
            setup_mod.connect_admin()
    finally:
        setup_mod.POSTGRES_ADMIN_PASSWORD = orig_pw
