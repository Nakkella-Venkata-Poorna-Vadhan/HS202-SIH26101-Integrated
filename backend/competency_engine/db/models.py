"""
Complete SQLAlchemy 2.x Relational Models for SIH26101 Platform.
Implements the 23 relational tables, composite foreign keys, partial unique indexes,
and check constraints frozen in FINAL_ARCHITECTURE_PLAN_v2.7.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from competency_engine.db.base import Base
from competency_engine.db.enums import (
    AccountStatusEnum,
    AccountTypeEnum,
    AppStatusEnum,
    ApprovalStatusEnum,
    GeographicLevelEnum,
    RevocationAppealStatusEnum,
    RoutingSourceEnum,
    RoutingStatusEnum,
    VerificationOutcomeEnum,
)

# ---------------------------------------------------------------------------
# PostgreSQL ENUM Types matching schema
# ---------------------------------------------------------------------------
account_type_pg_enum = ENUM(AccountTypeEnum, name="account_type_enum", create_type=False)
account_status_pg_enum = ENUM(AccountStatusEnum, name="account_status_enum", create_type=False)
app_status_pg_enum = ENUM(AppStatusEnum, name="app_status_enum", create_type=False)
approval_status_pg_enum = ENUM(ApprovalStatusEnum, name="approval_status_enum", create_type=False)
geographic_level_pg_enum = ENUM(GeographicLevelEnum, name="geographic_level_enum", create_type=False)
routing_status_pg_enum = ENUM(RoutingStatusEnum, name="routing_status_enum", create_type=False)
routing_source_pg_enum = ENUM(RoutingSourceEnum, name="routing_source_enum", create_type=False)
verification_outcome_pg_enum = ENUM(VerificationOutcomeEnum, name="verification_outcome_enum", create_type=False)
revocation_appeal_status_pg_enum = ENUM(RevocationAppealStatusEnum, name="revocation_appeal_status_enum", create_type=False)

# ===========================================================================
# 1. Identity, Authentication & Administrative Invitations
# ===========================================================================

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("failed_login_attempts >= 0", name="chk_users_failed_login_attempts"),
        Index("idx_users_email", "email"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[AccountTypeEnum] = mapped_column(account_type_pg_enum, nullable=False)
    account_status: Mapped[AccountStatusEnum] = mapped_column(account_status_pg_enum, nullable=False, default=AccountStatusEnum.UNVERIFIED_EMAIL)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lockout_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_consumed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    consumed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        Index("idx_refresh_token_family", "family_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class AdminInvitation(Base):
    __tablename__ = "admin_invitations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    official_designation: Mapped[str] = mapped_column(String(255), nullable=False)
    authorized_scopes: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    created_by_staff_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_consumed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    consumed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

# ===========================================================================
# 2. Organizational Taxonomy & Geographic Hierarchy
# ===========================================================================

class OrgMinistry(Base):
    __tablename__ = "org_ministries"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class OrgDepartment(Base):
    __tablename__ = "org_departments"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    ministry_id: Mapped[str] = mapped_column(String(32), ForeignKey("org_ministries.id", ondelete="RESTRICT"), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class OrgCadre(Base):
    __tablename__ = "org_cadres"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    controlling_authority: Mapped[str] = mapped_column(String(255), nullable=False, default="MoSPI")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class OrgGradeBand(Base):
    __tablename__ = "org_grade_bands"
    __table_args__ = (
        CheckConstraint("hierarchical_rank >= 1", name="chk_grade_bands_hierarchical_rank"),
    )

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    hierarchical_rank: Mapped[int] = mapped_column(Integer, nullable=False)


class OrgDesignation(Base):
    __tablename__ = "org_designations"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    grade_band_id: Mapped[str] = mapped_column(String(32), ForeignKey("org_grade_bands.id", ondelete="RESTRICT"), nullable=False)
    cadre_id: Mapped[Optional[str]] = mapped_column(String(32), ForeignKey("org_cadres.id", ondelete="RESTRICT"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class OrgZone(Base):
    __tablename__ = "org_zones"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class OrgState(Base):
    __tablename__ = "org_states"
    __table_args__ = (
        UniqueConstraint("id", name="uq_state_id"),
    )

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    zone_id: Mapped[str] = mapped_column(String(32), ForeignKey("org_zones.id", ondelete="RESTRICT"), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(10), nullable=False)


class OrgLocation(Base):
    __tablename__ = "org_locations"
    __table_args__ = (
        UniqueConstraint("id", name="uq_location_id"),
        ForeignKeyConstraint(
            ["state_id", "zone_id"],
            ["org_states.id", "org_states.zone_id"],
            ondelete="RESTRICT",
            name="fk_org_locations_state_zone",
        ),
    )

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    state_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    zone_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    building_name: Mapped[str] = mapped_column(String(255), nullable=False)
    pin_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

# ===========================================================================
# 3. User Profiles & Scopes
# ===========================================================================

class AdministratorProfile(Base):
    __tablename__ = "administrator_profiles"
    __table_args__ = (
        CheckConstraint("max_managed_employees > 0", name="chk_admin_profiles_max_managed_employees"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    official_designation: Mapped[str] = mapped_column(String(255), nullable=False)
    max_managed_employees: Mapped[int] = mapped_column(Integer, nullable=False, default=200)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    scopes: Mapped[List["AdministratorScope"]] = relationship("AdministratorScope", back_populates="administrator", cascade="all, delete-orphan")


class AdministratorScope(Base):
    __tablename__ = "administrator_scopes"
    __table_args__ = (
        ForeignKeyConstraint(
            ["department_id", "ministry_id"],
            ["org_departments.id", "org_departments.ministry_id"],
            ondelete="RESTRICT",
            name="fk_admin_scopes_dept_ministry",
        ),
        ForeignKeyConstraint(
            ["zone_id"],
            ["org_zones.id"],
            ondelete="RESTRICT",
            name="fk_admin_scopes_zone",
        ),
        ForeignKeyConstraint(
            ["state_id", "zone_id"],
            ["org_states.id", "org_states.zone_id"],
            ondelete="RESTRICT",
            name="fk_admin_scopes_state_zone",
        ),
        ForeignKeyConstraint(
            ["location_id", "state_id", "zone_id"],
            ["org_locations.id", "org_locations.state_id", "org_locations.zone_id"],
            ondelete="RESTRICT",
            name="fk_admin_scopes_loc_state_zone",
        ),
        CheckConstraint(
            "(geographic_level = 'NATIONAL' AND zone_id IS NULL AND state_id IS NULL AND location_id IS NULL) OR " +
            "(geographic_level = 'ZONE'     AND zone_id IS NOT NULL AND state_id IS NULL AND location_id IS NULL) OR " +
            "(geographic_level = 'STATE'    AND zone_id IS NOT NULL AND state_id IS NOT NULL AND location_id IS NULL) OR " +
            "(geographic_level = 'STATION'  AND zone_id IS NOT NULL AND state_id IS NOT NULL AND location_id IS NOT NULL)",
            name="chk_geographic_level_integrity",
        ),
        UniqueConstraint(
            "admin_id",
            "ministry_id",
            "department_id",
            "cadre_id",
            "grade_band_id",
            "geographic_level",
            "zone_id",
            "state_id",
            "location_id",
            name="uq_admin_scope_unique",
            postgresql_nulls_not_distinct=True,
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    admin_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("administrator_profiles.id", ondelete="CASCADE"), nullable=False)
    ministry_id: Mapped[str] = mapped_column(String(32), ForeignKey("org_ministries.id", ondelete="RESTRICT"), nullable=False)
    department_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    cadre_id: Mapped[Optional[str]] = mapped_column(String(32), ForeignKey("org_cadres.id", ondelete="RESTRICT"), nullable=True)
    grade_band_id: Mapped[Optional[str]] = mapped_column(String(32), ForeignKey("org_grade_bands.id", ondelete="RESTRICT"), nullable=True)
    geographic_level: Mapped[GeographicLevelEnum] = mapped_column(geographic_level_pg_enum, nullable=False)
    zone_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    state_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    location_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    administrator: Mapped["AdministratorProfile"] = relationship("AdministratorProfile", back_populates="scopes")


class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"
    __table_args__ = (
        ForeignKeyConstraint(
            ["department_id", "ministry_id"],
            ["org_departments.id", "org_departments.ministry_id"],
            ondelete="RESTRICT",
            name="fk_employee_dept_ministry",
        ),
        CheckConstraint("experience_years >= 0.0", name="chk_employee_profiles_experience_years"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), unique=True, nullable=False)
    employee_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    ministry_id: Mapped[str] = mapped_column(String(32), nullable=False)
    department_id: Mapped[str] = mapped_column(String(32), nullable=False)
    cadre_id: Mapped[str] = mapped_column(String(32), ForeignKey("org_cadres.id", ondelete="RESTRICT"), nullable=False)
    location_id: Mapped[str] = mapped_column(String(32), ForeignKey("org_locations.id", ondelete="RESTRICT"), nullable=False)
    designation_id: Mapped[str] = mapped_column(String(32), ForeignKey("org_designations.id", ondelete="RESTRICT"), nullable=False)
    experience_years: Mapped[Decimal] = mapped_column(Numeric(4, 1), nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    self_declared_skills: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    supporting_document_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    approval_status: Mapped[ApprovalStatusEnum] = mapped_column(approval_status_pg_enum, nullable=False, default=ApprovalStatusEnum.UNAPPROVED)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by_admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("administrator_profiles.id", ondelete="RESTRICT"), nullable=True)
    revoked_by_staff_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class ProjectStaffProfile(Base):
    __tablename__ = "project_staff_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    staff_role: Mapped[str] = mapped_column(String(100), nullable=False, default="Platform Lead")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


# ===========================================================================
# 4. Versioned Applications & Routing Lifecycle
# ===========================================================================

class EmployeeApplication(Base):
    __tablename__ = "employee_applications"
    __table_args__ = (
        UniqueConstraint("id", "employee_id", name="uq_app_id_employee"),
        UniqueConstraint("employee_id", "submission_number", name="uq_employee_submission"),
        CheckConstraint("submission_number >= 1", name="chk_employee_applications_submission_number"),
        CheckConstraint("parent_application_id IS NULL OR parent_application_id != id", name="chk_no_self_parent"),
        ForeignKeyConstraint(
            ["parent_application_id", "employee_id"],
            ["employee_applications.id", "employee_applications.employee_id"],
            ondelete="RESTRICT",
            name="fk_emp_apps_parent_employee",
        ),
        Index(
            "uq_single_pending_application_per_employee",
            "employee_id",
            unique=True,
            postgresql_where=text("status IN ('SUBMITTED', 'ROUTED_PENDING_REVIEW', 'EVIDENCE_REQUESTED', 'ESCALATED_UNMATCHED')"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employee_profiles.id", ondelete="RESTRICT"), nullable=False)
    submission_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parent_application_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[AppStatusEnum] = mapped_column(app_status_pg_enum, nullable=False, default=AppStatusEnum.SUBMITTED)
    decision_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by_admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("administrator_profiles.id", ondelete="RESTRICT"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class ApplicationRoutingHistory(Base):
    __tablename__ = "application_routing_history"
    __table_args__ = (
        CheckConstraint("match_score >= 0.0 AND match_score <= 100.0", name="chk_routing_match_score"),
        Index("idx_routing_app_admin", "application_id", "admin_id"),
        Index("idx_routing_active", "admin_id", "routing_status", postgresql_where=text("routing_status = 'ACTIVE'")),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    application_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employee_applications.id", ondelete="RESTRICT"), nullable=False)
    admin_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("administrator_profiles.id", ondelete="RESTRICT"), nullable=False)
    routing_source: Mapped[RoutingSourceEnum] = mapped_column(routing_source_pg_enum, nullable=False, default=RoutingSourceEnum.AUTOMATIC_MATCH)
    routing_status: Mapped[RoutingStatusEnum] = mapped_column(routing_status_pg_enum, nullable=False, default=RoutingStatusEnum.ACTIVE)
    match_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    match_explanation: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    routed_by_actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    staff_justification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    routed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

# ===========================================================================
# 5. Field-Level Verification History
# ===========================================================================

class ApplicationFieldVerification(Base):
    __tablename__ = "application_field_verifications"
    __table_args__ = (
        ForeignKeyConstraint(
            ["application_id", "employee_id"],
            ["employee_applications.id", "employee_applications.employee_id"],
            ondelete="RESTRICT",
            name="fk_field_verif_app_emp",
        ),
        CheckConstraint("attempt_number >= 1", name="chk_field_verifications_attempt_number"),
        UniqueConstraint("application_id", "field_name", "attempt_number", name="uq_app_field_attempt"),
        Index("idx_verifications_app", "application_id"),
        Index("uq_app_field_latest", "application_id", "field_name", unique=True, postgresql_where=text("is_latest = TRUE")),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    application_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    field_name: Mapped[str] = mapped_column(String(64), nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_latest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    employee_submitted_value: Mapped[Any] = mapped_column(JSONB, nullable=False)
    admin_verified_value: Mapped[Any] = mapped_column(JSONB, nullable=False)
    evidence_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    verification_outcome: Mapped[VerificationOutcomeEnum] = mapped_column(verification_outcome_pg_enum, nullable=False)
    reviewing_admin_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("administrator_profiles.id", ondelete="RESTRICT"), nullable=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


# ===========================================================================
# 6. Approval Revocation Grievance Appeals
# ===========================================================================

class ApprovalRevocationAppeal(Base):
    __tablename__ = "approval_revocation_appeals"
    __table_args__ = (
        CheckConstraint(
            "reviewed_by_staff_id IS NULL OR reviewed_by_staff_id != revoked_by_staff_id",
            name="chk_appeal_independent_reviewer",
        ),
        Index("idx_revocation_appeals_emp", "employee_id"),
        Index("uq_single_pending_revocation_appeal", "employee_id", unique=True, postgresql_where=text("status = 'PENDING_REVIEW'")),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employee_profiles.id", ondelete="RESTRICT"), nullable=False)
    revoked_by_staff_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    appeal_reason: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_document_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[RevocationAppealStatusEnum] = mapped_column(
        revocation_appeal_status_pg_enum, nullable=False, default=RevocationAppealStatusEnum.PENDING_REVIEW
    )
    reviewed_by_staff_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    decision_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


# ===========================================================================
# 7. Active Management Assignments
# ===========================================================================

class AdminEmployeeAssignment(Base):
    __tablename__ = "admin_employee_assignments"
    __table_args__ = (
        Index("uq_single_active_assignment_per_employee", "employee_id", unique=True, postgresql_where=text("is_active = TRUE")),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    admin_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("administrator_profiles.id", ondelete="RESTRICT"), nullable=False)
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employee_profiles.id", ondelete="RESTRICT"), nullable=False)
    assignment_source: Mapped[str] = mapped_column(String(50), nullable=False, default="ADMIN_ACCEPTANCE")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revocation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


# ===========================================================================
# 8. Document Encryption & Retention Vault Registry
# ===========================================================================

class EmployeeDocument(Base):
    __tablename__ = "employee_documents"
    __table_args__ = (
        CheckConstraint("file_size_bytes > 0 AND file_size_bytes <= 5242880", name="chk_documents_file_size"),
        Index("idx_docs_employee", "employee_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employee_profiles.id", ondelete="RESTRICT"), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    vault_storage_path: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    kek_version: Mapped[str] = mapped_column(String(32), nullable=False, default="v1")
    encrypted_dek_b64: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    iv_nonce_b64: Mapped[str] = mapped_column(Text, nullable=False)
    auth_tag_b64: Mapped[str] = mapped_column(Text, nullable=False)
    is_legal_hold: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    retention_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


# ===========================================================================
# 9. Append-Only Audit Trail
# ===========================================================================

class ApplicationAuditLog(Base):
    __tablename__ = "application_audit_logs"
    __table_args__ = (
        Index("idx_audit_application", "application_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    application_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("employee_applications.id", ondelete="RESTRICT"), nullable=True)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    actor_email: Mapped[str] = mapped_column(String(255), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(30), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    previous_state: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    new_state: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())