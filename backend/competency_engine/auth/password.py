"""
Argon2id Password Hashing Module for SIH26101 Platform.
Strictly adheres to OWASP Password Storage Cheat Sheet standards:
- Type: Argon2id
- Memory Cost: 64 MB (65536 KiB)
- Time Cost: 2 iterations
- Parallelism: 1 lane/thread
- Hash Length: 32 bytes
Never logs passwords or stores plaintext.
"""

from __future__ import annotations

import argon2
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

# Configure Argon2id hasher with OWASP recommended baseline
_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=1,
    hash_len=32,
    type=argon2.Type.ID,
)


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using Argon2id."""
    if not plain_password:
        raise ValueError("Password cannot be empty.")
    if len(plain_password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    return _hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against an Argon2id hash.
    Returns True if valid, False otherwise.
    Never throws exceptions on invalid credentials or malformed hashes.
    """
    if not plain_password or not hashed_password:
        return False
    try:
        return _hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False
    except Exception:
        return False

