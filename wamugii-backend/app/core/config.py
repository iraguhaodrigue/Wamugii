from pydantic_settings import BaseSettings, SettingsConfigDict


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
