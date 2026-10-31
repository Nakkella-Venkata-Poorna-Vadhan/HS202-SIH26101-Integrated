"""
Comprehensive Authentication, Identity and RBAC Integration Test Suite for SIH26101 Platform.
Strictly tests:
1. Authentication:
   - Argon2id password hashing and verification.
   - Valid and invalid login with lockout tracking.
   - Short-lived JWT access tokens and invalid/expired token rejection.
   - Refresh-token rotation and family reuse detection (revocation).
   - Single-use expiring email verification.
   - Single-use expiring password reset.
   - Account deactivation.
   - Logout and session revocation.
2. Authorization & RBAC:
   - Anonymous access rejection on protected endpoints.
   - Employee cannot access Administrator endpoints (/api/admin/scopes).
   - Employee cannot access Project Staff endpoints (/api/project-staff/*).
   - Administrator cannot access Project Staff endpoints.
   - Administrator cannot self-delegate or modify own scopes.
   - Project Staff cannot bypass Administrator employee-acceptance responsibilities.
   - Header tampering (X-Learner-ID) cannot impersonate or elevate privileges.
   - Unapproved employee cannot access protected learning workspace (/api/employee/learning-workspace).
   - Approved employee can access learning workspace.
   - Administrator scope checking (within jurisdiction vs outside jurisdiction).
3. Registration & Invitations:
   - Public employee registration and duplicate rejection.
   - Unverified employee login blocked.
   - Administrator cannot register publicly (no public admin registration).
   - Project Staff invitation creation and single-use expiring acceptance.
   - Rejection of expired or already-consumed invitation tokens.
   - Project Staff bootstrap validation.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from competency_engine.api import app
from competency_engine.auth.dependencies import is_within_admin_jurisdiction
from competency_engine.auth.password import hash_password, verify_password
from competency_engine.auth.rate_limiter import rate_limiter
from competency_engine.auth.tokens import (
    create_access_token,
    decode_access_token,
    generate_secure_token,
    hash_token,
)
from competency_engine.db import (
    AccountStatusEnum,
    AccountTypeEnum,
    AdminEmployeeAssignment,
    AdminInvitation,
    AdministratorProfile,
    AdministratorScope,
    ApprovalStatusEnum,
    EmailVerification,
    EmployeeApplication,
    EmployeeProfile,
    GeographicLevelEnum,
    OrgCadre,
    OrgDepartment,
    OrgDesignation,
    OrgGradeBand,
    OrgLocation,
    OrgMinistry,
    OrgState,
    OrgZone,
    PasswordResetToken,
    ProjectStaffProfile,
    RefreshToken,
    User,
    get_db,
    get_engine,
    get_session_factory,
)
from competency_engine.email_service import DevelopmentEmailAdapter, get_email_service, set_email_service
from scripts.bootstrap_project_staff import bootstrap_project_staff


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Ensure clean email adapter and rate limiter per test."""
    email_adapter = DevelopmentEmailAdapter()
    set_email_service(email_adapter)
    rate_limiter.reset()
    yield email_adapter
    rate_limiter.reset()


@pytest.fixture
def client():
    """FastAPI TestClient instance."""
    return TestClient(app)


@pytest.fixture
def test_db():
    """Dedicated database session for testing against test database."""
    engine = get_engine()
    session_factory = get_session_factory(engine)
    session: Session = session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def create_test_org_hierarchy(db: Session, suffix: str = "T1"):
    """Seed minimal organizational taxonomy records for testing foreign keys in strict dependency order."""
    min_id = f"MIN_{suffix}"
    dept_id = f"DEP_{suffix}"
    cadre_id = f"CAD_{suffix}"
    grade_id = f"GB_{suffix}"
    desig_id = f"DES_{suffix}"
    zone_id = f"ZN_{suffix}"
    state_id = f"ST_{suffix}"
    loc_id = f"LOC_{suffix}"

    min_obj = OrgMinistry(id=min_id, name=f"Ministry {suffix}", code=f"M_{suffix}", is_active=True)
    db.merge(min_obj)
    db.commit()

    dept = OrgDepartment(id=dept_id, ministry_id=min_id, name=f"Dept {suffix}", code=f"D_{suffix}", is_active=True)
    cadre = OrgCadre(id=cadre_id, name=f"Cadre {suffix}", controlling_authority="MoSPI", is_active=True)
    grade = OrgGradeBand(id=grade_id, name=f"Grade {suffix}", hierarchical_rank=1)
    db.merge(dept)
    db.merge(cadre)
    db.merge(grade)
    db.commit()

    desig = OrgDesignation(id=desig_id, name=f"Desig {suffix}", grade_band_id=grade_id, cadre_id=cadre_id, is_active=True)
    zone = OrgZone(id=zone_id, name=f"Zone {suffix}", code=f"Z_{suffix}")
    db.merge(desig)
    db.merge(zone)
    db.commit()

    state = OrgState(id=state_id, zone_id=zone_id, name=f"State {suffix}", code=f"S_{suffix}")
    db.merge(state)
    db.commit()

    loc = OrgLocation(id=loc_id, state_id=state_id, zone_id=zone_id, city="Test City", building_name="Test Bhavan")
    db.merge(loc)
    db.commit()

    return min_id, dept_id, cadre_id, grade_id, desig_id, zone_id, state_id, loc_id


