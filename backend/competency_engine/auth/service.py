"""
Core Authentication and Identity Service for SIH26101 Platform.
Implements the definitive state machines, token lifecycle, role isolation,
and security controls from FINAL_ARCHITECTURE_PLAN_v2.7.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from competency_engine.auth.password import hash_password, verify_password
from competency_engine.auth.rate_limiter import (
    calculate_new_lockout,
    is_user_locked_out,
    rate_limiter,
)
from competency_engine.auth.schemas import (
    AdminAcceptInviteRequest,
    AdminInviteRequest,
    EmployeeRegisterRequest,
)
from competency_engine.auth.tokens import (
    ADMIN_INVITATION_EXPIRE_HOURS,
    EMAIL_VERIFICATION_EXPIRE_HOURS,
    PASSWORD_RESET_EXPIRE_HOURS,
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    generate_secure_token,
    hash_token,
)
from competency_engine.db import (
    AccountStatusEnum,
    AccountTypeEnum,
    AdminInvitation,
    AdministratorProfile,
    AdministratorScope,
    AppStatusEnum,
    ApprovalStatusEnum,
    EmailVerification,
    EmployeeApplication,
    EmployeeProfile,
    GeographicLevelEnum,
    PasswordResetToken,
    ProjectStaffProfile,
    RefreshToken,
    User,
)
from competency_engine.email_service import get_email_service


class AuthService:
    """Authentication and identity lifecycle manager."""

    @staticmethod
    def register_employee(
        db: Session,
        req: EmployeeRegisterRequest,
        client_ip: str,
    ) -> Tuple[User, str]:
        """
        Public self-registration for Civil Service Employees.
        - Checks IP rate limits.
        - Ensures email and employee_code uniqueness.
        - Creates User in UNVERIFIED_EMAIL status.
        - Creates EmployeeProfile in UNAPPROVED status.
        - Creates Initial EmployeeApplication in SUBMITTED status.
        - Generates email verification token and dispatches email.
        """
        allowed, retry_after = rate_limiter.is_allowed("register", client_ip)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many registration attempts. Please retry in {retry_after} seconds.",
            )

        norm_email = req.email.strip().lower()

        # Check existing user email
        existing_user = db.scalar(select(User).where(func.lower(User.email) == norm_email))
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An account with email '{norm_email}' already exists.",
            )

        # Check existing employee code
        existing_code = db.scalar(select(EmployeeProfile).where(EmployeeProfile.employee_code == req.employee_code.strip()))
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee code '{req.employee_code}' is already registered.",
            )

        # Validate organizational references exist
        from competency_engine.db.models import OrgDepartment, OrgMinistry, OrgLocation, OrgCadre, OrgDesignation
        ministry = db.scalar(select(OrgMinistry).where(OrgMinistry.id == req.ministry_id))
        if not ministry:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Referenced ministry ID '{req.ministry_id}' does not exist.",
            )
        department = db.scalar(select(OrgDepartment).where(OrgDepartment.id == req.department_id))
        if not department:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Referenced department ID '{req.department_id}' does not exist.",
            )
        cadre = db.scalar(select(OrgCadre).where(OrgCadre.id == req.cadre_id))
        if not cadre:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Referenced cadre ID '{req.cadre_id}' does not exist.",
            )
        location = db.scalar(select(OrgLocation).where(OrgLocation.id == req.location_id))
        if not location:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Referenced location ID '{req.location_id}' does not exist.",
            )
        designation = db.scalar(select(OrgDesignation).where(OrgDesignation.id == req.designation_id))
        if not designation:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Referenced designation ID '{req.designation_id}' does not exist.",
            )

        # Hash password with Argon2id
        hashed_pw = hash_password(req.password)

        user = User(
            email=norm_email,
            hashed_password=hashed_pw,
            account_type=AccountTypeEnum.EMPLOYEE,
            account_status=AccountStatusEnum.UNVERIFIED_EMAIL,
            failed_login_attempts=0,
        )
        db.add(user)
        db.flush()

        # Create unapproved employee profile
        profile = EmployeeProfile(
            user_id=user.id,
            employee_code=req.employee_code.strip(),
            full_name=req.full_name.strip(),
            ministry_id=req.ministry_id,
            department_id=req.department_id,
            cadre_id=req.cadre_id,
            location_id=req.location_id,
            designation_id=req.designation_id,
            experience_years=Decimal(str(req.experience_years)),
            phone_number=req.phone_number.strip() if req.phone_number else None,
            self_declared_skills=req.self_declared_skills,
            supporting_document_path=req.supporting_document_path,
            approval_status=ApprovalStatusEnum.UNAPPROVED,
        )
        db.add(profile)
        db.flush()

        # Create initial onboarding application (submission_number = 1)
        app_record = EmployeeApplication(
            employee_id=profile.id,
            submission_number=1,
            status=AppStatusEnum.SUBMITTED,
        )
        db.add(app_record)

        # Generate single-use verification token
        raw_token = generate_secure_token(32)
        token_digest = hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=EMAIL_VERIFICATION_EXPIRE_HOURS)

        verification_record = EmailVerification(
            user_id=user.id,
            token_hash=token_digest,
            expires_at=expires_at,
            is_consumed=False,
        )
        db.add(verification_record)
        db.commit()

        # Dispatch verification email via delivery abstraction
        email_service = get_email_service()
        email_service.send_verification_email(
            to_email=norm_email,
            token=raw_token,
            user_name=req.full_name,
        )

        return user, raw_token

    @staticmethod
    def verify_email(db: Session, raw_token: str, client_ip: str) -> User:
        """
        Verify single-use email token and transition account to ACTIVE.
        """
        allowed, retry_after = rate_limiter.is_allowed("verify_email", client_ip)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please retry in {retry_after} seconds.",
            )

        token_digest = hash_token(raw_token.strip())
        record = db.scalar(
            select(EmailVerification).where(EmailVerification.token_hash == token_digest)
        )
        if not record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or unrecognized verification token.",
            )

        if record.is_consumed:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Verification token has already been consumed.",
            )

        now = datetime.now(timezone.utc)
        record_expires = record.expires_at
        if record_expires.tzinfo is None:
            record_expires = record_expires.replace(tzinfo=timezone.utc)

        if record_expires < now:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Verification token has expired. Please request a new verification email.",
            )

        user = db.scalar(select(User).where(User.id == record.user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated user account not found.",
            )

        record.is_consumed = True
        record.consumed_at = now
        user.account_status = AccountStatusEnum.ACTIVE
        user.updated_at = now

        db.commit()
        return user

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str,
        client_ip: str,
    ) -> Tuple[User, str, str]:
        """
        Authenticate user with Argon2id, lockout protection, and JWT/refresh issuance.
        Returns: (user, access_token, refresh_token)
        """
        allowed, retry_after = rate_limiter.is_allowed("login", client_ip)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many login attempts. Please wait {retry_after} seconds before retrying.",
            )

        norm_email = email.strip().lower()
        user = db.scalar(select(User).where(func.lower(User.email) == norm_email))

        # Check account lockout before verifying password
        if user and is_user_locked_out(user.lockout_until):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is temporarily locked due to multiple failed login attempts. Please retry later or reset your password.",
            )

        if not user or not verify_password(password, user.hashed_password):
            if user:
                new_attempts, lockout_time = calculate_new_lockout(user.failed_login_attempts)
                user.failed_login_attempts = new_attempts
                user.lockout_until = lockout_time
                db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        # Check account status
        if user.account_status == AccountStatusEnum.UNVERIFIED_EMAIL:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email address has not been verified. Please verify your email before logging in.",
            )
        if user.account_status == AccountStatusEnum.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been suspended by project administration.",
            )
        if user.account_status == AccountStatusEnum.DEACTIVATED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated.",
            )

        # Successful login: reset failed login attempts
        user.failed_login_attempts = 0
        user.lockout_until = None

        # Issue access token
        access_token = create_access_token(
            user_id=str(user.id),
            email=user.email,
            account_type=user.account_type.value,
        )

        # Issue refresh token with a new family_id
        raw_refresh_token = generate_secure_token(32)
        family_id = uuid.uuid4()
        token_digest = hash_token(raw_refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=token_digest,
            family_id=family_id,
            is_revoked=False,
            expires_at=expires_at,
        )
        db.add(refresh_record)
        db.commit()

        return user, access_token, raw_refresh_token

    @staticmethod
    def rotate_refresh_token(
        db: Session,
        raw_refresh_token: str,
        client_ip: str,
    ) -> Tuple[User, str, str]:
        """
        Refresh token rotation with reuse detection.
        - If token is revoked: REUSE DETECTED! Invalidate all tokens in family.
        - If valid: Revoke current token, issue new token in same family.
        """
        token_digest = hash_token(raw_refresh_token.strip())
        record = db.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == token_digest)
        )
        if not record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or unrecognized refresh token.",
            )

        # REUSE DETECTION: if token is already revoked, attack or reuse is suspected
        if record.is_revoked:
            # Revoke entire token family
            db.execute(
                update(RefreshToken)
                .where(RefreshToken.family_id == record.family_id)
                .values(is_revoked=True)
            )
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Revoked refresh token reuse detected. All sessions in this token family have been invalidated.",
            )

        now = datetime.now(timezone.utc)
        record_expires = record.expires_at
        if record_expires.tzinfo is None:
            record_expires = record_expires.replace(tzinfo=timezone.utc)

        if record_expires < now:
            record.is_revoked = True
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired. Please log in again.",
            )

        user = db.scalar(select(User).where(User.id == record.user_id))
        if not user or user.account_status != AccountStatusEnum.ACTIVE:
            record.is_revoked = True
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Associated user account is not active.",
            )

        # Revoke current token
        record.is_revoked = True

        # Issue new refresh token within SAME family
        new_raw_refresh = generate_secure_token(32)
        new_token_digest = hash_token(new_raw_refresh)
        new_expires_at = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        new_record = RefreshToken(
            user_id=user.id,
            token_hash=new_token_digest,
            family_id=record.family_id,
            is_revoked=False,
            expires_at=new_expires_at,
        )
        db.add(new_record)

        # Issue new access token
        new_access_token = create_access_token(
            user_id=str(user.id),
            email=user.email,
            account_type=user.account_type.value,
        )

        db.commit()
        return user, new_access_token, new_raw_refresh

    @staticmethod
    def logout(db: Session, user_id: uuid.UUID, raw_refresh_token: Optional[str] = None) -> None:
        """
        Revoke user refresh tokens.
        If a specific token is given, revokes its family; otherwise revokes all tokens for user.
        """
        if raw_refresh_token:
            token_digest = hash_token(raw_refresh_token.strip())
            record = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_digest))
            if record:
                db.execute(
                    update(RefreshToken)
                    .where(RefreshToken.family_id == record.family_id)
                    .values(is_revoked=True)
                )
        else:
            db.execute(
                update(RefreshToken)
                .where(RefreshToken.user_id == user_id)
                .values(is_revoked=True)
            )
        db.commit()

    @staticmethod
    def request_password_reset(db: Session, email: str, client_ip: str) -> bool:
        """
        Generate password reset token and dispatch email.
        Timing-safe and enumeration-safe: always returns True.
        """
        allowed, retry_after = rate_limiter.is_allowed("password_reset", client_ip)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many password reset requests. Please retry in {retry_after} seconds.",
            )

        norm_email = email.strip().lower()
        user = db.scalar(select(User).where(func.lower(User.email) == norm_email))

        if user and user.account_status in (AccountStatusEnum.ACTIVE, AccountStatusEnum.UNVERIFIED_EMAIL):
            raw_token = generate_secure_token(32)
            token_digest = hash_token(raw_token)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=PASSWORD_RESET_EXPIRE_HOURS)

            reset_record = PasswordResetToken(
                user_id=user.id,
                token_hash=token_digest,
                expires_at=expires_at,
                is_consumed=False,
            )
            db.add(reset_record)
            db.commit()

            email_service = get_email_service()
            email_service.send_password_reset_email(to_email=norm_email, token=raw_token)

        return True

    @staticmethod
    def confirm_password_reset(
        db: Session,
        raw_token: str,
        new_password: str,
        client_ip: str,
    ) -> User:
        """
        Verify password reset token, update password with Argon2id, and revoke existing sessions.
        """
        token_digest = hash_token(raw_token.strip())
        record = db.scalar(
            select(PasswordResetToken).where(PasswordResetToken.token_hash == token_digest)
        )
        if not record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or unrecognized password reset token.",
            )

        if record.is_consumed:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Password reset token has already been consumed.",
            )

        now = datetime.now(timezone.utc)
        record_expires = record.expires_at
        if record_expires.tzinfo is None:
            record_expires = record_expires.replace(tzinfo=timezone.utc)

        if record_expires < now:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Password reset token has expired.",
            )

        user = db.scalar(select(User).where(User.id == record.user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated user account not found.",
            )

        # Update password
        user.hashed_password = hash_password(new_password)
        user.failed_login_attempts = 0
        user.lockout_until = None
        user.updated_at = now

        # Consume token
        record.is_consumed = True
        record.consumed_at = now

        # Invalidate all existing refresh tokens for security
        db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user.id)
            .values(is_revoked=True)
        )

        db.commit()
        return user

    @staticmethod
    def invite_administrator(
        db: Session,
        staff_user: User,
        req: AdminInviteRequest,
    ) -> Tuple[AdminInvitation, str]:
        """
        Project Staff creates a single-use administrator invitation token (72-hour validity).
        Strictly enforces that only Project Staff can invite administrators.
        """
        if staff_user.account_type != AccountTypeEnum.PROJECT_STAFF:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only authorized Project Staff may invite new administrators.",
            )

        norm_email = req.email.strip().lower()

        # Check existing active user with this email
        existing_user = db.scalar(select(User).where(func.lower(User.email) == norm_email))
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An account with email '{norm_email}' already exists.",
            )

        raw_token = generate_secure_token(32)
        token_digest = hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=ADMIN_INVITATION_EXPIRE_HOURS)

        invitation = AdminInvitation(
            email=norm_email,
            token_hash=token_digest,
            official_designation=req.official_designation.strip(),
            authorized_scopes=req.authorized_scopes,
            created_by_staff_id=staff_user.id,
            expires_at=expires_at,
            is_consumed=False,
        )
        db.add(invitation)
        db.commit()

        email_service = get_email_service()
        email_service.send_admin_invitation_email(
            to_email=norm_email,
            token=raw_token,
            designation=req.official_designation,
            scopes=req.authorized_scopes,
        )

        return invitation, raw_token

    @staticmethod
    def accept_admin_invite(
        db: Session,
        req: AdminAcceptInviteRequest,
        client_ip: str,
    ) -> Tuple[User, str, str]:
        """
        Activate Administrator account from single-use invitation.
        - Sets admin's own password with Argon2id.
        - Creates User as ADMINISTRATOR / ACTIVE.
        - Creates AdministratorProfile.
        - Unpacks authorized scopes into AdministratorScope records.
        - Consumes invitation.
        - Issues initial access and refresh tokens.
        """
        token_digest = hash_token(req.token.strip())
        invitation = db.scalar(
            select(AdminInvitation).where(AdminInvitation.token_hash == token_digest)
        )
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or unrecognized administrator invitation token.",
            )

        if invitation.is_consumed:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Invitation token has already been consumed.",
            )

        now = datetime.now(timezone.utc)
        inv_expires = invitation.expires_at
        if inv_expires.tzinfo is None:
            inv_expires = inv_expires.replace(tzinfo=timezone.utc)

        if inv_expires < now:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Administrator invitation token has expired.",
            )

        # Check existing user
        existing_user = db.scalar(select(User).where(func.lower(User.email) == invitation.email.lower()))
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An account with email '{invitation.email}' already exists.",
            )

        # Create active administrator user
        hashed_pw = hash_password(req.password)
        user = User(
            email=invitation.email.lower(),
            hashed_password=hashed_pw,
            account_type=AccountTypeEnum.ADMINISTRATOR,
            account_status=AccountStatusEnum.ACTIVE,
            failed_login_attempts=0,
        )
        db.add(user)
        db.flush()

        # Create AdministratorProfile
        profile = AdministratorProfile(
            user_id=user.id,
            full_name=req.full_name.strip(),
            official_designation=invitation.official_designation,
            max_managed_employees=200,
            is_active=True,
        )
        db.add(profile)
        db.flush()

        # Unpack scopes
        for scope_def in invitation.authorized_scopes:
            geo_str = scope_def.get("geographic_level", "NATIONAL").upper()
            try:
                geo_level = GeographicLevelEnum(geo_str)
            except ValueError:
                geo_level = GeographicLevelEnum.NATIONAL

            scope_record = AdministratorScope(
                admin_id=profile.id,
                ministry_id=scope_def.get("ministry_id", "MIN_MOSPI"),
                department_id=scope_def.get("department_id"),
                cadre_id=scope_def.get("cadre_id"),
                grade_band_id=scope_def.get("grade_band_id"),
                geographic_level=geo_level,
                zone_id=scope_def.get("zone_id"),
                state_id=scope_def.get("state_id"),
                location_id=scope_def.get("location_id"),
            )
            db.add(scope_record)

        # Mark invitation consumed
        invitation.is_consumed = True
        invitation.consumed_at = now

        # Issue tokens
        access_token = create_access_token(
            user_id=str(user.id),
            email=user.email,
            account_type=user.account_type.value,
        )

        raw_refresh_token = generate_secure_token(32)
        refresh_digest = hash_token(raw_refresh_token)
        refresh_expires = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=refresh_digest,
            family_id=uuid.uuid4(),
            is_revoked=False,
            expires_at=refresh_expires,
        )
        db.add(refresh_record)

        db.commit()
        return user, access_token, raw_refresh_token

    @staticmethod
    def deactivate_account(db: Session, user: User, password: str) -> None:
        """
        Deactivate an employee account after password confirmation.
        Revokes all refresh tokens and marks account DEACTIVATED.
        """
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password confirmation.",
            )

        user.account_status = AccountStatusEnum.DEACTIVATED
        user.updated_at = datetime.now(timezone.utc)

        db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user.id)
            .values(is_revoked=True)
        )
        db.commit()

