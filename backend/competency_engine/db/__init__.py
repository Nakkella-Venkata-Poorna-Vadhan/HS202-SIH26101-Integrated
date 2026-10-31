"""
Database Package for SIH26101 Platform.
Exposes Base metadata, session lifecycle dependencies, enumerations, and typed models.
"""

from competency_engine.db.base import Base, metadata
from competency_engine.db.config import db_settings
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
from competency_engine.db.models import (
    AdminEmployeeAssignment,
    AdminInvitation,
    AdministratorProfile,
    AdministratorScope,
    ApplicationAuditLog,
    ApplicationFieldVerification,
    ApplicationRoutingHistory,
    ApprovalRevocationAppeal,
    EmailVerification,
    EmployeeApplication,
    EmployeeDocument,
    EmployeeProfile,
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
)
from competency_engine.db.session import (
    audit_session_scope,
    check_db_health,
    db_session_scope,
    get_audit_db,
    get_db,
    get_engine,
    get_session_factory,
)

__all__ = [
    # Base
    "Base",
    "metadata",
    # Config & Session
    "db_settings",
    "get_engine",
    "get_session_factory",
    "get_db",
    "get_audit_db",
    "db_session_scope",
    "audit_session_scope",
    "check_db_health",
    # Enums
    "AccountTypeEnum",
    "AccountStatusEnum",
    "AppStatusEnum",
    "ApprovalStatusEnum",
    "GeographicLevelEnum",
    "RoutingStatusEnum",
    "RoutingSourceEnum",
    "VerificationOutcomeEnum",
    "RevocationAppealStatusEnum",
    # Models
    "User",
    "EmailVerification",
    "RefreshToken",
    "AdminInvitation",
    "OrgMinistry",
    "OrgDepartment",
    "OrgCadre",
    "OrgGradeBand",
    "OrgDesignation",
    "OrgZone",
    "OrgState",
    "OrgLocation",
    "EmployeeProfile",
    "AdministratorProfile",
    "AdministratorScope",
    "ProjectStaffProfile",
    "EmployeeApplication",
    "ApplicationRoutingHistory",
    "ApplicationFieldVerification",
    "ApprovalRevocationAppeal",
    "AdminEmployeeAssignment",
    "EmployeeDocument",
    "ApplicationAuditLog",
]