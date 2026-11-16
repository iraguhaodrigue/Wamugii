"""
The WHOIS fallback for extensions the IANA RDAP bootstrap file does not list.

.io and .co have no RDAP server, so before this they always came back
"unknown". The fallback speaks the WHOIS protocol (RFC 3912) over TCP 43.

No real registry is contacted. A fake WHOIS server runs on 127.0.0.1 on an
ephemeral port, in its own thread with its own event loop so it is independent
of whichever loop the app is using, and `WHOIS_SERVERS` / `WHOIS_PORT` are
pointed at it.
"""

import asyncio
import socket
import threading

import httpx
import pytest

from app.services import domain_lookup
from app.services.domain_lookup import _parse_whois

# Replies modelled on what the real servers send.
TAKEN_REPLY = """Domain Name: GOOGLE.IO
Registry Domain ID: D503300000040537123-LRMS
Registrar: MarkMonitor Inc.
Registry Expiry Date: 2027-05-18T04:00:00Z
Domain Status: clientTransferProhibited

>>> Last update of WHOIS database: 2026-11-10T00:00:00Z <<<
"""

NOT_FOUND_REPLY = """Domain not found.

>>> Last update of WHOIS database: 2026-11-10T00:00:00Z <<<
"""

GARBLED_REPLY = "Service temporarily unavailable. Please try again later.\n"


class FakeWhoisServer:
    """
    A WHOIS server that answers from a dict of {name: reply}.

    Runs in its own thread so the app's event loop can connect to it over a
    real socket, which is what makes this exercise the actual asyncio stream
    code rather than a stubbed-out function.
    """

    def __init__(self, replies: dict[str, str], default: str = NOT_FOUND_REPLY):
        self.replies, self.default = replies, default
        self.queries: list[str] = []
        self.port = _free_port()
        self._ready = threading.Event()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    async def _handle(self, reader, writer):
        raw = await reader.readline()
        name = raw.decode("utf-8", "replace").strip().lower()
        self.queries.append(name)
        writer.write(self.replies.get(name, self.default).encode())
        await writer.drain()
        writer.close()

    def _run(self) -> None:
        async def main():
            server = await asyncio.start_server(self._handle, "127.0.0.1", self.port)
            async with server:
                self._ready.set()
                while not self._stop.is_set():
                    await asyncio.sleep(0.02)

        asyncio.run(main())

    def __enter__(self) -> "FakeWhoisServer":
        self._thread.start()
        assert self._ready.wait(5), "fake WHOIS server did not start"
        return self

    def __exit__(self, *_exc) -> None:
        self._stop.set()
        self._thread.join(timeout=5)


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def fake_whois(monkeypatch):
    """Point .io and .co at a local fake server for the duration of a test."""
    def _start(replies: dict[str, str], default: str = NOT_FOUND_REPLY) -> FakeWhoisServer:
        server = FakeWhoisServer(replies, default)
        server.__enter__()
        monkeypatch.setattr(domain_lookup, "WHOIS_PORT", server.port)
        monkeypatch.setattr(
            domain_lookup, "WHOIS_SERVERS", {"io": "127.0.0.1", "co": "127.0.0.1"}
        )
        servers.append(server)
        return server

    servers: list[FakeWhoisServer] = []
    domain_lookup.clear_cache()
    yield _start
    for server in servers:
        server.__exit__()
    domain_lookup.clear_cache()


# --- the parser, on its own -------------------------------------------------


def test_a_domain_record_means_taken_with_its_details():
    check = _parse_whois("google.io", ".io", TAKEN_REPLY)
    assert check.status == "taken"
    assert check.expires_at.isoformat() == "2027-05-18"
    assert check.registrar == "MarkMonitor Inc."


def test_an_explicit_not_found_means_available():
    assert _parse_whois("kigalishop.io", ".io", NOT_FOUND_REPLY).status == "available"


@pytest.mark.parametrize(
    "reply",
    [
        "NOT FOUND\n",
        "No Data Found\n",
        "No match for KIGALISHOP.IO.\n",
        "Domain not found.\n",
        "No entries found for the selected source.\n",
    ],
)
def test_every_wording_of_not_found_is_understood(reply):
    assert _parse_whois("kigalishop.io", ".io", reply).status == "available"


