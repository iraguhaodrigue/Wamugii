import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Below this, HS256 signing is considered weak and `jwt` already warns on every
# encode. 32 bytes matches the pyjwt recommendation; we recommend 48 (via
# `secrets.token_urlsafe(48)`) in .env.example for a comfortable margin.
MIN_SECRET_KEY_BYTES = 32


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "WAMUGII TECH SOLUTIONS API"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://wamugii:wamugii@db:5432/wamugii"

    # Security
    SECRET_KEY: str = "CHANGE_ME_TO_A_LONG_RANDOM_STRING"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # First admin (created by the seed script)
    FIRST_ADMIN_EMAIL: str = "admin@wamugii.rw"
    FIRST_ADMIN_PASSWORD: str = "changeme123"

    # CORS (comma separated). Your Next.js dev server is usually http://localhost:3000
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # Brevo transactional email. Both optional: with either missing, email
    # sending is skipped with a warning so local dev and tests run without a
    # Brevo account. See app/services/email_service.py.
    BREVO_API_KEY: str | None = None
    BREVO_FROM_EMAIL: str | None = None
    BREVO_FROM_NAME: str = "WAMUGII TECH SOLUTIONS"

    # Public URL of the frontend, used to build call-to-action links in emails.
    # Unset means emails are sent without a CTA button rather than linking to
    # a localhost URL the recipient cannot open.
    FRONTEND_URL: str | None = None


settings = Settings()


def _check_secret_key(key: str) -> None:
    """
    Warn if SECRET_KEY is too short to sign JWTs comfortably.

    Called at module load (and again from `main.py` on app start, so it reaches
    uvicorn's own log output and not just whichever handler happens to be set
    up at import time). A warning rather than a crash: this is a shared repo
    and a short dev-only key must not stop the app booting, but it must be
    hard to miss in a real deploy. Generate a strong one with:

        python -c "import secrets; print(secrets.token_urlsafe(48))"

    and put it in .env (gitignored). Never commit a real key.
    """
    length = len(key.encode("utf-8"))
    if length < MIN_SECRET_KEY_BYTES:
        logger.warning(
            "SECRET_KEY is %d bytes (minimum recommended: %d). JWTs signed with "
            "this key are weaker than they should be. Generate a strong one with "
            "`python -c \"import secrets; print(secrets.token_urlsafe(48))\"` and "
            "set it in your .env file. Never commit the real key.",
            length,
            MIN_SECRET_KEY_BYTES,
        )
    # The placeholder value in .env.example is a specific foot-gun worth
    # calling out even if it happens to be long enough.
    if key.startswith("CHANGE_ME") or key == "change-this-to-a-long-random-string":
        logger.warning(
            "SECRET_KEY looks like the .env.example placeholder. Replace it with "
            "a freshly generated value before any real deploy."
        )


_check_secret_key(settings.SECRET_KEY)
