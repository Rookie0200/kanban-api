from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.task import TaskCreate, TaskRead, TaskStatus
from app.services import task_service
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskRead)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Authorization checks (e.g., is user member of project) should be here
    task = task_service.create_task(db, task_in=task_in)
    return task

@router.patch("/status/{task_id}/", response_model=TaskRead)
def update_status(task_id: int, status: TaskStatus, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    task = task_service.update_task_status(db, task_id=task_id, status=status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
