from pydantic import BaseModel
import uuid
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    backlog = "backlog"
    todo = "todo"
    in_progress = "in_progress"
    done = "done"

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    project_id: uuid.UUID 
    assignee_id: Optional[uuid.UUID] = None

class TaskRead(TaskBase):
    id: uuid.UUID 
    project_id: uuid.UUID 
    assignee_id: Optional[uuid.UUID]
    status: TaskStatus

    class Config:
        orm_mode = True
