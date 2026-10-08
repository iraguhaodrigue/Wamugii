from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import _check_secret_key, settings

app = FastAPI(title=settings.PROJECT_NAME)


@app.on_event("startup")
def _warn_on_weak_secret() -> None:
    """
    Re-run the SECRET_KEY check once uvicorn's logging is wired up.

    The check at import time catches cases where another entry point imports
    the module (CLI scripts, tests). This one guarantees a running API server
    always logs it on boot, which is where an operator is most likely to see
    it.
    """
    _check_secret_key(settings.SECRET_KEY)

origins = [o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": settings.PROJECT_NAME}