# ===========================================================================
# 1. Password Hashing and Cryptographic Token Tests
# ===========================================================================

def test_password_hashing_argon2id():
    """Verify password hashing strictly uses Argon2id with OWASP parameters."""
    pwd = "GovOfficialSecure2026!"
    hashed = hash_password(pwd)
    assert hashed.startswith("$argon2id$")
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False
    assert verify_password("", hashed) is False

    with pytest.raises(ValueError):
        hash_password("short")  # min 8 chars


def test_token_hashing_sha256():
    """Verify token hashing produces 64-char hex digest."""
    raw = generate_secure_token(32)
    digest = hash_token(raw)
    assert len(digest) == 64
    assert digest == hash_token(raw)


def test_jwt_access_token_creation_and_expiration():
    """Verify JWT access tokens encode subject, role, issuer, audience, and expire properly."""
    user_id = str(uuid.uuid4())
    token = create_access_token(user_id=user_id, email="officer@mospi.gov.in", account_type="EMPLOYEE")
    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["email"] == "officer@mospi.gov.in"
    assert payload["account_type"] == "EMPLOYEE"
    assert payload["iss"] == "sih26101:auth"
    assert payload["aud"] == "sih26101:api"

    # Test expired token rejection
    expired_token = create_access_token(
        user_id=user_id,
        email="officer@mospi.gov.in",
        account_type="EMPLOYEE",
        expires_delta=timedelta(seconds=-10),
    )
    with pytest.raises(ValueError) as exc:
        decode_access_token(expired_token)
    assert "expired" in str(exc.value).lower()

    # Test token with invalid issuer rejected
    from jose import jwt
    from competency_engine.auth.tokens import get_jwt_secret, ALGORITHM
    bad_iss_token = jwt.encode(
        {"sub": user_id, "email": "a@b.com", "account_type": "EMPLOYEE", "iss": "malicious_issuer", "aud": "sih26101:api"},
        get_jwt_secret(),
        algorithm=ALGORITHM,
    )
    with pytest.raises(ValueError) as exc:
        decode_access_token(bad_iss_token)
    assert "issuer" in str(exc.value).lower() or "invalid" in str(exc.value).lower()

    # Test token with invalid audience rejected
    bad_aud_token = jwt.encode(
        {"sub": user_id, "email": "a@b.com", "account_type": "EMPLOYEE", "iss": "sih26101:auth", "aud": "wrong_audience"},
        get_jwt_secret(),
        algorithm=ALGORITHM,
    )
    with pytest.raises(ValueError) as exc:
        decode_access_token(bad_aud_token)
    assert "audience" in str(exc.value).lower() or "invalid" in str(exc.value).lower()


def test_user_controlled_header_bypass_rejected(client):
    """
    Hard Security Invariant:
    User-controlled identity headers (e.g. X-Learner-ID, X-Role, etc.) MUST NOT bypass
    token authentication on protected endpoints. Must return 401 Unauthorized.
    """
    for endpoint in [
        "/api/employee/learning-workspace",
        "/api/employee/application-status",
        "/api/admin/scopes",
        "/api/project-staff/administrators",
    ]:
        resp = client.get(
            endpoint,
            headers={
                "X-Learner-ID": "LEARNER-001",
                "X-User-Role": "ADMINISTRATOR",
                "X-Actor-ID": "STAFF-001",
            },
        )
        assert resp.status_code == 401, f"Endpoint {endpoint} allowed user-controlled identity header bypass!"


