"""
Authentication and Identity Package for SIH26101 Platform.
"""

from competency_engine.auth.dependencies import (
    get_admin_profile,
    get_client_ip,
    get_current_user,
    get_employee_profile,
    get_optional_current_user,
    get_staff_profile,
    is_within_admin_jurisdiction,
    require_admin_user,
    require_approved_employee,
    require_employee_user,
    require_role,
    require_staff_user,
)
from competency_engine.auth.password import hash_password, verify_password
from competency_engine.auth.rate_limiter import rate_limiter
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
from competency_engine.auth.tokens import (
    create_access_token,
    decode_access_token,
    generate_secure_token,
    hash_token,
)

__all__ = [
    # Password & Tokens
    "hash_password",
    "verify_password",
    "hash_token",
    "generate_secure_token",
    "create_access_token",
    "decode_access_token",
    # Service
    "AuthService",
    # Rate Limiter
    "rate_limiter",
    # Dependencies
    "get_current_user",
    "get_optional_current_user",
    "get_client_ip",
    "require_role",
    "require_employee_user",
    "require_admin_user",
    "require_staff_user",
    "get_employee_profile",
    "require_approved_employee",
    "get_admin_profile",
    "get_staff_profile",
    "is_within_admin_jurisdiction",
    # Schemas
    "EmployeeRegisterRequest",
    "LoginRequest",
    "RefreshTokenRequest",
    "EmailVerificationRequest",
    "PasswordResetRequest",
    "PasswordResetConfirmRequest",
    "AdminInviteRequest",
    "AdminAcceptInviteRequest",
    "DeactivateAccountRequest",
    "UserSummaryResponse",
    "TokenResponse",
    "MessageResponse",
    "ApplicationStatusResponse",
]

