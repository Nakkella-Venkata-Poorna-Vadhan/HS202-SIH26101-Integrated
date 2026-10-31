"""
Reusable FastAPI Authentication & Authorization Dependencies for SIH26101 Platform.
Enforces strict server-side RBAC, JWT verification, and jurisdiction scope boundaries.
Eliminates user-controlled identity headers (X-Learner-ID) on protected endpoints.
"""

from __future__ import annotations

import uuid
from typing import Callable, List, Optional, Tuple

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from competency_engine.auth.tokens import decode_access_token
from competency_engine.db import (
    AccountStatusEnum,
    AccountTypeEnum,
    AdministratorProfile,
    AdministratorScope,
    ApprovalStatusEnum,
    EmployeeProfile,
    GeographicLevelEnum,
    ProjectStaffProfile,
    User,
    get_db,
)

# Mandatory bearer scheme
security_bearer = HTTPBearer(auto_error=True)
optional_bearer = HTTPBearer(auto_error=False)


def get_client_ip(request: Request) -> str:
    """Extract client IP address for audit and rate-limiting."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
    db: Session = Depends(get_db),
) -> User:
    """
    Validate access token and return verified, active User entity.
    Never relies on client-supplied identity headers or unverified input.
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token: missing subject claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token: invalid subject UUID.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.scalar(select(User).where(User.id == user_uuid))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User identity in token not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.account_status != AccountStatusEnum.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Account is not active (status: {user.account_status.value}).",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Optional authentication dependency; returns None if unauthenticated."""
    if not credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
        user = db.scalar(select(User).where(User.id == uuid.UUID(user_id_str)))
        if user and user.account_status == AccountStatusEnum.ACTIVE:
            return user
        return None
    except Exception:
        return None


def require_role(*allowed_roles: AccountTypeEnum) -> Callable[[User], User]:
    """Dependency factory restricting access to specific account types."""

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.account_type not in allowed_roles:
            role_names = [r.value for r in allowed_roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: this resource requires one of the following roles: {', '.join(role_names)}.",
            )
        return current_user

    return role_checker


# Role-specific dependencies
require_employee_user = require_role(AccountTypeEnum.EMPLOYEE)
require_admin_user = require_role(AccountTypeEnum.ADMINISTRATOR)
require_staff_user = require_role(AccountTypeEnum.PROJECT_STAFF)


def get_employee_profile(
    current_user: User = Depends(require_employee_user),
    db: Session = Depends(get_db),
) -> EmployeeProfile:
    """Retrieve the EmployeeProfile for the currently authenticated employee."""
    profile = db.scalar(select(EmployeeProfile).where(EmployeeProfile.user_id == current_user.id))
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found.",
        )
    return profile


def require_approved_employee(
    profile: EmployeeProfile = Depends(get_employee_profile),
) -> EmployeeProfile:
    """
    Strict invariant: Protects employee learning workspace and advanced features.
    Rejects unapproved or revoked employees with 403 Forbidden.
    """
    if profile.approval_status != ApprovalStatusEnum.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Official administrative approval is required to access protected employee services. Your current approval status is "
            f"'{profile.approval_status.value}'.",
        )
    return profile


def get_admin_profile(
    current_user: User = Depends(require_admin_user),
    db: Session = Depends(get_db),
) -> AdministratorProfile:
    """Retrieve AdministratorProfile and eager-load authorized scopes."""
    profile = db.scalar(
        select(AdministratorProfile)
        .options(joinedload(AdministratorProfile.scopes))
        .where(AdministratorProfile.user_id == current_user.id)
    )
    if not profile or not profile.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator profile is inactive or not found.",
        )
    return profile


def get_staff_profile(
    current_user: User = Depends(require_staff_user),
    db: Session = Depends(get_db),
) -> ProjectStaffProfile:
    """Retrieve ProjectStaffProfile."""
    profile = db.scalar(
        select(ProjectStaffProfile).where(ProjectStaffProfile.user_id == current_user.id)
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project Staff profile not found.",
        )
    return profile


def is_within_admin_jurisdiction(
    admin_scopes: List[AdministratorScope],
    target_ministry_id: str,
    target_department_id: Optional[str] = None,
    target_cadre_id: Optional[str] = None,
    target_grade_band_id: Optional[str] = None,
    target_zone_id: Optional[str] = None,
    target_state_id: Optional[str] = None,
    target_location_id: Optional[str] = None,
) -> bool:
    """
    Evaluate whether a target employee / application lies within the administrator's authorized scopes.
    Checks organizational boundaries and hierarchical geographic levels (NATIONAL > ZONE > STATE > STATION).
    """
    for scope in admin_scopes:
        # Ministry match is required
        if scope.ministry_id != target_ministry_id:
            continue

        # Department match if scope is departmental
        if scope.department_id and target_department_id and scope.department_id != target_department_id:
            continue

        # Cadre match if scope is cadre-specific
        if scope.cadre_id and target_cadre_id and scope.cadre_id != target_cadre_id:
            continue

        # Grade band match if scope is grade-specific
        if scope.grade_band_id and target_grade_band_id and scope.grade_band_id != target_grade_band_id:
            continue

        # Geographic level check
        if scope.geographic_level == GeographicLevelEnum.NATIONAL:
            return True
        elif scope.geographic_level == GeographicLevelEnum.ZONE:
            if target_zone_id and scope.zone_id == target_zone_id:
                return True
        elif scope.geographic_level == GeographicLevelEnum.STATE:
            if target_zone_id and target_state_id and scope.zone_id == target_zone_id and scope.state_id == target_state_id:
                return True
        elif scope.geographic_level == GeographicLevelEnum.STATION:
            if (
                target_zone_id
                and target_state_id
                and target_location_id
                and scope.zone_id == target_zone_id
                and scope.state_id == target_state_id
                and scope.location_id == target_location_id
            ):
                return True

    return False