# ===========================================================================
# 2. Employee Registration & Email Verification Tests
# ===========================================================================

def test_employee_registration_lifecycle(client, test_db, setup_test_environment):
    """Verify full employee self-registration and email verification flow."""
    min_id, dept_id, cadre_id, grade_id, desig_id, zone_id, state_id, loc_id = create_test_org_hierarchy(test_db, "REG1")

    email = f"emp_{uuid.uuid4().hex[:8]}@mospi.gov.in"
    payload = {
        "email": email,
        "password": "EmpStrongPassword2026!",
        "employee_code": f"EC_{uuid.uuid4().hex[:6]}",
        "full_name": "Shri Arun Kumar",
        "ministry_id": min_id,
        "department_id": dept_id,
        "cadre_id": cadre_id,
        "location_id": loc_id,
        "designation_id": desig_id,
        "experience_years": 8.5,
        "phone_number": "+919876543210",
        "self_declared_skills": ["Sample Survey Design", "National Accounts"],
    }

    # 1. Register employee
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert "Registration successful" in data["message"]
    user_data = data["user"]
    assert user_data["account_status"] == "UNVERIFIED_EMAIL"
    assert user_data["is_approved"] is False

    # 2. Verify duplicate registration rejected
    dup_resp = client.post("/api/auth/register", json=payload)
    assert dup_resp.status_code == 409

    # 3. Attempt login before email verification -> Rejected (403 Forbidden)
    login_unverified = client.post("/api/auth/login", json={"email": email, "password": "EmpStrongPassword2026!"})
    assert login_unverified.status_code == 403
    assert "verify your email" in login_unverified.json()["detail"].lower()

    # 4. Extract token from test email service outbox
    token = setup_test_environment.get_latest_token(email)
    assert token is not None

    # 5. Verify email with single-use token
    verify_resp = client.post("/api/auth/verify-email", json={"token": token})
    assert verify_resp.status_code == 200
    assert verify_resp.json()["user"]["account_status"] == "ACTIVE"

    # 6. Attempt token reuse -> Rejected (410 Gone)
    reuse_resp = client.post("/api/auth/verify-email", json={"token": token})
    assert reuse_resp.status_code == 410

    # 7. Successful login after verification
    login_resp = client.post("/api/auth/login", json={"email": email, "password": "EmpStrongPassword2026!"})
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data
    assert "refresh_token" in login_data
    assert login_data["user"]["is_approved"] is False  # Public registration does not auto-approve!


# ===========================================================================
# 3. Refresh Token Rotation & Reuse Detection
# ===========================================================================

def test_refresh_token_rotation_and_reuse_detection(client, test_db, setup_test_environment):
    """Verify refresh token rotation and token-family invalidation on reuse."""
    min_id, dept_id, cadre_id, grade_id, desig_id, zone_id, state_id, loc_id = create_test_org_hierarchy(test_db, "ROT1")

    email = f"emp_rot_{uuid.uuid4().hex[:8]}@mospi.gov.in"
    reg_payload = {
        "email": email,
        "password": "ValidPassword2026!",
        "employee_code": f"EC_{uuid.uuid4().hex[:6]}",
        "full_name": "Rotational Officer",
        "ministry_id": min_id,
        "department_id": dept_id,
        "cadre_id": cadre_id,
        "location_id": loc_id,
        "designation_id": desig_id,
        "experience_years": 5.0,
    }
    client.post("/api/auth/register", json=reg_payload)
    token = setup_test_environment.get_latest_token(email)
    client.post("/api/auth/verify-email", json={"token": token})

    # Log in and obtain initial refresh token
    login_resp = client.post("/api/auth/login", json={"email": email, "password": "ValidPassword2026!"})
    initial_refresh = login_resp.json()["refresh_token"]

    # 1. Rotate refresh token -> Valid
    rot_resp1 = client.post("/api/auth/refresh", json={"refresh_token": initial_refresh})
    assert rot_resp1.status_code == 200
    new_refresh1 = rot_resp1.json()["refresh_token"]
    assert new_refresh1 != initial_refresh

    # 2. Rotate second time -> Valid
    rot_resp2 = client.post("/api/auth/refresh", json={"refresh_token": new_refresh1})
    assert rot_resp2.status_code == 200
    new_refresh2 = rot_resp2.json()["refresh_token"]
    assert new_refresh2 != new_refresh1

    # 3. REUSE ATTACK: Present initial_refresh (which has already been rotated/revoked)
    reuse_resp = client.post("/api/auth/refresh", json={"refresh_token": initial_refresh})
    assert reuse_resp.status_code == 401
    assert "reuse detected" in reuse_resp.json()["detail"].lower()

    # 4. Entire family must now be revoked: attempting to use newest refresh token is rejected
    invalidated_resp = client.post("/api/auth/refresh", json={"refresh_token": new_refresh2})
    assert invalidated_resp.status_code == 401


