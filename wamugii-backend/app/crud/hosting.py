from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.hosting import BillingCycle, HostingAccount, HostingPlan, HostingStatus
from app.schemas.hosting import (
    HostingAccountCreate,
    HostingAccountUpdate,
    HostingPlanCreate,
    HostingPlanUpdate,
)


def _add_months(start: date, months: int) -> date:
    """
    Shift a date by whole months, clamping the day to the target month's length.

    Needed because a 31st start date has no 31st to land on in the next month —
    31 Jan + 1 month becomes 28/29 Feb rather than rolling into March, which is
    how billing anniversaries are normally read.
    """
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    # Day 1 of the following month, minus a day, is the last day of this one.
    if month == 12:
        last_day = (date(year + 1, 1, 1) - timedelta(days=1)).day
    else:
        last_day = (date(year, month + 1, 1) - timedelta(days=1)).day
    return date(year, month, min(start.day, last_day))


def compute_next_billing_date(start_date: date | None, cycle: BillingCycle) -> date | None:
    """One cycle on from `start_date`. None in, None out."""
    if start_date is None:
        return None
    return _add_months(start_date, 12 if cycle == BillingCycle.YEARLY else 1)


# --- plans ------------------------------------------------------------------


def list_plans(db: Session, *, include_inactive: bool = False) -> list[HostingPlan]:
    query = select(HostingPlan)
    if not include_inactive:
        query = query.where(HostingPlan.is_active.is_(True))
    return list(
        db.scalars(query.order_by(HostingPlan.display_order.asc(), HostingPlan.id.asc())).all()
    )


def get_plan(db: Session, plan_id: int) -> HostingPlan | None:
    return db.get(HostingPlan, plan_id)


def create_plan(db: Session, data: HostingPlanCreate) -> HostingPlan:
    plan = HostingPlan(**data.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def update_plan(db: Session, plan: HostingPlan, data: HostingPlanUpdate) -> HostingPlan:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    db.commit()
    db.refresh(plan)
    return plan


def deactivate_plan(db: Session, plan: HostingPlan) -> HostingPlan:
    plan.is_active = False
    db.commit()
    db.refresh(plan)
    return plan


def count_plans(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(HostingPlan)) or 0


# --- accounts ---------------------------------------------------------------


def get_account(db: Session, account_id: int) -> HostingAccount | None:
    return db.get(HostingAccount, account_id)


def list_accounts(
    db: Session,
    *,
    limit: int = 20,
    offset: int = 0,
    status: HostingStatus | None = None,
    plan_id: int | None = None,
    client_id: int | None = None,
    search: str | None = None,
    include_inactive: bool = False,
) -> list[HostingAccount]:
    query = select(HostingAccount)
    if not include_inactive:
        query = query.where(HostingAccount.is_active.is_(True))
    if status is not None:
        query = query.where(HostingAccount.status == status)
    if plan_id is not None:
        query = query.where(HostingAccount.plan_id == plan_id)
    if client_id is not None:
        query = query.where(HostingAccount.client_id == client_id)
    if search:
        query = query.where(func.lower(HostingAccount.domain).contains(search.lower()))
    query = query.order_by(HostingAccount.created_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(query).all())


def create_account(db: Session, data: HostingAccountCreate) -> HostingAccount:
    payload = data.model_dump()
    # Derived, never taken from the request: the caller supplies the start date
    # and the cycle, the anniversary follows from them.
    payload["next_billing_date"] = compute_next_billing_date(
        payload.get("start_date"), payload["billing_cycle"]
    )
    account = HostingAccount(**payload)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def update_account(db: Session, account: HostingAccount, data: HostingAccountUpdate) -> HostingAccount:
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(account, field, value)

    # Recompute the anniversary whenever either input to it moved, unless the
    # caller set it explicitly in the same request.
    if ("start_date" in updates or "billing_cycle" in updates) and "next_billing_date" not in updates:
        account.next_billing_date = compute_next_billing_date(
            account.start_date, account.billing_cycle
        )

    db.commit()
    db.refresh(account)
    return account


def deactivate_account(db: Session, account: HostingAccount) -> HostingAccount:
    account.is_active = False
    db.commit()
    db.refresh(account)
    return account


def get_accounts_expiring_soon(db: Session, days: int = 7) -> list[HostingAccount]:
    """
    Active accounts whose expiry falls within the next `days`.

    Intended for an expiry-reminder sweep. Nothing calls it on a schedule yet —
    there is no scheduler in this project — so it exists for an admin view or a
    future job rather than firing on its own.
    """
    today = date.today()
    horizon = today + timedelta(days=days)
    return list(
        db.scalars(
            select(HostingAccount)
            .where(
                HostingAccount.is_active.is_(True),
                HostingAccount.status == HostingStatus.ACTIVE,
                HostingAccount.expires_at.is_not(None),
                HostingAccount.expires_at >= today,
                HostingAccount.expires_at <= horizon,
            )
            .order_by(HostingAccount.expires_at.asc())
        ).all()
    )


def list_accounts_for_client(
    db: Session,
    client_id: int,
    *,
    include_inactive: bool = False,
) -> list[HostingAccount]:
    """The client portal's own list — scoped by client_id, never by anything else."""
    query = select(HostingAccount).where(HostingAccount.client_id == client_id)
    if not include_inactive:
        query = query.where(HostingAccount.is_active.is_(True))
    return list(db.scalars(query.order_by(HostingAccount.created_at.desc())).all())


def get_account_for_client(db: Session, account_id: int, client_id: int) -> HostingAccount | None:
    """None for anything that isn't this client's, which the router turns into 404."""
    return db.scalar(
        select(HostingAccount).where(
            HostingAccount.id == account_id,
            HostingAccount.client_id == client_id,
            HostingAccount.is_active.is_(True),
        )
    )


def count_active_accounts(db: Session) -> int:
    """SQL COUNT for the admin dashboard's hosting block."""
    return (
        db.scalar(
            select(func.count())
            .select_from(HostingAccount)
            .where(
                HostingAccount.status == HostingStatus.ACTIVE,
                HostingAccount.is_active.is_(True),
            )
        )
        or 0
    )
