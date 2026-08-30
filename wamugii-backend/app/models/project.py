import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    PENDING = "PENDING"
    PLANNING = "PLANNING"
    IN_PROGRESS = "IN_PROGRESS"
    ON_HOLD = "ON_HOLD"
    TESTING = "TESTING"
    CLIENT_REVIEW = "CLIENT_REVIEW"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ProjectPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    quote_request_id: Mapped[int | None] = mapped_column(
        ForeignKey("quote_requests.id"), nullable=True, index=True
    )
    service_id: Mapped[int | None] = mapped_column(
        ForeignKey("services.id"), nullable=True, index=True
    )

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)

    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus), default=ProjectStatus.PENDING, index=True
    )
    priority: Mapped[ProjectPriority] = mapped_column(
        Enum(ProjectPriority), default=ProjectPriority.MEDIUM, index=True
    )

    budget: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    client = relationship("User")
    quote_request = relationship("QuoteRequest")
    service = relationship("Service")
    milestones = relationship("ProjectMilestone", back_populates="project")
    files = relationship("ProjectFile", back_populates="project")
