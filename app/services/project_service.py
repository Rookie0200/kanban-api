from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project import ProjectCreate

def create_project(db: Session, owner_id: int, project_in: ProjectCreate):
    project = Project(name=project_in.name, description=project_in.description, owner_id=owner_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def get_project(db: Session, project_id: int):
    return db.get(Project, project_id)