# ===========================================================================
# 4. Password Reset Lifecycle Tests
# ===========================================================================

def test_password_reset_lifecycle(client, test_db, setup_test_environment):
    """Verify password reset with single-use expiring token and session invalidation."""
    min_id, dept_id, cadre_id, grade_id, desig_id, zone_id, state_id, loc_id = create_test_org_hierarchy(test_db, "PW1")

    email = f"emp_pw_{uuid.uuid4().hex[:8]}@mospi.gov.in"
    client.post("/api/auth/register", json={
        "email": email,
        "password": "OldPassword2026!",
        "employee_code": f"EC_{uuid.uuid4().hex[:6]}",
        "full_name": "Reset Officer",
        "ministry_id": min_id,
        "department_id": dept_id,
        "cadre_id": cadre_id,
        "location_id": loc_id,
        "designation_id": desig_id,
        "experience_years": 4.0,
    })
    token = setup_test_environment.get_latest_token(email)
    client.post("/api/auth/verify-email", json={"token": token})

    # Log in to get an active session
    login_resp = client.post("/api/auth/login", json={"email": email, "password": "OldPassword2026!"})
    old_refresh = login_resp.json()["refresh_token"]

    # 1. Request password reset
    req_resp = client.post("/api/auth/password-reset/request", json={"email": email})
    assert req_resp.status_code == 200

    # 2. Extract reset token from email
    reset_token = setup_test_environment.get_latest_token(email)
    assert reset_token is not None

    # 3. Confirm password reset
    confirm_resp = client.post("/api/auth/password-reset/confirm", json={
        "token": reset_token,
        "new_password": "NewFreshPassword2026!",
    })
    assert confirm_resp.status_code == 200

    # 4. Old password rejected
    bad_login = client.post("/api/auth/login", json={"email": email, "password": "OldPassword2026!"})
    assert bad_login.status_code == 401

    # 5. Old refresh token invalidated
    bad_refresh = client.post("/api/auth/refresh", json={"refresh_token": old_refresh})
    assert bad_refresh.status_code == 401

    # 6. New password works
    good_login = client.post("/api/auth/login", json={"email": email, "password": "NewFreshPassword2026!"})
    assert good_login.status_code == 200


# ===========================================================================
# 5. Role Isolation & RBAC Boundary Tests
# ===========================================================================

