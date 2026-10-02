from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    short_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # The "explore" detail: a longer write-up and a bullet list, both optional
    # and both added alongside the original short_description/description rather
    # than replacing them, so every existing service keeps rendering unchanged.
    long_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSON-encoded list of strings, as Text for SQLite/PostgreSQL portability --
    # see models/service_question.py for the same reasoning.
    features: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    icon: Mapped[str | None] = mapped_column(String(255), nullable=True)
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price_from: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    questions = relationship(
        "ServiceQuestion",
        back_populates="service",
        order_by="ServiceQuestion.display_order, ServiceQuestion.id",
    )
