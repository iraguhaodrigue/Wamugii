"""
Domain search, online ordering and the admin domain dashboard.

* `search`    -- availability for one name across the active price-list
                 extensions (RDAP, see domain_lookup), with prices and, when the
                 main name is taken, a few alternative suggestions.
* `order`     -- a signed-in client asks for an available domain: a PENDING
                 domain row is created with the fees from the price list, and
                 the team is notified. Nothing is charged or registered
                 automatically; staff register it and invoice as usual.
* `dashboard` -- numbers and lists for the admin/staff domain dashboard.
"""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud import domain as domain_crud
from app.crud import domain_extension as extension_crud
from app.models.domain import Domain, DomainStatus
from app.models.domain_search import DomainSearch
from app.models.user import User
from app.schemas.domain import DomainCreate
from app.schemas.domain_search import (
    DashboardDomainRow,
    DomainCheckResult,
    DomainDashboard,
    DomainOrderCreate,
    DomainSearchResponse,
    ExtensionCount,
    SearchedName,
)
from app.services import domain_lookup, notifications
from app.services.domain_lookup import InvalidDomain

MAX_EXTENSIONS = 12
ORDER_REGISTRAR = "To be confirmed"


def _price_list(db: Session) -> dict[str, tuple[Decimal, Decimal, Decimal]]:
    """extension -> (client price, cost, margin) for active extensions, in display order."""
    return {e.extension: (e.client_price, e.cost_price, e.margin) for e in extension_crud.list_extensions(db)}


def _result(check: domain_lookup.Check, prices: dict) -> DomainCheckResult:
    price = prices.get(check.extension)
    return DomainCheckResult(
        domain=check.domain, extension=check.extension, status=check.status,
        price=price[0] if price else None, expires_at=check.expires_at,
        registrar=check.registrar, reason=check.reason,
    )


async def search(db: Session, text: str, user: User | None) -> DomainSearchResponse:
    prices = _price_list(db)
    try:
        name, typed = domain_lookup.parse_query(text, list(prices))
    except InvalidDomain as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    extensions = list(prices)[:MAX_EXTENSIONS]
    if typed:
        extensions = [typed] + [e for e in extensions if e != typed]
    if not extensions:
        extensions = [".rw", ".com"]
    pairs = [(name + ext, ext) for ext in extensions]
    checks = await domain_lookup.check_many(pairs)
    results = [_result(c, prices) for c in checks]

    suggestions: list[DomainCheckResult] = []
    primary = results[0]
    if primary.status == "taken":
        ext = primary.extension
        alt = [(idea + ext, ext) for idea in domain_lookup.suggestions_for(name)]
        suggestions = [_result(c, prices) for c in await domain_lookup.check_many(alt)
                       if c.status == "available"]

    db.add(DomainSearch(
        query=name[:100],
        available_count=sum(r.status == "available" for r in results),
        taken_count=sum(r.status == "taken" for r in results),
        user_id=user.id if user else None,
    ))
    db.commit()

    return DomainSearchResponse(query=text.strip()[:120], name=name, results=results,
                                suggestions=suggestions, checked_at=datetime.now(timezone.utc))


async def order(db: Session, client: User, data: DomainOrderCreate) -> Domain:
    prices = _price_list(db)
    try:
        name, ext = domain_lookup.parse_query(data.domain_name, list(prices))
    except InvalidDomain as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not ext:
        raise HTTPException(status_code=422, detail="Please include the extension, for example kigalishop.rw")
    if ext not in prices:
        raise HTTPException(status_code=422,
                            detail=f"We don't sell {ext} online yet. Send us a quote request and we'll help.")
    full = name + ext

    existing = db.scalar(select(Domain).where(
        Domain.domain_name == full, Domain.is_active.is_(True),
        Domain.status.in_([DomainStatus.PENDING, DomainStatus.ACTIVE])))
    if existing is not None:
        mine = existing.client_id == client.id
        raise HTTPException(status_code=409, detail=(
            f"You have already requested {full}." if mine else f"{full} is already being handled by our team."))

    check = (await domain_lookup.check_many([(full, ext)]))[0]
    if check.status == "taken":
        raise HTTPException(status_code=409, detail=f"Sorry, {full} has just been registered by someone else.")

    _, cost, margin = prices[ext]
    years = data.years
    checked = "available" if check.status == "available" else f"not confirmed ({check.reason})"
    domain = domain_crud.create_domain(db, DomainCreate(
        client_id=client.id,
        domain_name=full,
        registrar=ORDER_REGISTRAR,
        registration_fee=cost * years,
        service_fee=margin * years,
        status=DomainStatus.PENDING,
        notes=(f"Requested online by the client for {years} year{'s' if years > 1 else ''}. "
               f"Registry check on {date.today().isoformat()}: {checked}."),
    ))
    notifications.notify_domain_requested(db, domain, client, years)
    return domain


