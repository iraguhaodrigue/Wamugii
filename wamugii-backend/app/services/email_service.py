"""
Transactional email via Brevo.

A thin HTTP call rather than Brevo's SDK: the project already depends on httpx
(it ships with the FastAPI test client), so one POST to their REST API adds no
new dependency at all.

Like the notification emitters this wraps, `send_email` never raises. Email is
the least important thing happening in any request that triggers it — a Brevo
outage, a rate limit, or a missing API key must never turn a recorded payment
or a submitted quote into an error for the user.
"""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

BREVO_ENDPOINT = "https://api.brevo.com/v3/smtp/email"
TIMEOUT_SECONDS = 10.0


def is_configured() -> bool:
    """True when Brevo credentials are present and email can actually be sent."""
    return bool(settings.BREVO_API_KEY and settings.BREVO_FROM_EMAIL)


def send_email(
    to_email: str,
    to_name: str,
    subject: str,
    html_content: str,
    text_content: str | None = None,
) -> bool:
    """
    Send one transactional email. Returns True on a 2xx from Brevo, False on
    anything else — including "not configured", which is a normal state in
    local dev, not an error.

    Never raises: every failure path logs and returns False.
    """
    if not is_configured():
        logger.warning(
            "email not sent to %s (%r): BREVO_API_KEY/BREVO_FROM_EMAIL not configured",
            to_email,
            subject,
        )
        return False

    payload: dict = {
        "sender": {"email": settings.BREVO_FROM_EMAIL, "name": settings.BREVO_FROM_NAME},
        "to": [{"email": to_email, "name": to_name}],
        "subject": subject,
        "htmlContent": html_content,
    }
    if text_content:
        payload["textContent"] = text_content

    try:
        response = httpx.post(
            BREVO_ENDPOINT,
            json=payload,
            headers={
                "api-key": settings.BREVO_API_KEY or "",
                "accept": "application/json",
                "content-type": "application/json",
            },
            timeout=TIMEOUT_SECONDS,
        )
    except Exception:
        # Network error, DNS failure, timeout — logged, not raised.
        logger.exception("email to %s (%r) failed: could not reach Brevo", to_email, subject)
        return False

    if response.is_success:
        logger.info("email sent to %s (%r)", to_email, subject)
        return True

    # 4xx/5xx: bad key, unverified sender, rate limit, malformed payload. The
    # body carries Brevo's reason and is worth having in the log, but it is
    # truncated so a large error page cannot flood the logs.
    logger.warning(
        "email to %s (%r) rejected by Brevo: HTTP %s %s",
        to_email,
        subject,
        response.status_code,
        response.text[:500],
    )
    return False
