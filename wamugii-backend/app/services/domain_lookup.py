"""
Domain availability lookups over RDAP.

RDAP (Registration Data Access Protocol, RFC 9082/9083) is the official,
JSON-based successor to WHOIS. Every gTLD registry and many ccTLD registries
run an RDAP server; IANA publishes which server answers for which TLD in a
"bootstrap" file. For a domain lookup the registry answers:

* 200 with a JSON record -> the name is registered (taken);
* 404                    -> the registry has no such name (available);
* anything else          -> we could not tell (rate limit, outage, ...).

Why RDAP and not a registrar API: it is free, needs no account or API key,
comes straight from the registry, and covers .rw (RICTA runs
https://rdap.ricta.org.rw). A registrar API (e.g. Namecheap) can be added
later for automatic registration; availability would still come from here.

"Available" means "not registered". A registry can still refuse a name at
registration time (reserved or premium names, local eligibility rules), so the
UI says the final check happens when WAMUGII registers it.

Results are cached in memory for a few minutes so repeated searches (and the
re-check when a client orders) do not hammer the registries.
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import date

import httpx

logger = logging.getLogger(__name__)

BOOTSTRAP_URL = "https://data.iana.org/rdap/dns.json"
BOOTSTRAP_TTL = 24 * 3600          # IANA updates the file rarely
RESULT_TTL = 5 * 60                # cache each answer for 5 minutes
UNKNOWN_TTL = 30                   # retry failed lookups sooner
TIMEOUT = httpx.Timeout(6.0, connect=4.0)
MAX_PARALLEL = 8

# Used when the IANA bootstrap file cannot be fetched. Values copied from the
# IANA root zone database / bootstrap file.
FALLBACK_SERVERS: dict[str, str] = {
    "rw": "https://rdap.ricta.org.rw/",
    "com": "https://rdap.verisign.com/com/v1/",
    "net": "https://rdap.verisign.com/net/v1/",
}

USER_AGENT = "WAMUGII-domain-search/1.0 (+https://wamugii.kento.rw)"

_LABEL = re.compile(r"^(?!-)[a-z0-9-]{1,63}(?<!-)$")


class InvalidDomain(ValueError):
    """The text cannot be a domain name."""


def to_ascii_label(label: str) -> str:
    """One label in its ASCII (punycode) form, validated."""
    label = label.strip().lower()
    if not label:
        raise InvalidDomain("Please type a name.")
    try:
        ascii_label = label.encode("idna").decode("ascii") if not label.isascii() else label
    except UnicodeError as exc:
        raise InvalidDomain("That name has characters a domain cannot use.") from exc
    if not _LABEL.match(ascii_label):
        raise InvalidDomain(
            "Use only letters, numbers and hyphens (not at the start or end), up to 63 characters."
        )
    if ascii_label[2:4] == "--" and not ascii_label.startswith("xn--"):
        raise InvalidDomain("A name cannot have two hyphens in the 3rd and 4th place.")
    return ascii_label


def parse_query(text: str, known_extensions: list[str]) -> tuple[str, str | None]:
    """
    Split what a person typed into (name, extension or None).

    Accepts "kigalishop", "kigalishop.rw", "www.kigalishop.co.rw",
    "https://kigalishop.com/about". Spaces are removed ("kigali shop" ->
    "kigalishop"). Multi-level extensions such as ".co.rw" are matched against
    the known list first (longest match wins).
    """
    q = (text or "").strip().lower()
    q = re.sub(r"^[a-z]+://", "", q)
    q = q.split("/")[0].split("?")[0].split("#")[0]
    q = re.sub(r"\s+", "", q).strip(".")
    if q.startswith("www."):
        q = q[4:]
    if not q:
        raise InvalidDomain("Please type a name.")
    if "." not in q:
        return to_ascii_label(q), None
    for ext in sorted(known_extensions, key=len, reverse=True):
        if q.endswith(ext) and len(q) > len(ext):
            name = q[: -len(ext)]
            if "." not in name:
                return to_ascii_label(name), ext
    name, _, rest = q.partition(".")
    for part in rest.split("."):
        to_ascii_label(part)
    return to_ascii_label(name), "." + rest


def tld_of(extension: str) -> str:
    """'.co.rw' -> 'rw'."""
    return extension.rsplit(".", 1)[-1]


@dataclass
class Check:
    domain: str
    extension: str
    status: str                     # available | taken | unknown
    expires_at: date | None = None
    registrar: str | None = None
    reason: str | None = None


@dataclass
class _Cache:
    servers: dict[str, str] = field(default_factory=dict)
    servers_at: float = 0.0
    results: dict[str, tuple[float, Check]] = field(default_factory=dict)


_cache = _Cache()
_bootstrap_lock = asyncio.Lock()


def clear_cache() -> None:
    _cache.servers, _cache.servers_at, _cache.results = {}, 0.0, {}


async def _load_bootstrap(client: httpx.AsyncClient) -> None:
    async with _bootstrap_lock:
        if _cache.servers and time.time() - _cache.servers_at < BOOTSTRAP_TTL:
            return
        try:
            r = await client.get(BOOTSTRAP_URL)
            r.raise_for_status()
            servers: dict[str, str] = {}
            for tlds, urls in r.json().get("services", []):
                url = next((u for u in urls if u.startswith("https://")), urls[0] if urls else None)
                if url:
                    for t in tlds:
                        servers[t.lower()] = url if url.endswith("/") else url + "/"
            if servers:
                _cache.servers, _cache.servers_at = servers, time.time()
                return
        except Exception as exc:  # network, JSON, shape -- fall back quietly
            logger.warning("RDAP bootstrap unavailable (%s); using built-in servers", exc)
        _cache.servers = dict(FALLBACK_SERVERS)
        _cache.servers_at = time.time() - BOOTSTRAP_TTL + 600   # try again in 10 minutes


async def rdap_server(tld: str, client: httpx.AsyncClient) -> str | None:
    if not _cache.servers or time.time() - _cache.servers_at >= BOOTSTRAP_TTL:
        await _load_bootstrap(client)
    return _cache.servers.get(tld) or FALLBACK_SERVERS.get(tld)


def _parse_record(data: dict) -> tuple[date | None, str | None]:
    expires, registrar = None, None
    for event in data.get("events", []) or []:
        if event.get("eventAction") == "expiration" and event.get("eventDate"):
            try:
                expires = date.fromisoformat(str(event["eventDate"])[:10])
            except ValueError:
                pass
    for entity in data.get("entities", []) or []:
        if "registrar" in (entity.get("roles") or []):
            for item in (entity.get("vcardArray") or [None, []])[1]:
                if item and item[0] == "fn":
                    registrar = str(item[3])[:100]
    return expires, registrar


async def check_domain(domain: str, extension: str, client: httpx.AsyncClient) -> Check:
    now = time.time()
    cached = _cache.results.get(domain)
    if cached and cached[0] > now:
        return cached[1]
    server = await rdap_server(tld_of(extension), client)
    if server is None:
        result = Check(domain, extension, "unknown", reason="No public lookup service for this extension")
    else:
        try:
            r = await client.get(f"{server}domain/{domain}", headers={"Accept": "application/rdap+json"})
            if r.status_code == 404:
                result = Check(domain, extension, "available")
            elif r.status_code == 200:
                try:
                    expires, registrar = _parse_record(r.json())
                except ValueError:
                    expires, registrar = None, None
                result = Check(domain, extension, "taken", expires, registrar)
            elif r.status_code == 429:
                result = Check(domain, extension, "unknown", reason="The registry is busy; try again in a minute")
            else:
                result = Check(domain, extension, "unknown", reason=f"Registry answered {r.status_code}")
        except httpx.HTTPError as exc:
            logger.info("RDAP lookup for %s failed: %s", domain, exc)
            result = Check(domain, extension, "unknown", reason="The registry did not answer in time")
    ttl = UNKNOWN_TTL if result.status == "unknown" else RESULT_TTL
    _cache.results[domain] = (now + ttl, result)
    if len(_cache.results) > 5000:                      # keep memory bounded
        for key in sorted(_cache.results, key=lambda k: _cache.results[k][0])[:1000]:
            _cache.results.pop(key, None)
    return result


def make_client(transport: httpx.AsyncBaseTransport | None = None) -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True, transport=transport,
                             headers={"User-Agent": USER_AGENT})


# Tests swap this for an httpx.MockTransport so no real registry is called.
transport_override: httpx.AsyncBaseTransport | None = None


async def check_many(pairs: list[tuple[str, str]]) -> list[Check]:
    """Check (domain, extension) pairs in parallel, keeping their order."""
    sem = asyncio.Semaphore(MAX_PARALLEL)
    async with make_client(transport_override) as client:
        async def one(domain: str, ext: str) -> Check:
            async with sem:
                return await check_domain(domain, ext, client)
        return list(await asyncio.gather(*(one(d, e) for d, e in pairs)))


def suggestions_for(name: str) -> list[str]:
    """A few alternative names to try when the exact one is taken."""
    base = name[:55]
    ideas = [f"{base}rw", f"get{base}", f"{base}-rw", f"my{base}", f"{base}hq"]
    out = []
    for idea in ideas:
        if _LABEL.match(idea) and idea != name and idea not in out:
            out.append(idea)
    return out[:4]
