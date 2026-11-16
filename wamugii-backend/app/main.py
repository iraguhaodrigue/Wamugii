from fastapi import FastAPI, Request
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

# Headers that cost nothing and close off whole classes of attack. Set here
# rather than only in nginx so they are present however the API is reached --
# straight to the container, through a different proxy, or in local dev.
#
# HSTS and Content-Security-Policy are deliberately NOT here: both belong on
# the edge that terminates TLS and serves the HTML (Plesk nginx), and a CSP set
# on JSON responses protects nothing. See deploy/nginx-security-headers.conf.
SECURITY_HEADERS = {
    # Stop the browser second-guessing our Content-Type.
    "X-Content-Type-Options": "nosniff",
    # No framing at all: nothing here is meant to be embedded.
    "X-Frame-Options": "DENY",
    # Send the full URL only to ourselves, the origin alone to anyone else.
    "Referrer-Policy": "strict-origin-when-cross-origin",
    # The API never needs these, so refuse them for anything it serves.
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # setdefault, not assignment: a route that deliberately sets its own value
    # (a future embeddable widget, say) keeps it.
    for header, value in SECURITY_HEADERS.items():
        response.headers.setdefault(header, value)
    return response


app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": settings.PROJECT_NAME}
