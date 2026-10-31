"""
FastAPI Router for Authentication, Identity, RBAC & Jurisdictions in SIH26101 Platform.
Implements the 41-endpoint matrix specifications from FINAL_ARCHITECTURE_PLAN_v2.7.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from competency_engine.auth.dependencies import (
    get_admin_profile,
    get_client_ip,
    get_current_user,
    get_employee_profile,
    get_staff_profile,
    require_admin_user,
    require_approved_employee,
    require_employee_user,
    require_role,
    require_staff_user,
)
from competency_engine.auth.schemas import (
    AdminAcceptInviteRequest,
    AdminInviteRequest,
    ApplicationStatusResponse,
    DeactivateAccountRequest,
    EmailVerificationRequest,
    EmployeeRegisterRequest,
    LoginRequest,
    MessageResponse,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserSummaryResponse,
)
from competency_engine.auth.service import AuthService
from competency_engine.db import (
    AccountStatusEnum,
    AccountTypeEnum,
    AdministratorProfile,
    AdministratorScope,
    ApprovalStatusEnum,
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
    ProjectStaffProfile,
    RefreshToken,
    User,
    get_db,
)

router = APIRouter(tags=["Authentication & Identity"])


def _build_user_summary(user: User, db: Session) -> UserSummaryResponse:
    """Helper to construct rich user summary response based on account type."""
    is_approved = False
    profile_data: Optional[Dict[str, Any]] = None

    if user.account_type == AccountTypeEnum.EMPLOYEE:
        emp = db.scalar(select(EmployeeProfile).where(EmployeeProfile.user_id == user.id))
        if emp:
            is_approved = (emp.approval_status == ApprovalStatusEnum.APPROVED)
            profile_data = {
                "profile_id": str(emp.id),
                "employee_code": emp.employee_code,
                "full_name": emp.full_name,
                "ministry_id": emp.ministry_id,
                "department_id": emp.department_id,
                "cadre_id": emp.cadre_id,
                "location_id": emp.location_id,
                "designation_id": emp.designation_id,
                "experience_years": float(emp.experience_years),
                "approval_status": emp.approval_status.value,
                "approved_at": emp.approved_at.isoformat() if emp.approved_at else None,
            }
    elif user.account_type == AccountTypeEnum.ADMINISTRATOR:
        adm = db.scalar(
            select(AdministratorProfile)
            .options(joinedload(AdministratorProfile.scopes))
            .where(AdministratorProfile.user_id == user.id)
        )
        if adm:
            is_approved = True
            profile_data = {
                "profile_id": str(adm.id),
                "full_name": adm.full_name,
                "official_designation": adm.official_designation,
                "max_managed_employees": adm.max_managed_employees,
                "is_active": adm.is_active,
                "scopes": [
                    {
                        "id": str(s.id),
                        "ministry_id": s.ministry_id,
                        "department_id": s.department_id,
                        "cadre_id": s.cadre_id,
                        "grade_band_id": s.grade_band_id,
                        "geographic_level": s.geographic_level.value,
                        "zone_id": s.zone_id,
                        "state_id": s.state_id,
                        "location_id": s.location_id,
                    }
                    for s in adm.scopes
                ],
            }
    elif user.account_type == AccountTypeEnum.PROJECT_STAFF:
        stf = db.scalar(select(ProjectStaffProfile).where(ProjectStaffProfile.user_id == user.id))
        if stf:
            is_approved = True
            profile_data = {
                "profile_id": str(stf.id),
                "full_name": stf.full_name,
                "staff_role": stf.staff_role,
            }

    return UserSummaryResponse(
        id=str(user.id),
        email=user.email,
        account_type=user.account_type.value,
        account_status=user.account_status.value,
        is_approved=is_approved,
        profile=profile_data,
    )


# ===========================================================================
# 1. Public Authentication Endpoints
# ===========================================================================

@router.post("/api/auth/register", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
def register_employee(
    req: EmployeeRegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Public self-registration for Civil Service Employees.
    Creates account in UNVERIFIED_EMAIL and employee profile in UNAPPROVED status.
    Dispatches single-use verification email.
    """
    client_ip = get_client_ip(request)
    user, _ = AuthService.register_employee(db, req, client_ip)
    summary = _build_user_summary(user, db)
    return {
        "message": "Registration successful. Please check your email to verify your account.",
        "user": summary.model_dump(),
    }


