import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    STAFF = "STAFF"
    CLIENT = "CLIENT"
    # A project collaborator (intern, contractor, team member). They only ever
    # see the projects they are explicitly assigned to, and never any
    # client-identifying or billing field -- see api/v1/team.py and
    # schemas/team.py, which are the only read surface they are given.
    TEAM_MEMBER = "TEAM_MEMBER"


class ApprovalStatus(str, enum.Enum):
    """
    Whether an account has been cleared to use the app.

    Only team-member self-registrations start PENDING; every other account
    (and every account that existed before this column) is APPROVED, so the
    gate in `deps.get_current_active_user` is a no-op for them.
    """

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.CLIENT)
    # server_default as well as default: the migration backfills existing rows
    # through it, and a row inserted by raw SQL still lands APPROVED rather
    # than NULL (which the gate would have to guess about).
    approval_status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus),
        default=ApprovalStatus.APPROVED,
        server_default=ApprovalStatus.APPROVED.value,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    uploaded_files = relationship("ProjectFile", back_populates="uploaded_by_user")
    project_memberships = relationship(
        "ProjectMember",
        back_populates="user",
        foreign_keys="ProjectMember.user_id",
    )
