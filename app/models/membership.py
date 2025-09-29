import uuid
from sqlalchemy.dialects.postgresql import UUID 
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProjectMember(Base):
    __tablename__ = "project_members"
    # id = Column(Integer, primary_key=True, index=True)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(String, default="member")  # e.g. owner, member
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="memberships")

    __table_args__ = (UniqueConstraint("project_id", "user_id", name="_project_user_uc"),)