def _extension_of(name: str, known: list[str]) -> str:
    for ext in sorted(known, key=len, reverse=True):
        if name.endswith(ext):
            return ext
    return "." + name.rsplit(".", 1)[-1] if "." in name else "?"


def dashboard(db: Session, today: date | None = None) -> DomainDashboard:
    today = today or date.today()
    rows = db.execute(
        select(Domain, User.full_name).join(User, User.id == Domain.client_id).where(Domain.is_active.is_(True))
    ).all()

    def row(d: Domain, client_name: str) -> DashboardDomainRow:
        return DashboardDomainRow(
            id=d.id, domain_name=d.domain_name, client_id=d.client_id, client_name=client_name,
            status=d.status, total_fee=d.total_fee, created_at=d.created_at, expires_at=d.expires_at,
            days_left=(d.expires_at - today).days if d.expires_at else None, auto_renew=d.auto_renew)

    counts = Counter(d.status.value for d, _ in rows)
    pending = sorted((row(d, n) for d, n in rows if d.status == DomainStatus.PENDING),
                     key=lambda r: r.created_at, reverse=True)[:25]
    horizon = today + timedelta(days=90)
    expiring = sorted((row(d, n) for d, n in rows
                       if d.status == DomainStatus.ACTIVE and d.expires_at and d.expires_at <= horizon),
                      key=lambda r: r.expires_at)[:50]
    yearly = sum((d.total_fee for d, _ in rows if d.status == DomainStatus.ACTIVE), Decimal("0"))

    known = [e.extension for e in extension_crud.list_extensions(db, include_inactive=True)]
    ext_counts = Counter(_extension_of(d.domain_name, known) for d, _ in rows
                         if d.status in (DomainStatus.ACTIVE, DomainStatus.PENDING))

    now = datetime.now(timezone.utc)
    since7, since30 = now - timedelta(days=7), now - timedelta(days=30)
    s7 = db.scalar(select(func.count()).select_from(DomainSearch).where(DomainSearch.created_at >= since7)) or 0
    s30 = db.scalar(select(func.count()).select_from(DomainSearch).where(DomainSearch.created_at >= since30)) or 0
    with_free = db.scalar(select(func.count()).select_from(DomainSearch).where(
        DomainSearch.created_at >= since30, DomainSearch.available_count > 0)) or 0
    top = db.execute(
        select(DomainSearch.query, func.count().label("n"), func.max(DomainSearch.created_at))
        .where(DomainSearch.created_at >= since30)
        .group_by(DomainSearch.query).order_by(func.count().desc(), func.max(DomainSearch.created_at).desc())
        .limit(10)
    ).all()

    return DomainDashboard(
        counts={s.value: counts.get(s.value, 0) for s in DomainStatus} | {"TOTAL": len(rows)},
        yearly_value=yearly,
        pending_requests=pending,
        expiring=expiring,
        by_extension=[ExtensionCount(extension=e, count=c) for e, c in ext_counts.most_common()],
        searches_7_days=s7,
        searches_30_days=s30,
        top_searches=[SearchedName(name=q, searches=n, last_searched=t) for q, n, t in top],
        available_share=round(with_free / s30, 3) if s30 else None,
    )
