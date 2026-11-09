"""
Domain search (RDAP availability), online ordering and the domain dashboard.

No real registry is ever called: `domain_lookup.transport_override` is replaced
with an httpx.MockTransport that imitates the IANA bootstrap file and two
RDAP servers.
"""

from datetime import date, timedelta

import httpx
import pytest

from app.core.security import create_access_token
from app.crud import user as user_crud
from app.models.domain import Domain, DomainStatus
from app.models.notification import Notification, NotificationType
from app.models.user import Role
from app.schemas.user import UserCreate
from app.services import domain_lookup
from app.services.domain_lookup import InvalidDomain, parse_query
from tests.conftest import TestingSessionLocal

REGISTERED = {"google.com", "kigalishop.rw", "kigalishop.com", "ricta.org.rw"}
CALLS: list[str] = []


def _fake_registry(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    CALLS.append(url)
    if url == domain_lookup.BOOTSTRAP_URL:
        return httpx.Response(200, json={"services": [
            [["com", "net"], ["https://rdap.test-verisign.example/v1/"]],
            [["rw"], ["https://rdap.test-ricta.example/"]],
            [["org"], ["https://rdap.test-pir.example/rdap/"]],
        ]})
    name = url.rsplit("/domain/", 1)[-1]
    if name.startswith("busy"):
        return httpx.Response(429)
    if name in REGISTERED:
        return httpx.Response(200, json={
            "objectClassName": "domain", "ldhName": name,
            "events": [{"eventAction": "registration", "eventDate": "2015-03-01T00:00:00Z"},
                       {"eventAction": "expiration", "eventDate": "2027-03-01T00:00:00Z"}],
            "entities": [{"roles": ["registrar"], "vcardArray": ["vcard", [["version", {}, "text", "4.0"],
                                                                            ["fn", {}, "text", "Test Registrar Ltd"]]]}],
        })
    return httpx.Response(404, json={"errorCode": 404, "title": "Not Found"})


@pytest.fixture(autouse=True)
def _fake_rdap(monkeypatch):
    from app.api.v1 import domains as domains_api
    domain_lookup.clear_cache()
    domains_api.search_limiter.reset()
    CALLS.clear()
    monkeypatch.setattr(domain_lookup, "transport_override", httpx.MockTransport(_fake_registry))
    yield
    domain_lookup.clear_cache()


def _user(email, role=Role.CLIENT, name="Aline Uwase"):
    db = TestingSessionLocal()
    try:
        return user_crud.create(db, UserCreate(full_name=name, email=email, password="password123"), role=role)
    finally:
        db.close()


def _auth(user):
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _prices(client, admin_headers):
    for ext, cost, order in [(".rw", "14000", 1), (".com", "16000", 2), (".co.rw", "14000", 3), (".org", "17000", 4)]:
        r = client.post("/api/v1/domains/extensions", headers=admin_headers,
                        json={"extension": ext, "cost_price": cost, "margin": "5000", "display_order": order})
        assert r.status_code == 201, r.text


# --- parsing -----------------------------------------------------------------


@pytest.mark.parametrize("typed, expected", [
    ("kigalishop", ("kigalishop", None)),
    ("KigaliShop.RW", ("kigalishop", ".rw")),
    ("https://www.kigalishop.co.rw/about", ("kigalishop", ".co.rw")),
    ("kigali shop", ("kigalishop", None)),
    ("ishuri-ryacu.com", ("ishuri-ryacu", ".com")),
    ("café", ("xn--caf-dma", None)),
])
def test_parse_query_understands_what_people_type(typed, expected):
    assert parse_query(typed, [".rw", ".com", ".co.rw"]) == expected


@pytest.mark.parametrize("bad", ["", "-shop", "shop-", "a_b", "x" * 64, "ab--cd", "shop!.rw"])
def test_parse_query_rejects_impossible_names(bad):
    with pytest.raises(InvalidDomain):
        parse_query(bad, [".rw"])


# --- search ------------------------------------------------------------------


def test_search_shows_availability_and_prices_for_every_extension(client, admin_headers):
    _prices(client, admin_headers)
    r = client.get("/api/v1/domains/search", params={"q": "ishuri"})
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "ishuri"
    by_domain = {x["domain"]: x for x in body["results"]}
    assert list(by_domain) == ["ishuri.rw", "ishuri.com", "ishuri.co.rw", "ishuri.org"]
    assert all(x["status"] == "available" for x in body["results"])
    assert by_domain["ishuri.rw"]["price"] == "19000.00"
    assert body["suggestions"] == []


def test_typed_extension_comes_first_and_taken_names_show_details_and_suggestions(client, admin_headers):
    _prices(client, admin_headers)
    body = client.get("/api/v1/domains/search", params={"q": "kigalishop.rw"}).json()
    first = body["results"][0]
    assert first["domain"] == "kigalishop.rw" and first["status"] == "taken"
    assert first["expires_at"] == "2027-03-01" and first["registrar"] == "Test Registrar Ltd"
    assert {x["domain"]: x["status"] for x in body["results"]}["kigalishop.com"] == "taken"
    assert {x["domain"]: x["status"] for x in body["results"]}["kigalishop.co.rw"] == "available"
    assert body["suggestions"] and all(s["domain"].endswith(".rw") and s["status"] == "available"
                                       for s in body["suggestions"])


def test_an_extension_not_in_the_price_list_is_checked_without_a_price(client, admin_headers):
    _prices(client, admin_headers)
    body = client.get("/api/v1/domains/search", params={"q": "ishuri.net"}).json()
    assert body["results"][0]["domain"] == "ishuri.net"
    assert body["results"][0]["status"] == "available"
    assert body["results"][0]["price"] is None


def test_a_busy_registry_gives_unknown_not_an_error(client, admin_headers):
    _prices(client, admin_headers)
    body = client.get("/api/v1/domains/search", params={"q": "busyname"}).json()
    assert {x["status"] for x in body["results"]} == {"unknown"}
    assert "busy" in body["results"][0]["reason"]


def test_answers_are_cached(client, admin_headers):
    _prices(client, admin_headers)
    client.get("/api/v1/domains/search", params={"q": "ishuri"})
    first = len(CALLS)
    client.get("/api/v1/domains/search", params={"q": "ishuri"})
    assert len(CALLS) == first          # no new registry calls


def test_bad_input_is_a_422_with_a_clear_message(client, admin_headers):
    r = client.get("/api/v1/domains/search", params={"q": "-bad-"})
    assert r.status_code == 422
    assert "letters, numbers and hyphens" in r.json()["detail"]


def test_search_is_rate_limited(client, admin_headers):
    _prices(client, admin_headers)
    codes = [client.get("/api/v1/domains/search", params={"q": "ishuri"}).status_code for _ in range(22)]
    assert codes[:20] == [200] * 20 and codes[20:] == [429, 429]


def test_rate_limit_is_per_visitor_behind_nginx(client, admin_headers):
    _prices(client, admin_headers)
    a = {"X-Forwarded-For": "1.1.1.1"}
    b = {"X-Forwarded-For": "9.9.9.9, 2.2.2.2"}     # first entry is visitor-supplied; nginx added the last
    for _ in range(20):
        assert client.get("/api/v1/domains/search", params={"q": "ishuri"}, headers=a).status_code == 200
    assert client.get("/api/v1/domains/search", params={"q": "ishuri"}, headers=a).status_code == 429
    assert client.get("/api/v1/domains/search", params={"q": "ishuri"}, headers=b).status_code == 200
    spoof = {"X-Forwarded-For": "5.5.5.5, 1.1.1.1"}  # faking a new first entry does not escape the limit
    assert client.get("/api/v1/domains/search", params={"q": "ishuri"}, headers=spoof).status_code == 429


def test_bootstrap_failure_falls_back_to_built_in_servers(client, admin_headers, monkeypatch):
    def broken(request):
        if str(request.url) == domain_lookup.BOOTSTRAP_URL:
            raise httpx.ConnectError("down")
        return _fake_registry(request)
    monkeypatch.setattr(domain_lookup, "transport_override", httpx.MockTransport(broken))
    _prices(client, admin_headers)
    body = client.get("/api/v1/domains/search", params={"q": "ricta.org.rw"}).json()
    # .rw has a built-in server, so it still works
    assert body["results"][0]["domain"].endswith(".rw")
    assert any("rdap.ricta.org.rw" in c for c in CALLS)


def test_searches_are_logged_without_ip_addresses(client, admin_headers):
    _prices(client, admin_headers)
    client.get("/api/v1/domains/search", params={"q": "ishuri"})
    from app.models.domain_search import DomainSearch
    db = TestingSessionLocal()
    try:
        rows = db.query(DomainSearch).all()
        assert len(rows) == 1 and rows[0].query == "ishuri" and rows[0].available_count == 4
        assert rows[0].user_id is None
    finally:
        db.close()


# --- public price list --------------------------------------------------------


def test_public_price_list_hides_cost_and_margin(client, admin_headers):
    _prices(client, admin_headers)
    row = client.get("/api/v1/domains/extensions").json()[0]
    assert set(row) == {"extension", "client_price", "display_order"}


def test_second_level_rwandan_extensions_are_allowed(client, admin_headers):
    r = client.post("/api/v1/domains/extensions", headers=admin_headers,
                    json={"extension": "CO.RW", "cost_price": "14000"})
    assert r.status_code == 201 and r.json()["extension"] == ".co.rw"


# --- ordering ------------------------------------------------------------------


def test_client_can_order_an_available_domain(client, admin_headers, staff_headers):
    _prices(client, admin_headers)
    aline = _user("aline@example.com")
    r = client.post("/api/v1/client/domains/order", headers=_auth(aline),
                    json={"domain_name": "ishuri.rw", "years": 2})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["domain_name"] == "ishuri.rw" and body["status"] == "PENDING"
    assert body["registration_fee"] == "28000.00" and body["service_fee"] == "10000.00"
    assert body["total_fee"] == "38000.00"
    assert "notes" not in body

    db = TestingSessionLocal()
    try:
        notes = db.query(Notification).filter(Notification.type == NotificationType.DOMAIN_REQUESTED).all()
        assert len(notes) == 2            # one per admin/staff user
        assert "ishuri.rw" in notes[0].message
        domain = db.query(Domain).one()
        assert "2 years" in domain.notes and "available" in domain.notes
    finally:
        db.close()

    mine = client.get("/api/v1/client/domains", headers=_auth(aline)).json()
    assert [d["domain_name"] for d in mine] == ["ishuri.rw"]


def test_ordering_a_taken_domain_is_refused(client, admin_headers):
    _prices(client, admin_headers)
    r = client.post("/api/v1/client/domains/order", headers=_auth(_user("a@example.com")),
                    json={"domain_name": "kigalishop.rw"})
    assert r.status_code == 409 and "registered" in r.json()["detail"]


def test_the_same_domain_cannot_be_requested_twice(client, admin_headers):
    _prices(client, admin_headers)
    a, b = _user("a@example.com"), _user("b@example.com", name="Jean")
    assert client.post("/api/v1/client/domains/order", headers=_auth(a), json={"domain_name": "ishuri.rw"}).status_code == 201
    again = client.post("/api/v1/client/domains/order", headers=_auth(a), json={"domain_name": "ishuri.rw"})
    other = client.post("/api/v1/client/domains/order", headers=_auth(b), json={"domain_name": "ishuri.rw"})
    assert again.status_code == 409 and "already requested" in again.json()["detail"]
    assert other.status_code == 409 and "already being handled" in other.json()["detail"]


def test_extensions_we_do_not_sell_cannot_be_ordered_online(client, admin_headers):
    _prices(client, admin_headers)
    r = client.post("/api/v1/client/domains/order", headers=_auth(_user("a@example.com")),
                    json={"domain_name": "ishuri.net"})
    assert r.status_code == 422 and "don't sell .net" in r.json()["detail"]


def test_an_unconfirmed_check_still_allows_the_order_with_a_note(client, admin_headers):
    _prices(client, admin_headers)
    r = client.post("/api/v1/client/domains/order", headers=_auth(_user("a@example.com")),
                    json={"domain_name": "busyname.rw"})
    assert r.status_code == 201
    db = TestingSessionLocal()
    try:
        assert "not confirmed" in db.query(Domain).one().notes
    finally:
        db.close()


def test_only_clients_can_order(client, admin_headers, staff_headers):
    _prices(client, admin_headers)
    assert client.post("/api/v1/client/domains/order", json={"domain_name": "ishuri.rw"}).status_code == 401
    assert client.post("/api/v1/client/domains/order", headers=staff_headers,
                       json={"domain_name": "ishuri.rw"}).status_code == 403


# --- dashboard -----------------------------------------------------------------


def test_dashboard_summarises_requests_renewals_and_demand(client, admin_headers):
    _prices(client, admin_headers)
    aline = _user("aline@example.com")
    client.post("/api/v1/client/domains/order", headers=_auth(aline), json={"domain_name": "ishuri.rw"})
    today = date.today()
    for name, days in [("soon.rw", 20), ("later.com", 200), ("late.rw", -3)]:
        r = client.post("/api/v1/domains", headers=admin_headers, json={
            "client_id": aline.id, "domain_name": name, "status": "ACTIVE",
            "registration_fee": "14000", "service_fee": "5000",
            "registered_date": str(today - timedelta(days=300)), "expires_at": str(today + timedelta(days=days))})
        assert r.status_code == 201, r.text
    for q in ["ishuri", "ishuri", "kigalishop"]:
        client.get("/api/v1/domains/search", params={"q": q})

    d = client.get("/api/v1/domains/dashboard", headers=admin_headers).json()
    assert d["counts"]["PENDING"] == 1 and d["counts"]["ACTIVE"] == 3 and d["counts"]["TOTAL"] == 4
    assert d["yearly_value"] == "57000.00"
    assert [p["domain_name"] for p in d["pending_requests"]] == ["ishuri.rw"]
    assert d["pending_requests"][0]["client_name"] == "Aline Uwase"
    assert [e["domain_name"] for e in d["expiring"]] == ["late.rw", "soon.rw"]
    assert d["expiring"][0]["days_left"] == -3
    assert {e["extension"]: e["count"] for e in d["by_extension"]} == {".rw": 3, ".com": 1}
    assert d["searches_30_days"] == 3
    assert d["top_searches"][0] == {**d["top_searches"][0], "name": "ishuri", "searches": 2}
    assert d["available_share"] == 1.0


def test_dashboard_is_for_staff_only(client, client_headers, staff_headers):
    assert client.get("/api/v1/domains/dashboard", headers=client_headers).status_code == 403
    assert client.get("/api/v1/domains/dashboard", headers=staff_headers).status_code == 200
