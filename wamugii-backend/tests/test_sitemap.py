"""sitemap.xml: the public pages plus every published course."""

from xml.etree import ElementTree

from app.api.v1.sitemap import DEFAULT_SITE_URL, site_url
from app.core.config import settings

NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def _locs(xml: str) -> list[str]:
    root = ElementTree.fromstring(xml)
    return [el.text or "" for el in root.findall(".//s:loc", NS)]


def _publish_course(client, admin_headers, title: str, slug: str) -> dict:
    r = client.post(
        "/api/v1/courses",
        headers=admin_headers,
        json={"title": title, "slug": slug, "description": "A course.", "is_free": True,
              "status": "PUBLISHED"},
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_sitemap_is_valid_xml_with_the_public_pages(client):
    r = client.get("/api/v1/sitemap.xml")
    assert r.status_code == 200
    # Crawlers reject a sitemap served as text/html.
    assert r.headers["content-type"].startswith("application/xml")

    locs = _locs(r.text)
    base = site_url()
    for path in ("/", "/services", "/hosting", "/domains", "/courses", "/request-quote"):
        assert f"{base}{path}" in locs


def test_sitemap_lists_published_courses(client, admin_headers):
    _publish_course(client, admin_headers, "Modern AI", "modern-ai")
    locs = _locs(client.get("/api/v1/sitemap.xml").text)
    assert f"{site_url()}/courses/modern-ai" in locs


def test_sitemap_omits_drafts_and_deleted_courses(client, admin_headers):
    """
    A draft has no public page, so listing it would send crawlers to a 404.
    """
    published = _publish_course(client, admin_headers, "Published", "published-one")
    client.post(
        "/api/v1/courses",
        headers=admin_headers,
        json={"title": "Draft", "slug": "draft-one", "description": "x", "is_free": True,
              "status": "DRAFT"},
    )
    removed = _publish_course(client, admin_headers, "Removed", "removed-one")
    client.delete(f"/api/v1/courses/{removed['id']}", headers=admin_headers)

    locs = _locs(client.get("/api/v1/sitemap.xml").text)
    base = site_url()
    assert f"{base}/courses/{published['slug']}" in locs
    assert f"{base}/courses/draft-one" not in locs
    assert f"{base}/courses/removed-one" not in locs


def test_sitemap_is_public(client):
    """An uptime monitor and a crawler both arrive without a session."""
    assert client.get("/api/v1/sitemap.xml").status_code == 200


def test_site_url_follows_the_configured_frontend_url(monkeypatch):
    monkeypatch.setattr(settings, "FRONTEND_URL", "https://example.test/")
    assert site_url() == "https://example.test"
    monkeypatch.setattr(settings, "FRONTEND_URL", None)
    assert site_url() == DEFAULT_SITE_URL


def test_course_slugs_are_escaped(client, admin_headers):
    """
    Slugs are generated, not free text, but the sitemap must still be valid XML
    whatever a slug contains -- so this asserts the document parses.
    """
    _publish_course(client, admin_headers, "Maths & Python", "maths-python")
    xml = client.get("/api/v1/sitemap.xml").text
    ElementTree.fromstring(xml)          # raises if the document is malformed
    assert "&amp;" in xml or "&" not in xml