def test_a_record_wins_over_not_found_boilerplate():
    """
    Several registries attach "no match for any other query is implied" to
    every reply, including replies about registered names. Reading that as
    "available" would advertise a taken domain as free, so the presence of a
    record decides on its own.
    """
    reply = (
        "Domain Name: KIGALISHOP.CO\n"
        "Registrar: Some Registrar\n"
        "NOTICE: no match for any other query is implied by this answer.\n"
    )
    assert _parse_whois("kigalishop.co", ".co", reply).status == "taken"


def test_an_unreadable_reply_stays_unknown():
    """Never guess: an answer we cannot read is reported as "could not tell"."""
    check = _parse_whois("kigalishop.io", ".io", GARBLED_REPLY)
    assert check.status == "unknown"
    assert check.reason


# --- over a real socket -----------------------------------------------------


def test_whois_lookup_talks_to_the_server_and_reads_the_reply(fake_whois):
    server = fake_whois({"google.io": TAKEN_REPLY})

    taken = asyncio.run(domain_lookup._check_via_whois("google.io", ".io", "127.0.0.1"))
    free = asyncio.run(domain_lookup._check_via_whois("kigalishop.io", ".io", "127.0.0.1"))

    assert taken.status == "taken"
    assert taken.registrar == "MarkMonitor Inc."
    assert free.status == "available"
    # The name really went down the socket.
    assert server.queries == ["google.io", "kigalishop.io"]


def test_whois_failure_is_unknown_not_available(fake_whois):
    """
    Port 43 blocked outbound is the likely failure on a hardened host. It must
    read as "could not tell", never as "available".
    """
    unreachable_port = _free_port()          # nothing is listening there
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(domain_lookup, "WHOIS_PORT", unreachable_port)
        check = asyncio.run(domain_lookup._check_via_whois("kigalishop.io", ".io", "127.0.0.1"))
    assert check.status == "unknown"
    assert check.reason


def test_whois_timeout_is_unknown(fake_whois, monkeypatch):
    """A server that accepts the connection then says nothing must not hang."""
    async def _never_answers(*_args, **_kwargs):
        await asyncio.sleep(10)
        return ""

    monkeypatch.setattr(domain_lookup, "_whois_query", _never_answers)
    monkeypatch.setattr(domain_lookup, "WHOIS_TIMEOUT", 0.05)

    check = asyncio.run(domain_lookup._check_via_whois("kigalishop.io", ".io", "127.0.0.1"))
    assert check.status == "unknown"
    assert "in time" in check.reason


# --- end to end, through the search endpoint --------------------------------


def _bootstrap_without_io_or_co(request: httpx.Request) -> httpx.Response:
    """
    The IANA bootstrap file as it really is: no entry for .io or .co, which is
    exactly why the fallback exists.
    """
    if str(request.url) == domain_lookup.BOOTSTRAP_URL:
        return httpx.Response(200, json={"services": [[["rw"], ["https://rdap.test-ricta.example/"]]]})
    return httpx.Response(404, json={"errorCode": 404})


def test_search_uses_whois_for_io_and_co(client, admin_headers, fake_whois, monkeypatch):
    server = fake_whois({"google.io": TAKEN_REPLY})
    monkeypatch.setattr(
        domain_lookup, "transport_override", httpx.MockTransport(_bootstrap_without_io_or_co)
    )

    for ext, order in ((".io", 1), (".co", 2)):
        r = client.post(
            "/api/v1/domains/extensions",
            headers=admin_headers,
            json={"extension": ext, "cost_price": "40000", "margin": "5000", "display_order": order},
        )
        assert r.status_code == 201, r.text

    body = client.get("/api/v1/domains/search", params={"q": "google"}).json()
    by_ext = {row["extension"]: row for row in body["results"]}

    # .io is registered in the fake registry; .co falls through to not-found.
    assert by_ext[".io"]["status"] == "taken"
    assert by_ext[".co"]["status"] == "available"
    # No longer the old "no public lookup service" dead end.
    assert server.queries
