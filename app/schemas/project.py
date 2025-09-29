from pydantic import BaseModel
import uuid
from typing import Optional, List
from app.schemas.user import UserRead

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectRead(ProjectBase):
    id: uuid.UUID 
    owner_id: uuid.UUID 

    class Config:
        orm_mode = True