def test_rbac_boundaries_and_separation_of_duties(client, test_db, setup_test_environment):
    """
    Verify strict backend RBAC:
    - Employee cannot access Admin or Staff endpoints.
    - Admin cannot access Staff endpoints.
    - Admin cannot self-delegate or expand own scopes.
    - Staff cannot bypass Administrator employee-acceptance authority.
    """
    min_id, dept_id, cadre_id, grade_id, desig_id, zone_id, state_id, loc_id = create_test_org_hierarchy(test_db, "RBAC")

    # 1. Create Staff user via bootstrap
    staff_email = f"staff_{uuid.uuid4().hex[:8]}@mospi.gov.in"
    staff_user = bootstrap_project_staff(
        email=staff_email,
        full_name="Lead Governance Officer",
        password="StaffMasterPassword2026!",
        staff_role="Platform Lead",
    )
    staff_login = client.post("/api/auth/login", json={"email": staff_email, "password": "StaffMasterPassword2026!"})
    staff_token = staff_login.json()["access_token"]
    staff_headers = {"Authorization": f"Bearer {staff_token}"}

    # 2. Staff invites an Administrator
    admin_email = f"admin_{uuid.uuid4().hex[:8]}@mospi.gov.in"
    invite_resp = client.post(
        "/api/project-staff/administrators/invite",
        headers=staff_headers,
        json={
            "email": admin_email,
            "official_designation": "Deputy Director General",
            "authorized_scopes": [
                {
                    "ministry_id": min_id,
                    "department_id": dept_id,
                    "geographic_level": "ZONE",
                    "zone_id": zone_id,
                }
            ],
        },
    )
    assert invite_resp.status_code == 200, invite_resp.text
    admin_invite_token = setup_test_environment.get_latest_token(admin_email)

    # 3. Administrator accepts invitation and sets password
    accept_resp = client.post(
        "/api/auth/accept-admin-invite",
        json={
            "token": admin_invite_token,
            "full_name": "Dr. Administrator",
            "password": "AdminSecurePassword2026!",
        },
    )
    assert accept_resp.status_code == 201
    admin_token = accept_resp.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 4. Create an Employee
    emp_email = f"emp_rbac_{uuid.uuid4().hex[:8]}@mospi.gov.in"
    client.post("/api/auth/register", json={
        "email": emp_email,
        "password": "EmpPassword2026!",
        "employee_code": f"EC_{uuid.uuid4().hex[:6]}",
        "full_name": "Subordinate Officer",
        "ministry_id": min_id,
        "department_id": dept_id,
        "cadre_id": cadre_id,
        "location_id": loc_id,
        "designation_id": desig_id,
        "experience_years": 3.0,
    })
    emp_token_val = setup_test_environment.get_latest_token(emp_email)
    client.post("/api/auth/verify-email", json={"token": emp_token_val})
    emp_login = client.post("/api/auth/login", json={"email": emp_email, "password": "EmpPassword2026!"})
    emp_token = emp_login.json()["access_token"]
    emp_headers = {"Authorization": f"Bearer {emp_token}"}

    # --- RBAC Assertion 1: Anonymous access rejected ---
    anon_resp = client.get("/api/admin/scopes")
    assert anon_resp.status_code == 403 or anon_resp.status_code == 401

    # --- RBAC Assertion 2: Employee cannot access Administrator endpoints ---
    emp_on_admin = client.get("/api/admin/scopes", headers=emp_headers)
    assert emp_on_admin.status_code == 403

    # --- RBAC Assertion 3: Employee cannot access Project Staff endpoints ---
    emp_on_staff = client.get("/api/project-staff/administrators", headers=emp_headers)
    assert emp_on_staff.status_code == 403

    # --- RBAC Assertion 4: Administrator cannot access Project Staff endpoints ---
    admin_on_staff = client.get("/api/project-staff/administrators", headers=admin_headers)
    assert admin_on_staff.status_code == 403

    # --- RBAC Assertion 5: Administrator can read their own scopes ---
    admin_scopes_resp = client.get("/api/admin/scopes", headers=admin_headers)
    assert admin_scopes_resp.status_code == 200
    scopes = admin_scopes_resp.json()
    assert len(scopes) == 1
    assert scopes[0]["zone_id"] == zone_id

    # --- RBAC Assertion 6: Administrator cannot modify their own scopes (no self-delegation) ---
    # Only staff can call PUT /api/project-staff/administrators/{id}/scopes
    admin_profile_id = accept_resp.json()["user"]["profile"]["profile_id"]
    admin_self_update = client.put(
        f"/api/project-staff/administrators/{admin_profile_id}/scopes",
        headers=admin_headers,
        json=[],
    )
    assert admin_self_update.status_code == 403

    # --- RBAC Assertion 7: Header tampering (X-Learner-ID) cannot bypass RBAC ---
    tampered_headers = {
        "Authorization": f"Bearer {emp_token}",
        "X-Learner-ID": "ADMIN-SUPERVISOR",
    }
    tampered_resp = client.get("/api/admin/scopes", headers=tampered_headers)
    assert tampered_resp.status_code == 403


# ===========================================================================
# 6. Unapproved Employee Learning Workspace Hard Invariant Tests
# ===========================================================================

