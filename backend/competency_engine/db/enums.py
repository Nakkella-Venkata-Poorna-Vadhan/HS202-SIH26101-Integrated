"""
Database Enumerations for SIH26101 Platform.
Reflects frozen PostgreSQL enum definitions from FINAL_ARCHITECTURE_PLAN_v2.7.
"""

from __future__ import annotations

import enum


class AccountTypeEnum(str, enum.Enum):
    """User account type hierarchy."""
    EMPLOYEE = "EMPLOYEE"
    ADMINISTRATOR = "ADMINISTRATOR"
    PROJECT_STAFF = "PROJECT_STAFF"


class AccountStatusEnum(str, enum.Enum):
    """Lifecycle status of a user login account."""
    UNVERIFIED_EMAIL = "UNVERIFIED_EMAIL"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DEACTIVATED = "DEACTIVATED"


class AppStatusEnum(str, enum.Enum):
    """Lifecycle status of an individual employee application submission."""
    SUBMITTED = "SUBMITTED"
    ROUTED_PENDING_REVIEW = "ROUTED_PENDING_REVIEW"
    EVIDENCE_REQUESTED = "EVIDENCE_REQUESTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    ESCALATED_UNMATCHED = "ESCALATED_UNMATCHED"


class ApprovalStatusEnum(str, enum.Enum):
    """Long-lived official platform approval status of an employee profile."""
    UNAPPROVED = "UNAPPROVED"
    APPROVED = "APPROVED"
    REVOKED = "REVOKED"


class GeographicLevelEnum(str, enum.Enum):
    """Geographic authority tiers for administrator scope enforcement."""
    NATIONAL = "NATIONAL"
    ZONE = "ZONE"
    STATE = "STATE"
    STATION = "STATION"


class RoutingStatusEnum(str, enum.Enum):
    """Status of an application routing proposal to an administrator."""
    ACTIVE = "ACTIVE"
    DECLINED_BY_ADMIN = "DECLINED_BY_ADMIN"
    SUPERSEDED = "SUPERSEDED"
    WITHDRAWN = "WITHDRAWN"
    COMPLETED_ACCEPTED = "COMPLETED_ACCEPTED"
    COMPLETED_REJECTED = "COMPLETED_REJECTED"


class RoutingSourceEnum(str, enum.Enum):
    """Origin mechanism for application-to-administrator routing."""
    AUTOMATIC_MATCH = "AUTOMATIC_MATCH"
    STAFF_MANUAL_ROUTE = "STAFF_MANUAL_ROUTE"
    STAFF_REASSIGNMENT = "STAFF_REASSIGNMENT"


class VerificationOutcomeEnum(str, enum.Enum):
    """Field-level verification result recorded by reviewing administrator."""
    VERIFIED_MATCH = "VERIFIED_MATCH"
    VERIFIED_CORRECTED = "VERIFIED_CORRECTED"
    DISCREPANCY_FLAGGED = "DISCREPANCY_FLAGGED"
    UNVERIFIABLE = "UNVERIFIABLE"


class RevocationAppealStatusEnum(str, enum.Enum):
    """Status of an employee grievance appeal against an administrative revocation."""
    PENDING_REVIEW = "PENDING_REVIEW"
    APPEAL_ALLOWED_REINSTATED = "APPEAL_ALLOWED_REINSTATED"
    APPEAL_DISMISSED_CONFIRMED = "APPEAL_DISMISSED_CONFIRMED"