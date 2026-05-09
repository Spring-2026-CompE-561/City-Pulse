import logging
import smtplib
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger(__name__)


def can_send_email() -> bool:
    return bool(
        settings.smtp_host
        and settings.smtp_from_email
    )


def send_password_reset_email(
    *,
    recipient_email: str,
    reset_link: str,
    access_code: str,
) -> None:
    """
    Send password reset email with both reset link and access code.

    If SMTP is not configured, this logs a warning and returns without raising.
    """
    if not can_send_email():
        logger.warning(
            "SMTP is not configured. Password reset email was not sent for %s.",
            recipient_email,
        )
        return

    message = EmailMessage()
    message["From"] = settings.smtp_from_email or ""
    message["To"] = recipient_email
    message["Subject"] = "CityPulse password reset instructions"
    message.set_content(
        (
            "We received a request to reset your CityPulse password.\n\n"
            f"Reset link: {reset_link}\n\n"
            f"Access code: {access_code}\n\n"
            "Enter the access code in the reset form after opening the link.\n"
            f"This reset link expires in {settings.password_reset_expire_minutes} minutes.\n"
            "If you did not request this change, you can ignore this email."
        )
    )

    smtp_host = settings.smtp_host
    if smtp_host is None:
        return
    with smtplib.SMTP(smtp_host, settings.smtp_port, timeout=15) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password or "")
        smtp.send_message(message)