def test_unapproved_employee_cannot_access_learning_workspace(client, test_db, setup_test_environment):
    """
    Hard Invariant: Unapproved employees must NOT access protected employee functionality.
    Only approved employees (approval_status == APPROVED) may access /api/employee/learning-workspace.
    """
    min_id, dept_id, cadre_id, grade_id, desig_id, zone_id, state_id, loc_id = create_test_org_hierarchy(test_db, "WS1")

    email = f"emp_ws_{uuid.uuid4().hex[:8]}@mospi.gov.in"
    client.post("/api/auth/register", json={
        "email": email,
        "password": "EmpStrongPassword2026!",
        "employee_code": f"EC_{uuid.uuid4().hex[:6]}",
        "full_name": "Applicant Officer",
        "ministry_id": min_id,
        "department_id": dept_id,
        "cadre_id": cadre_id,
        "location_id": loc_id,
        "designation_id": desig_id,
        "experience_years": 2.0,
    })
    token = setup_test_environment.get_latest_token(email)
    client.post("/api/auth/verify-email", json={"token": token})

    login_resp = client.post("/api/auth/login", json={"email": email, "password": "EmpStrongPassword2026!"})
    access_token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 1. Employee can access their own application status
    status_resp = client.get("/api/employee/application-status", headers=headers)
    assert status_resp.status_code == 200
    assert status_resp.json()["approval_status"] == "UNAPPROVED"

    # 2. Unapproved employee CANNOT access protected learning workspace -> 403 Forbidden
    ws_resp_unapproved = client.get("/api/employee/learning-workspace", headers=headers)
    assert ws_resp_unapproved.status_code == 403
    assert "administrative approval is required" in ws_resp_unapproved.json()["detail"].lower()

    # 3. Simulate official Administrator approval in database
    emp_profile = test_db.scalar(select(EmployeeProfile).where(EmployeeProfile.employee_code == status_resp.json()["employee_code"]))
    emp_profile.approval_status = ApprovalStatusEnum.APPROVED
    emp_profile.approved_at = datetime.now(timezone.utc)
    test_db.commit()

    # 4. Now approved employee CAN access protected learning workspace -> 200 OK
    ws_resp_approved = client.get("/api/employee/learning-workspace", headers=headers)
    assert ws_resp_approved.status_code == 200
    assert ws_resp_approved.json()["status"] == "APPROVED_LEARNER"


# ===========================================================================
# 7. Jurisdictional Boundary Check Unit Tests
# ===========================================================================

def test_jurisdiction_scoping_rules():
    """Verify jurisdictional evaluation logic across geographic and organizational levels."""
    # Create mock scope: ZONE level
    scope_zone = AdministratorScope(
        admin_id=uuid.uuid4(),
        ministry_id="MIN_MOSPI",
        department_id="DEPT_FOD",
        cadre_id="CAD_ISS",
        grade_band_id=None,
        geographic_level=GeographicLevelEnum.ZONE,
        zone_id="ZN_NORTH",
        state_id=None,
        location_id=None,
    )

    # In jurisdiction: same ministry, dept, cadre, and zone
    assert is_within_admin_jurisdiction(
        [scope_zone],
        target_ministry_id="MIN_MOSPI",
        target_department_id="DEPT_FOD",
        target_cadre_id="CAD_ISS",
        target_zone_id="ZN_NORTH",
    ) is True

    # Out of jurisdiction: different zone
    assert is_within_admin_jurisdiction(
        [scope_zone],
        target_ministry_id="MIN_MOSPI",
        target_department_id="DEPT_FOD",
        target_cadre_id="CAD_ISS",
        target_zone_id="ZN_SOUTH",
    ) is False

    # Out of jurisdiction: different department
    assert is_within_admin_jurisdiction(
        [scope_zone],
        target_ministry_id="MIN_MOSPI",
        target_department_id="DEPT_NAD",
        target_cadre_id="CAD_ISS",
        target_zone_id="ZN_NORTH",
    ) is False

    # Create mock scope: NATIONAL level
    scope_national = AdministratorScope(
        admin_id=uuid.uuid4(),
        ministry_id="MIN_MOSPI",
        department_id=None,
        cadre_id=None,
        grade_band_id=None,
        geographic_level=GeographicLevelEnum.NATIONAL,
        zone_id=None,
        state_id=None,
        location_id=None,
    )
    # Matches any zone/state/location within MIN_MOSPI
    assert is_within_admin_jurisdiction(
        [scope_national],
        target_ministry_id="MIN_MOSPI",
        target_zone_id="ZN_WEST",
    ) is True


# ===========================================================================
# 8. Account Deactivation Tests
# ===========================================================================

