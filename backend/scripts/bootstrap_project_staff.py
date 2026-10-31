"""
Secure First Project Staff Bootstrap Utility for SIH26101 Platform.
Implements the definitive bootstrap requirement from FINAL_ARCHITECTURE_PLAN_v2.7:
- No hardcoded credentials or default administrator accounts.
- No publicly accessible staff-registration endpoint.
- Reads credentials securely from CLI arguments, environment variables, or interactive prompt.
- Hashes password using Argon2id.
- Creates active Project Staff account and ProjectStaffProfile.
"""

from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path

# Setup paths for importing application modules
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import func, select
from competency_engine.auth.password import hash_password
from competency_engine.db import (
    AccountStatusEnum,
    AccountTypeEnum,
    ProjectStaffProfile,
    User,
    get_db,
    get_engine,
    get_session_factory,
)


def bootstrap_project_staff(
    email: str,
    full_name: str,
    password: str,
    staff_role: str = "Platform Lead",
) -> User:
    """Provision a new Project Staff user and profile."""
    norm_email = email.strip().lower()
    if not norm_email or "@" not in norm_email:
        raise ValueError("A valid email address is required.")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    engine = get_engine()
    session_factory = get_session_factory(engine)

    with session_factory() as db:
        existing_user = db.scalar(select(User).where(func.lower(User.email) == norm_email))
        if existing_user:
            raise ValueError(f"An account with email '{norm_email}' already exists.")

        hashed_pw = hash_password(password)

        staff_user = User(
            email=norm_email,
            hashed_password=hashed_pw,
            account_type=AccountTypeEnum.PROJECT_STAFF,
            account_status=AccountStatusEnum.ACTIVE,
            failed_login_attempts=0,
        )
        db.add(staff_user)
        db.flush()

        profile = ProjectStaffProfile(
            user_id=staff_user.id,
            full_name=full_name.strip(),
            staff_role=staff_role.strip(),
        )
        db.add(profile)
        db.commit()
        db.refresh(staff_user)

        return staff_user


def count_project_staff() -> int:
    """Return count of registered Project Staff members."""
    engine = get_engine()
    session_factory = get_session_factory(engine)
    with session_factory() as db:
        return db.scalar(
            select(func.count(User.id)).where(User.account_type == AccountTypeEnum.PROJECT_STAFF)
        ) or 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Secure Project Staff Bootstrap Utility for SIH26101")
    parser.add_argument("--email", help="Project staff email address", default=os.getenv("PROJECT_STAFF_EMAIL"))
    parser.add_argument("--name", help="Project staff full name", default=os.getenv("PROJECT_STAFF_NAME"))
    parser.add_argument("--role", help="Staff role title", default=os.getenv("PROJECT_STAFF_ROLE", "Platform Lead"))
    parser.add_argument("--password", help="Account password (or set PROJECT_STAFF_PASSWORD)", default=os.getenv("PROJECT_STAFF_PASSWORD"))
    parser.add_argument("--check-only", action="store_true", help="Check if staff is already provisioned")

    args = parser.parse_args()

    if args.check_only:
        count = count_project_staff()
        print(f"Total provisioned Project Staff accounts: {count}")
        sys.exit(0 if count > 0 else 1)

    email = args.email
    name = args.name
    role = args.role
    password = args.password

    # Interactive prompts if arguments are missing
    if not email:
        email = input("Enter Project Staff Email: ").strip()
    if not name:
        name = input("Enter Full Name: ").strip()
    if not password:
        password = getpass.getpass("Enter Secure Password (min 8 chars): ").strip()

    try:
        user = bootstrap_project_staff(
            email=email,
            full_name=name,
            password=password,
            staff_role=role,
        )
        print(f"[SUCCESS] Project Staff account provisioned successfully.")
        print(f"  User ID: {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Role: {role}")
        print(f"  Account Status: {user.account_status.value}")
    except Exception as e:
        print(f"[ERROR] Failed to bootstrap Project Staff: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

