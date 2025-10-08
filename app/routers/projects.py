from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from app.schemas.project import ProjectCreate, ProjectRead, ProjectList, ProjectUpdate, ProjectMemberCreate, ProjectMemberRead, MemberRole
from app.services import project_service
from app.deps import get_db, get_current_user
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import uuid

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectRead)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # print("project name from req :",project_in.name)
    # print("project description from req :",project_in.description)
    try:
        project = project_service.create_project(
            db, owner_id=current_user.id, project_in=project_in)
        return project
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Failed to create project!!!")


@router.get("/", response_model=ProjectList)
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        items, total = project_service.list_projects(
            db, user_id=current_user.id, skip=skip, limit=limit, search=search)
        return {"items": items, "total": total}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Failed to get project list!!!")


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: uuid.UUID = Path(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        project = project_service.get_project(db, project_id)
    # ensure user is member
    # if you want, enforce membership check here; service already checks on some ops
        return project
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Failed to get project details!!!")


@router.put("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        project = project_service.update_project(
            db, project_id=project_id, user_id=current_user.id, project_in=payload)
        return project
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Failed to update project details!!!")


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    try:
        project_service.soft_delete_project(
            db, project_id=project_id, user_id=current_user.id)
        return {"detail": "deleted"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Failed to delete project!!!")


@router.post("/{project_id}/restore", response_model=ProjectRead)
def restore_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    try:
        project = project_service.restore_project(
            db, project_id=project_id, user_id=current_user.id)
        return project
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Failed to restore deleted project!!!")


@router.post("/{project_id}/archive", response_model=ProjectRead)
def archive_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:

        project = project_service.archive_project(
            db, project_id=project_id, user_id=current_user.id)
        return project
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Failed to archive project!!!")


@router.post("/{project_id}/transfer-ownership/{new_owner_id}", response_model=ProjectRead)
def transfer_ownership(
    project_id: uuid.UUID,
    new_owner_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    try:
        project = project_service.transfer_ownership(
            db, project_id=project_id, current_owner_id=current_user.id, new_owner_id=new_owner_id)
        return project
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Failed to transfer project ownership!!!")


@router.post("/{project_id}/members", response_model=ProjectMemberRead, status_code=201)
def add_member(
    project_id: uuid.UUID,
    payload: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        pm = project_service.add_member(
            db, project_id=project_id, user_id=payload.user_id, adder_id=current_user.id, role=payload.role)
        return pm
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Failed to add member to project!!!")


@router.delete("/{project_id}/members/{user_id}", status_code=204)
def remove_member(
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        project_service.remove_member(
            db, project_id=project_id, user_id=user_id, remover_id=current_user.id)
        return {"detail": "member removed"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Failed to delete member from project!!!")


@router.patch("/{project_id}/members/{user_id}/role", response_model=ProjectMemberRead)
def change_member_role(
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    role: str,  # will accept enum name
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # validate role string -> MemberRole
    # from app.models.project_member import MemberRole
    try:
        new_role = MemberRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")

    pm = project_service.change_member_role(
        db, project_id=project_id, target_user_id=user_id, changer_id=current_user.id, new_role=new_role)
    return pm
