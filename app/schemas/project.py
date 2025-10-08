from pydantic import BaseModel
import uuid
from typing import Optional, List
from app.schemas.user import UserRead
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime
from app.models.project import ProjectStatus
from app.models.membership import MemberRole

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name:Optional[str] = Field(None, max_length=255)
    description:Optional[str] = None
    status:Optional[ProjectStatus] = None

class ProjectMemberBase(BaseModel):
    user_id:uuid.UUID
    role:Optional[MemberRole]= MemberRole.member

class ProjectMemberCreate(BaseModel):
    pass

class ProjectMemberRead(ProjectMemberBase):
    id:uuid.UUID
    joined_at:datetime

    class Config:
        orm_mode=True


class ProjectRead(ProjectBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    status: ProjectStatus
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    members: Optional[List[ProjectMemberRead]] = [] 

    class Config:
        orm_mode = True

class ProjectList(BaseModel):
    items:List[ProjectRead]
    total:int
