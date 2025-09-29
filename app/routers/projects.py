from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.project import ProjectCreate, ProjectRead
from app.services import project_service
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectRead)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # print("project name from req :",project_in.name)
    # print("project description from req :",project_in.description)
    project = project_service.create_project(db, owner_id=current_user.id, project_in=project_in)
    return project
