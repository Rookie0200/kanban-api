from pydantic import BaseModel
from typing import Optional, List
from app.schemas.user import UserRead

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectRead(ProjectBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
