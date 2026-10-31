"""
Pydantic Schemas for Authentication and Identity in SIH26101 Platform.
Strict request/response type validation according to FINAL_ARCHITECTURE_PLAN_v2.7.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field


class EmployeeRegisterRequest(BaseModel):
    """Public employee self-registration schema."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    employee_code: str = Field(..., min_length=2, max_length=64)
    full_name: str = Field(..., min_length=2, max_length=255)
    ministry_id: str = Field(..., min_length=1, max_length=32)
    department_id: str = Field(..., min_length=1, max_length=32)
    cadre_id: str = Field(..., min_length=1, max_length=32)
    location_id: str = Field(..., min_length=1, max_length=32)
    designation_id: str = Field(..., min_length=1, max_length=32)
    experience_years: Decimal = Field(..., ge=0.0, le=60.0)
    phone_number: Optional[str] = Field(None, max_length=20)
    self_declared_skills: List[str] = Field(default_factory=list)
    supporting_document_path: Optional[str] = None


class LoginRequest(BaseModel):
    """Account login credentials."""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token rotation request."""
    refresh_token: str


class EmailVerificationRequest(BaseModel):
    """Single-use email verification request."""
    token: str


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    """Password reset confirmation schema."""
    token: str
    new_password: str = Field(..., min_length=8)


class AdminInviteRequest(BaseModel):
    """Project Staff administrator invitation schema."""
    email: EmailStr
    official_designation: str = Field(..., min_length=2, max_length=255)
    authorized_scopes: List[Dict[str, Any]] = Field(default_factory=list)


class AdminAcceptInviteRequest(BaseModel):
    """Administrator invite acceptance & activation schema."""
    token: str
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8)


class DeactivateAccountRequest(BaseModel):
    """Account deactivation confirmation schema."""
    password: str


class UserSummaryResponse(BaseModel):
    """Public user identity summary."""
    id: str
    email: str
    account_type: str
    account_status: str
    is_approved: bool = False
    profile: Optional[Dict[str, Any]] = None


class TokenResponse(BaseModel):
    """OAuth2-compatible token issuance response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes
    refresh_token: str
    user: UserSummaryResponse


class MessageResponse(BaseModel):
    """Standard generic operational message."""
    message: str
    detail: Optional[str] = None


class ApplicationStatusResponse(BaseModel):
    """Employee application and approval status response."""
    user_id: str
    email: str
    account_status: str
    approval_status: str
    has_profile: bool
    employee_code: Optional[str] = None
    full_name: Optional[str] = None
    application_id: Optional[str] = None
    application_status: Optional[str] = None
    submission_number: Optional[int] = None
    approved_at: Optional[str] = None
    assigned_admin_name: Optional[str] = None

