"""
Cryptographic Token & JWT Management Module for SIH26101 Platform.
Implements:
1. Short-lived JWT Access Tokens (15-minute default validity).
2. Opaque, high-entropy single-use tokens for refresh, email verification, password reset, and invitations.
3. Cryptographic token hashing via SHA-256 for secure database persistence.
4. Token verification and claims validation with fail-fast security.
"""

from __future__ import annotations

import hashlib
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt

# JWT configuration defaults
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
EMAIL_VERIFICATION_EXPIRE_HOURS = 24
PASSWORD_RESET_EXPIRE_HOURS = 1
ADMIN_INVITATION_EXPIRE_HOURS = 72

ALGORITHM = "HS256"
JWT_ISSUER = "sih26101:auth"
JWT_AUDIENCE = "sih26101:api"


def get_jwt_secret() -> str:
    """Retrieve JWT secret key from environment or fail fast."""
    secret = os.getenv("JWT_SECRET_KEY")
    if not secret or len(secret) < 32:
        raise ValueError(
            "JWT_SECRET_KEY environment variable is not configured or too short (minimum 32 characters required)."
        )
    return secret


def hash_token(raw_token: str) -> str:
    """
    Compute deterministic SHA-256 hex digest of an opaque token.
    Only token hashes are stored in the database.
    """
    if not raw_token:
        raise ValueError("Cannot hash an empty token.")
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def generate_secure_token(nbytes: int = 32) -> str:
    """Generate high-entropy URL-safe cryptographic token."""
    return secrets.token_urlsafe(nbytes)


def create_access_token(
    user_id: str,
    email: str,
    account_type: str,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Issue short-lived signed JWT access token.
    Claims:
    - sub: user_id (UUID string)
    - email: user email
    - account_type: EMPLOYEE | ADMINISTRATOR | PROJECT_STAFF
    - iat: issued at timestamp
    - exp: expiration timestamp
    - jti: unique token identifier
    """
    secret = get_jwt_secret()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "email": email,
        "account_type": account_type,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": str(uuid.uuid4()),
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.
    Raises ValueError on invalid signature, expiration, audience, issuer, or malformed claims.
    """
    secret = get_jwt_secret()
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
            options={
                "verify_exp": True,
                "verify_sub": True,
                "verify_iss": True,
                "verify_aud": True,
            },
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid or expired access token: {e}") from e