@router.post("/api/auth/verify-email", response_model=Dict[str, Any])
def verify_email(
    req: EmailVerificationRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Verify email address with single-use token and activate login."""
    client_ip = get_client_ip(request)
    user = AuthService.verify_email(db, req.token, client_ip)
    summary = _build_user_summary(user, db)
    return {
        "message": "Email verified successfully. Your account is now active.",
        "user": summary.model_dump(),
    }


@router.post("/api/auth/login", response_model=TokenResponse)
def login(
    req: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Authenticate credentials with Argon2id, rate limiting, and token rotation."""
    client_ip = get_client_ip(request)
    user, access_token, refresh_token = AuthService.authenticate_user(
        db, req.email, req.password, client_ip
    )
    summary = _build_user_summary(user, db)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=900,
        refresh_token=refresh_token,
        user=summary,
    )


@router.post("/api/auth/refresh", response_model=TokenResponse)
def refresh_token(
    req: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Rotate refresh token with family reuse detection and revocation."""
    client_ip = get_client_ip(request)
    user, new_access, new_refresh = AuthService.rotate_refresh_token(
        db, req.refresh_token, client_ip
    )
    summary = _build_user_summary(user, db)
    return TokenResponse(
        access_token=new_access,
        token_type="bearer",
        expires_in=900,
        refresh_token=new_refresh,
        user=summary,
    )


@router.post("/api/auth/logout", response_model=MessageResponse)
def logout(
    req: Optional[RefreshTokenRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Revoke authenticated user's refresh token(s)."""
    raw_ref = req.refresh_token if req else None
    AuthService.logout(db, current_user.id, raw_ref)
    return MessageResponse(message="Logged out successfully.")


@router.post("/api/auth/password-reset/request", response_model=MessageResponse)
def request_password_reset(
    req: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Initiate password reset (rate-limited, enumeration-safe)."""
    client_ip = get_client_ip(request)
    AuthService.request_password_reset(db, req.email, client_ip)
    return MessageResponse(
        message="If an account with that email exists, password reset instructions have been sent."
    )


@router.post("/api/auth/password-reset/confirm", response_model=MessageResponse)
def confirm_password_reset(
    req: PasswordResetConfirmRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Confirm password reset with single-use token and update password."""
    client_ip = get_client_ip(request)
    AuthService.confirm_password_reset(db, req.token, req.new_password, client_ip)
    return MessageResponse(
        message="Password has been reset successfully. You may now log in with your new password."
    )


@router.get("/api/auth/me", response_model=UserSummaryResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserSummaryResponse:
    """Return authenticated caller identity and linked role profile."""
    return _build_user_summary(current_user, db)


@router.post("/api/auth/accept-admin-invite", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
def accept_admin_invite(
    req: AdminAcceptInviteRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Activate Administrator account from single-use staff invitation."""
    client_ip = get_client_ip(request)
    user, access_token, refresh_token = AuthService.accept_admin_invite(db, req, client_ip)
    summary = _build_user_summary(user, db)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=900,
        refresh_token=refresh_token,
        user=summary,
    )


# ===========================================================================
# 2. Employee Identity & Status Endpoints
# ===========================================================================

@router.get("/api/employee/application-status", response_model=ApplicationStatusResponse)
def get_employee_application_status(
    current_user: User = Depends(require_employee_user),
    db: Session = Depends(get_db),
) -> ApplicationStatusResponse:
    """
    Retrieve employee's onboarding application and platform approval status.
    Civil servants can view their submission progress without administrative privileges.
    """
    profile = db.scalar(select(EmployeeProfile).where(EmployeeProfile.user_id == current_user.id))
    if not profile:
        return ApplicationStatusResponse(
            user_id=str(current_user.id),
            email=current_user.email,
            account_status=current_user.account_status.value,
            approval_status=ApprovalStatusEnum.UNAPPROVED.value,
            has_profile=False,
        )

    # Fetch latest application
    latest_app = db.scalar(
        select(EmployeeApplication)
        .where(EmployeeApplication.employee_id == profile.id)
        .order_by(EmployeeApplication.submission_number.desc())
    )

    # If approved by an administrator, get admin name
    admin_name: Optional[str] = None
    if profile.approved_by_admin_id:
        adm = db.scalar(select(AdministratorProfile).where(AdministratorProfile.id == profile.approved_by_admin_id))
        if adm:
            admin_name = adm.full_name

    return ApplicationStatusResponse(
        user_id=str(current_user.id),
        email=current_user.email,
        account_status=current_user.account_status.value,
        approval_status=profile.approval_status.value,
        has_profile=True,
        employee_code=profile.employee_code,
        full_name=profile.full_name,
        application_id=str(latest_app.id) if latest_app else None,
        application_status=latest_app.status.value if latest_app else None,
        submission_number=latest_app.submission_number if latest_app else None,
        approved_at=profile.approved_at.isoformat() if profile.approved_at else None,
        assigned_admin_name=admin_name,
    )


@router.post("/api/employee/deactivate-account", response_model=MessageResponse)
def deactivate_employee_account(
    req: DeactivateAccountRequest,
    current_user: User = Depends(require_employee_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Deactivate caller's own employee account after password confirmation."""
    AuthService.deactivate_account(db, current_user, req.password)
    return MessageResponse(message="Account deactivated successfully.")


@router.get("/api/employee/learning-workspace", response_model=Dict[str, Any])
def get_employee_learning_workspace(
    profile: EmployeeProfile = Depends(require_approved_employee),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Protected employee learning workspace.
    Hard Invariant: Unapproved or revoked employees are strictly rejected with 403 Forbidden.
    """
    return {
        "status": "APPROVED_LEARNER",
        "employee_code": profile.employee_code,
        "full_name": profile.full_name,
        "approval_status": profile.approval_status.value,
        "approved_at": profile.approved_at.isoformat() if profile.approved_at else None,
        "ministry_id": profile.ministry_id,
        "department_id": profile.department_id,
        "cadre_id": profile.cadre_id,
        "location_id": profile.location_id,
        "experience_years": float(profile.experience_years),
        "self_declared_skills": profile.self_declared_skills,
        "workspace": {
            "enrolled_courses": [],
            "completed_modules": 0,
            "weekly_progress_percentage": 0,
            "active_competencies": profile.self_declared_skills,
        },
    }


# ===========================================================================
# 3. Administrator Endpoints
# ===========================================================================

@router.get("/api/admin/scopes", response_model=List[Dict[str, Any]])
def get_administrator_scopes(
    admin_profile: AdministratorProfile = Depends(get_admin_profile),
) -> List[Dict[str, Any]]:
    """Return caller's authorized administrative scopes and jurisdictional boundaries."""
    return [
        {
            "id": str(s.id),
            "ministry_id": s.ministry_id,
            "department_id": s.department_id,
            "cadre_id": s.cadre_id,
            "grade_band_id": s.grade_band_id,
            "geographic_level": s.geographic_level.value,
            "zone_id": s.zone_id,
            "state_id": s.state_id,
            "location_id": s.location_id,
        }
        for s in admin_profile.scopes
    ]


# ===========================================================================
# 4. Project Staff Governance Endpoints
# ===========================================================================

@router.post("/api/project-staff/administrators/invite", response_model=Dict[str, Any])
def invite_administrator(
    req: AdminInviteRequest,
    current_staff: User = Depends(require_staff_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Project Staff invites a new Administrator with designated scopes.
    Generates a single-use token expiring in 72 hours.
    """
    invitation, raw_token = AuthService.invite_administrator(db, current_staff, req)
    return {
        "message": f"Administrator invitation created for {req.email}.",
        "invitation_id": str(invitation.id),
        "email": invitation.email,
        "official_designation": invitation.official_designation,
        "expires_at": invitation.expires_at.isoformat(),
        # Token is delivered via email; not exposed in public production response
    }


@router.get("/api/project-staff/administrators", response_model=List[Dict[str, Any]])
def list_administrators(
    current_staff: User = Depends(require_staff_user),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """List all administrators and their assigned scopes for governance review."""
    admins = db.scalars(
        select(AdministratorProfile).options(joinedload(AdministratorProfile.scopes))
    ).unique().all()

    results = []
    for adm in admins:
        user = db.scalar(select(User).where(User.id == adm.user_id))
        results.append({
            "id": str(adm.id),
            "user_id": str(adm.user_id),
            "email": user.email if user else None,
            "full_name": adm.full_name,
            "official_designation": adm.official_designation,
            "max_managed_employees": adm.max_managed_employees,
            "is_active": adm.is_active,
            "account_status": user.account_status.value if user else None,
            "scopes": [
                {
                    "id": str(s.id),
                    "ministry_id": s.ministry_id,
                    "department_id": s.department_id,
                    "cadre_id": s.cadre_id,
                    "grade_band_id": s.grade_band_id,
                    "geographic_level": s.geographic_level.value,
                    "zone_id": s.zone_id,
                    "state_id": s.state_id,
                    "location_id": s.location_id,
                }
                for s in adm.scopes
            ],
        })
    return results


@router.put("/api/project-staff/administrators/{admin_id}/scopes", response_model=Dict[str, Any])
def update_administrator_scopes(
    admin_id: uuid.UUID,
    scopes: List[Dict[str, Any]],
    current_staff: User = Depends(require_staff_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Update authorized scopes for an Administrator."""
    admin_profile = db.scalar(
        select(AdministratorProfile)
        .options(joinedload(AdministratorProfile.scopes))
        .where(AdministratorProfile.id == admin_id)
    )
    if not admin_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Administrator with ID '{admin_id}' not found.",
        )

    # Remove existing scopes and replace
    for s in list(admin_profile.scopes):
        db.delete(s)

    for scope_def in scopes:
        geo_str = scope_def.get("geographic_level", "NATIONAL").upper()
        try:
            geo_level = GeographicLevelEnum(geo_str)
        except ValueError:
            geo_level = GeographicLevelEnum.NATIONAL

        new_scope = AdministratorScope(
            admin_id=admin_profile.id,
            ministry_id=scope_def.get("ministry_id", "MIN_MOSPI"),
            department_id=scope_def.get("department_id"),
            cadre_id=scope_def.get("cadre_id"),
            grade_band_id=scope_def.get("grade_band_id"),
            geographic_level=geo_level,
            zone_id=scope_def.get("zone_id"),
            state_id=scope_def.get("state_id"),
            location_id=scope_def.get("location_id"),
        )
        db.add(new_scope)

    db.commit()
    return {
        "message": f"Updated scopes for administrator '{admin_profile.full_name}'.",
        "admin_id": str(admin_id),
        "total_scopes": len(scopes),
    }


@router.post("/api/project-staff/users/{user_id}/status", response_model=Dict[str, Any])
def set_user_account_status(
    user_id: uuid.UUID,
    account_status_val: str,
    current_staff: User = Depends(require_staff_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Project Staff governance action: suspend or reinstate an account."""
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found.",
        )

    try:
        new_status = AccountStatusEnum(account_status_val.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid account status '{account_status_val}'. Valid values: {[s.value for s in AccountStatusEnum]}",
        )

    user.account_status = new_status
    if new_status in (AccountStatusEnum.SUSPENDED, AccountStatusEnum.DEACTIVATED):
        # Invalidate active refresh tokens
        from sqlalchemy import update
        db.execute(
            update(RefreshToken).where(RefreshToken.user_id == user.id).values(is_revoked=True)
        )

    db.commit()
    return {
        "message": f"Account status for user '{user.email}' updated to {new_status.value}.",
        "user_id": str(user_id),
        "account_status": new_status.value,
    }


# ===========================================================================
# 5. Organizational Taxonomy Read Endpoints (Supports Registration UI)
# ===========================================================================

@router.get("/api/org/taxonomy", response_model=Dict[str, Any])
def get_organizational_taxonomy(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Public taxonomy directory for registration form dropdowns and UI navigation.
    Returns ministries, departments, cadres, grade bands, designations, zones, states, and locations.
    """
    ministries = db.scalars(select(OrgMinistry).where(OrgMinistry.is_active == True)).all()
    departments = db.scalars(select(OrgDepartment).where(OrgDepartment.is_active == True)).all()
    cadres = db.scalars(select(OrgCadre).where(OrgCadre.is_active == True)).all()
    grade_bands = db.scalars(select(OrgGradeBand).order_by(OrgGradeBand.hierarchical_rank.asc())).all()
    designations = db.scalars(select(OrgDesignation).where(OrgDesignation.is_active == True)).all()
    zones = db.scalars(select(OrgZone)).all()
    states = db.scalars(select(OrgState)).all()
    locations = db.scalars(select(OrgLocation)).all()

    return {
        "ministries": [{"id": m.id, "name": m.name, "code": m.code} for m in ministries],
        "departments": [
            {"id": d.id, "ministry_id": d.ministry_id, "name": d.name, "code": d.code}
            for d in departments
        ],
        "cadres": [{"id": c.id, "name": c.name, "controlling_authority": c.controlling_authority} for c in cadres],
        "grade_bands": [{"id": g.id, "name": g.name, "rank": g.hierarchical_rank} for g in grade_bands],
        "designations": [
            {"id": d.id, "name": d.name, "grade_band_id": d.grade_band_id, "cadre_id": d.cadre_id}
            for d in designations
        ],
        "zones": [{"id": z.id, "name": z.name, "code": z.code} for z in zones],
        "states": [{"id": s.id, "zone_id": s.zone_id, "name": s.name, "code": s.code} for s in states],
        "locations": [
            {
                "id": l.id,
                "state_id": l.state_id,
                "zone_id": l.zone_id,
                "city": l.city,
                "building_name": l.building_name,
                "pin_code": l.pin_code,
            }
            for l in locations
        ],
    }
