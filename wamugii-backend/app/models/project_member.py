import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProjectRole(str, enum.Enum):
    """What a member does on one specific project."""

    TEAM_LEAD = "TEAM_LEAD"
    PROGRAMMER = "PROGRAMMER"
    TESTER = "TESTER"
    RESEARCHER = "RESEARCHER"
    DESIGNER = "DESIGNER"


class ProjectMember(Base):
    """
    One person's membership of one project, with the role they hold on it.

    A user can be on many projects with a different role on each, but only one
    role per project -- hence the unique constraint on (project_id, user_id).

    That constraint and the soft delete interact: a removed member keeps their
    row with `is_active = False`, so re-adding them cannot insert a second row.
    `crud.project_member.add_or_reactivate` reactivates the existing row
    instead, which also preserves the original `assigned_at` as a record of
    when the person first joined.
    """

    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_members_project_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    # A TEAM_MEMBER or STAFF user -- validated in api/v1/project_members.py.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    project_role: Mapped[ProjectRole] = mapped_column(
        Enum(ProjectRole), default=ProjectRole.PROGRAMMER, index=True
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # The ADMIN/STAFF user who made the assignment.
    assigned_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    project = relationship("Project", back_populates="members")
    user = relationship("User", foreign_keys=[user_id], back_populates="project_memberships")
    assigner = relationship("User", foreign_keys=[assigned_by])
