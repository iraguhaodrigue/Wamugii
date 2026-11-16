"""
sitemap.xml, built from the live catalogue.

Generated rather than checked in, because the course list changes whenever an
instructor publishes one, and a stale sitemap is worse than none: it points
crawlers at pages that may have moved and omits the ones that matter.

nginx maps https://wamugii.kento.rw/sitemap.xml onto this endpoint -- see
deploy/nginx-security-headers.conf. robots.txt is a static file in the
frontend's public/ folder, since it never changes.
"""

from xml.sax.saxutils import escape

from fastapi import APIRouter, Response

from app.api.deps import DbDep
from app.core.config import settings
from app.crud import course as course_crud

router = APIRouter(tags=["sitemap"])

# The public marketing pages, with a rough hint of how often each changes.
# "changefreq" and "priority" are only hints and crawlers may ignore them.
STATIC_PAGES: list[tuple[str, str, str]] = [
    ("", "weekly", "1.0"),
    ("services", "monthly", "0.9"),
    ("hosting", "monthly", "0.8"),
    ("domains", "monthly", "0.8"),
    ("courses", "weekly", "0.8"),
    ("request-quote", "yearly", "0.6"),
]

DEFAULT_SITE_URL = "https://wamugii.kento.rw"


def site_url() -> str:
    """The public origin, without a trailing slash."""
    return (settings.FRONTEND_URL or DEFAULT_SITE_URL).rstrip("/")


def _entry(loc: str, changefreq: str, priority: str, lastmod: str | None = None) -> str:
    parts = [f"    <loc>{escape(loc)}</loc>"]
    if lastmod:
        parts.append(f"    <lastmod>{lastmod}</lastmod>")
    parts.append(f"    <changefreq>{changefreq}</changefreq>")
    parts.append(f"    <priority>{priority}</priority>")
    body = "\n".join(parts)
    return f"  <url>\n{body}\n  </url>"


@router.get(
    "/sitemap.xml",
    summary="sitemap.xml for the public site (public)",
    response_class=Response,
)
def sitemap(db: DbDep) -> Response:
    base = site_url()

    urls = [_entry(f"{base}/{path}" if path else f"{base}/", freq, pri)
            for path, freq, pri in STATIC_PAGES]

    # Only PUBLISHED and active courses: a draft has no public page, and
    # listing one would send crawlers to a 404.
    for course in course_crud.list_published_courses(db):
        urls.append(
            _entry(
                f"{base}/courses/{course.slug}",
                "monthly",
                "0.7",
                course.updated_at.date().isoformat() if course.updated_at else None,
            )
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    # Explicit media type: served through nginx this must not inherit the SPA's
    # text/html, or crawlers reject it.
    return Response(content=xml, media_type="application/xml")