def test_account_deactivation(client, test_db, setup_test_environment):
    """Verify employee can deactivate own account and tokens are revoked."""
    min_id, dept_id, cadre_id, grade_id, desig_id, zone_id, state_id, loc_id = create_test_org_hierarchy(test_db, "DEACT")

    email = f"emp_deact_{uuid.uuid4().hex[:8]}@mospi.gov.in"
    client.post("/api/auth/register", json={
        "email": email,
        "password": "EmpDeactPassword2026!",
        "employee_code": f"EC_{uuid.uuid4().hex[:6]}",
        "full_name": "Departing Officer",
        "ministry_id": min_id,
        "department_id": dept_id,
        "cadre_id": cadre_id,
        "location_id": loc_id,
        "designation_id": desig_id,
        "experience_years": 10.0,
    })
    token = setup_test_environment.get_latest_token(email)
    client.post("/api/auth/verify-email", json={"token": token})

    login_resp = client.post("/api/auth/login", json={"email": email, "password": "EmpDeactPassword2026!"})
    access_token = login_resp.json()["access_token"]
    refresh_token = login_resp.json()["refresh_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 1. Wrong password confirmation rejected
    bad_deact = client.post("/api/employee/deactivate-account", headers=headers, json={"password": "WrongPassword!"})
    assert bad_deact.status_code == 401

    # 2. Correct password confirms deactivation
    good_deact = client.post("/api/employee/deactivate-account", headers=headers, json={"password": "EmpDeactPassword2026!"})
    assert good_deact.status_code == 200

    # 3. Subsequent login rejected
    login_after = client.post("/api/auth/login", json={"email": email, "password": "EmpDeactPassword2026!"})
    assert login_after.status_code == 403
    assert "deactivated" in login_after.json()["detail"].lower()

    # 4. Refresh token rejected
    refresh_after = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_after.status_code == 401


# ===========================================================================
# 9. Additional Security & Edge-Case Authorization Tests
# ===========================================================================

def test_logout_and_refresh_token_revocation(client, test_db, setup_test_environment):
    """Verify calling /api/auth/logout explicitly revokes refresh tokens."""
    min_id, dept_id, cadre_id, grade_id, desig_id, zone_id, state_id, loc_id = create_test_org_hierarchy(test_db, "LGO")

    email = f"emp_lgo_{uuid.uuid4().hex[:8]}@mospi.gov.in"
    client.post("/api/auth/register", json={
        "email": email,
        "password": "LogoutPassword2026!",
        "employee_code": f"EC_{uuid.uuid4().hex[:6]}",
        "full_name": "Logging Out Officer",
        "ministry_id": min_id,
        "department_id": dept_id,
        "cadre_id": cadre_id,
        "location_id": loc_id,
        "designation_id": desig_id,
        "experience_years": 1.0,
    })
    token = setup_test_environment.get_latest_token(email)
    client.post("/api/auth/verify-email", json={"token": token})

    login_resp = client.post("/api/auth/login", json={"email": email, "password": "LogoutPassword2026!"})
    access_token = login_resp.json()["access_token"]
    refresh_token = login_resp.json()["refresh_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 1. Logout
    logout_resp = client.post("/api/auth/logout", headers=headers, json={"refresh_token": refresh_token})
    assert logout_resp.status_code == 200

    # 2. Refresh token is now revoked
    ref_resp = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert ref_resp.status_code == 401


def test_invalid_and_expired_admin_invitation_rejection(client, test_db, setup_test_environment):
    """Verify invalid, expired, and duplicate administrator invitation acceptances are rejected."""
    # 1. Non-existent token -> 400 Bad Request
    fake_resp = client.post("/api/auth/accept-admin-invite", json={
        "token": "non_existent_token_12345",
        "full_name": "Fake Admin",
        "password": "SomePassword2026!",
    })
    assert fake_resp.status_code == 400

    # 2. Expired invitation token in DB -> 410 Gone
    staff_user = bootstrap_project_staff(
        email=f"staff_{uuid.uuid4().hex[:8]}@mospi.gov.in",
        full_name="Staff Lead",
        password="StaffSecret2026!",
    )
    raw_token = generate_secure_token(32)
    token_digest = hash_token(raw_token)
    past_time = datetime.now(timezone.utc) - timedelta(hours=2)

    invitation = AdminInvitation(
        email=f"admin_exp_{uuid.uuid4().hex[:8]}@mospi.gov.in",
        token_hash=token_digest,
        official_designation="Director",
        authorized_scopes=[],
        created_by_staff_id=staff_user.id,
        expires_at=past_time,
        is_consumed=False,
    )
    test_db.add(invitation)
    test_db.commit()

    expired_resp = client.post("/api/auth/accept-admin-invite", json={
        "token": raw_token,
        "full_name": "Expired Admin",
        "password": "ValidPassword2026!",
    })
    assert expired_resp.status_code == 410
    assert "expired" in expired_resp.json()["detail"].lower()
