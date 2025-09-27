from sqlalchemy.orm import Session
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate

def create_task(db: Session, task_in: TaskCreate):
    task = Task(title=task_in.title, description=task_in.description, project_id=task_in.project_id,
                assignee_id=task_in.assignee_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def update_task_status(db: Session, task_id: int, status: TaskStatus):
    task = db.get(Task, task_id)
    if not task:
        return None
    task.status = status
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
