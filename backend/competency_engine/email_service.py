"""
Email Delivery Abstraction for SIH26101 Platform.
Supports:
1. Development/test email adapter: In-memory store and safe local logging; no external dependencies.
2. Production SMTP adapter: Configured via environment variables with STARTTLS / SSL support.
3. Templates for:
   - Email verification
   - Administrator invitation
   - Password reset
Never exposes tokens in public API responses.
"""

from __future__ import annotations

import abc
import os
import smtplib
from email.message import EmailMessage
from typing import Any, Dict, List, Optional


class BaseEmailService(abc.ABC):
    """Abstract base class for email delivery."""

    @abc.abstractmethod
    def send_email(
        self,
        to_email: str,
        subject: str,
        text_body: str,
        html_body: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send an email."""
        raise NotImplementedError

    def send_verification_email(
        self,
        to_email: str,
        token: str,
        user_name: Optional[str] = None,
    ) -> bool:
        """Send account email verification message."""
        greeting = f"Dear {user_name}," if user_name else "Dear Civil Service Colleague,"
        subject = "SIH26101 Platform — Verify Your Email Address"
        text_body = f"""{greeting}

Thank you for registering on the Official Statistics Competency Intelligence and Adaptive Learning Platform.

Please use the following verification code/token to verify your email address:
Token: {token}

This verification link/token will expire in 24 hours.

If you did not register for this platform, please ignore this email.

Ministry of Statistics and Programme Implementation (MoSPI)
Government of India
"""
        html_body = f"""<html>
<body>
    <p>{greeting}</p>
    <p>Thank you for registering on the <strong>Official Statistics Competency Intelligence and Adaptive Learning Platform</strong>.</p>
    <p>Please use the following single-use verification token to activate your account:</p>
    <p style="font-size: 18px; font-family: monospace; background: #f1f5f9; padding: 10px; border-radius: 4px; display: inline-block;">
        {token}
    </p>
    <p>This token will expire in 24 hours.</p>
    <p><em>Ministry of Statistics and Programme Implementation (MoSPI), Government of India</em></p>
</body>
</html>"""
        return self.send_email(
            to_email=to_email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            metadata={"type": "EMAIL_VERIFICATION", "token": token},
        )

    def send_password_reset_email(
        self,
        to_email: str,
        token: str,
        user_name: Optional[str] = None,
    ) -> bool:
        """Send password reset token."""
        greeting = f"Dear {user_name}," if user_name else "Dear Civil Service Colleague,"
        subject = "SIH26101 Platform — Password Reset Request"
        text_body = f"""{greeting}

We received a request to reset your password on the Official Statistics Competency Intelligence and Adaptive Learning Platform.

Please use the following single-use token to reset your password:
Token: {token}

This token will expire in 1 hour.

If you did not request a password reset, please contact project administration immediately.

Ministry of Statistics and Programme Implementation (MoSPI)
Government of India
"""
        html_body = f"""<html>
<body>
    <p>{greeting}</p>
    <p>We received a request to reset your password on the <strong>Official Statistics Competency Intelligence and Adaptive Learning Platform</strong>.</p>
    <p>Please use the following single-use password reset token:</p>
    <p style="font-size: 18px; font-family: monospace; background: #f1f5f9; padding: 10px; border-radius: 4px; display: inline-block;">
        {token}
    </p>
    <p>This token will expire in 1 hour.</p>
    <p><em>Ministry of Statistics and Programme Implementation (MoSPI), Government of India</em></p>
</body>
</html>"""
        return self.send_email(
            to_email=to_email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            metadata={"type": "PASSWORD_RESET", "token": token},
        )

    def send_admin_invitation_email(
        self,
        to_email: str,
        token: str,
        designation: str,
        scopes: List[Any],
    ) -> bool:
        """Send administrator authorization invitation."""
        subject = "SIH26101 Platform — Administrator Invitation"
        text_body = f"""Dear Officer,

You have been designated as a Supervisory Administrator on the Official Statistics Competency Intelligence and Adaptive Learning Platform.

Official Designation: {designation}
Authorized Scope Count: {len(scopes)}

Please use the following single-use invitation token to set your administrative password and activate your account:
Token: {token}

This invitation token will expire in 72 hours.

Ministry of Statistics and Programme Implementation (MoSPI)
Government of India
"""
        html_body = f"""<html>
<body>
    <p>Dear Officer,</p>
    <p>You have been designated as a Supervisory Administrator on the <strong>Official Statistics Competency Intelligence and Adaptive Learning Platform</strong>.</p>
    <p><strong>Official Designation:</strong> {designation}<br>
       <strong>Authorized Jurisdiction Scopes:</strong> {len(scopes)} scope(s) assigned.</p>
    <p>Please use the following single-use invitation token to complete administrative activation:</p>
    <p style="font-size: 18px; font-family: monospace; background: #f1f5f9; padding: 10px; border-radius: 4px; display: inline-block;">
        {token}
    </p>
    <p>This invitation token will expire in 72 hours.</p>
    <p><em>Ministry of Statistics and Programme Implementation (MoSPI), Government of India</em></p>
</body>
</html>"""
        return self.send_email(
            to_email=to_email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            metadata={"type": "ADMIN_INVITATION", "token": token, "designation": designation},
        )


class DevelopmentEmailAdapter(BaseEmailService):
    """In-memory, test-friendly email adapter that records sent messages without external network calls."""

    def __init__(self) -> None:
        self.outbox: List[Dict[str, Any]] = []

    def send_email(
        self,
        to_email: str,
        subject: str,
        text_body: str,
        html_body: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        record = {
            "to_email": to_email,
            "subject": subject,
            "text_body": text_body,
            "html_body": html_body,
            "metadata": metadata or {},
        }
        self.outbox.append(record)
        return True

    def get_latest_email(self, to_email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Return the most recently sent email, optionally filtered by recipient."""
        if not self.outbox:
            return None
        if to_email is None:
            return self.outbox[-1]
        for msg in reversed(self.outbox):
            if msg["to_email"].lower() == to_email.lower():
                return msg
        return None

    def get_latest_token(self, to_email: Optional[str] = None) -> Optional[str]:
        """Convenience method for tests to extract the token from the latest email."""
        msg = self.get_latest_email(to_email)
        if msg and "metadata" in msg and "token" in msg["metadata"]:
            return msg["metadata"]["token"]
        return None

    def clear(self) -> None:
        """Clear outbox for testing isolation."""
        self.outbox.clear()


class SMTPEmailAdapter(BaseEmailService):
    """Production SMTP email adapter."""

    def __init__(
        self,
        host: str,
        port: int,
        user: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
        from_email: Optional[str] = None,
    ) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.use_tls = use_tls
        self.from_email = from_email or "no-reply@sih26101.gov.in"

    def send_email(
        self,
        to_email: str,
        subject: str,
        text_body: str,
        html_body: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = to_email
        msg.set_content(text_body)
        if html_body:
            msg.add_alternative(html_body, subtype="html")

        try:
            with smtplib.SMTP(self.host, self.port, timeout=10) as server:
                if self.use_tls:
                    server.starttls()
                if self.user and self.password:
                    server.login(self.user, self.password)
                server.send_message(msg)
            return True
        except Exception:
            return False


# Global default email service instance
_default_email_service: Optional[BaseEmailService] = None


def get_email_service() -> BaseEmailService:
    """Factory providing configured email adapter based on environment."""
    global _default_email_service
    if _default_email_service is not None:
        return _default_email_service

    env = os.getenv("ENVIRONMENT", "development").lower()
    smtp_host = os.getenv("SMTP_HOST")

    if env == "production" and smtp_host:
        port = int(os.getenv("SMTP_PORT", "587"))
        user = os.getenv("SMTP_USER")
        password = os.getenv("SMTP_PASSWORD")
        use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")
        from_email = os.getenv("SMTP_FROM_EMAIL")
        _default_email_service = SMTPEmailAdapter(
            host=smtp_host,
            port=port,
            user=user,
            password=password,
            use_tls=use_tls,
            from_email=from_email,
        )
    else:
        _default_email_service = DevelopmentEmailAdapter()

    return _default_email_service


def set_email_service(service: BaseEmailService) -> None:
    """Override email service instance (useful for test fixtures)."""
    global _default_email_service
    _default_email_service = service

