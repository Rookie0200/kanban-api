from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from app.models.project import Project, ProjectStatus, ProjectMember
from app.schemas.project import ProjectCreate, MemberRole, ProjectUpdate
import uuid
from fastapi import HTTPException
from datetime import datetime


def create_project(db: Session, owner_id: uuid.UUID, project_in: ProjectCreate) -> Project:
    project = Project(
        name=project_in.name.strip(),
        description=project_in.description,
        owner_id=owner_id,
        status=ProjectStatus.active,
    )
    db.add(project)
    db.flush()  # assign project.id

    # add owner as member automatically
    owner_member = ProjectMember(
        project_id=project.id, user_id=owner_id, role=MemberRole.owner)
    db.add(owner_member)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not create project")
    db.refresh(project)
    return project


def get_project(db: Session, project_id: uuid.UUID, *, include_deleted: bool = False) -> Project:
    project = db.get(Project, project_id)
    if not project or (project.is_deleted and not include_deleted):
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def list_projects(
    db: Session,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 25,
    search: Optional[str] = None,
) -> Tuple[List[Project], int]:
    # user must be a member to see project (join members)
    query = db.query(Project).join(ProjectMember).filter(
        ProjectMember.user_id == user_id,
        Project.is_deleted == False
    ).distinct()

    if search:
        query = query.filter(Project.name.ilike(f"%{search}%"))

    total = query.count()
    items = query.order_by(Project.created_at.desc()
                           ).offset(skip).limit(limit).all()
    return items, total


def update_project(db: Session, project_id: uuid.UUID, user_id: uuid.UUID, project_in: ProjectUpdate) -> Project:
    project = get_project(db, project_id)
    # only owner or admin can update project (we'll check membership)
    member = db.query(ProjectMember).filter_by(
        project_id=project.id, user_id=user_id).first()
    if not member or member.role not in (MemberRole.owner, MemberRole.admin):
        raise HTTPException(
            status_code=403, detail="Not authorized to update project")

    if project_in.name is not None:
        project.name = project_in.name.strip()
    if project_in.description is not None:
        project.description = project_in.description
    if project_in.status is not None:
        project.status = project_in.status

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to update project")
    db.refresh(project)
    return project


def soft_delete_project(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> None:
    project = get_project(db, project_id)
    if project.owner_id != user_id:
        raise HTTPException(
            status_code=403, detail="Only owner can delete project")

    project.is_deleted = True
    project.deleted_at = datetime.utcnow()
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to delete project")


def restore_project(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> Project:
    project = get_project(db, project_id, include_deleted=True)
    if project.owner_id != user_id:
        raise HTTPException(
            status_code=403, detail="Only owner can restore project")
    if not project.is_deleted:
        raise HTTPException(status_code=400, detail="Project is not deleted")

    project.is_deleted = False
    project.deleted_at = None
    db.commit()
    db.refresh(project)
    return project


def archive_project(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> Project:
    project = get_project(db, project_id)
    member = db.query(ProjectMember).filter_by(
        project_id=project.id, user_id=user_id).first()
    if not member or member.role not in (MemberRole.owner, MemberRole.admin):
        raise HTTPException(
            status_code=403, detail="Not authorized to archive project")

    project.status = ProjectStatus.archived
    db.commit()
    db.refresh(project)
    return project


def transfer_ownership(db: Session, project_id: uuid.UUID, current_owner_id: uuid.UUID, new_owner_id: uuid.UUID) -> Project:
    project = get_project(db, project_id)
    if project.owner_id != current_owner_id:
        raise HTTPException(
            status_code=403, detail="Only current owner can transfer ownership")

    # ensure new_owner is a member (add if not)
    member = db.query(ProjectMember).filter_by(
        project_id=project.id, user_id=new_owner_id).first()
    if not member:
        new_member = ProjectMember(
            project_id=project.id, user_id=new_owner_id, role=MemberRole.owner)
        db.add(new_member)
    else:
        member.role = MemberRole.owner

    # demote previous owner to admin (or member)
    prev_member = db.query(ProjectMember).filter_by(
        project_id=project.id, user_id=current_owner_id).first()
    if prev_member:
        prev_member.role = MemberRole.admin

    project.owner_id = new_owner_id
    db.commit()
    db.refresh(project)
    return project


def add_member(db: Session, project_id: uuid.UUID, user_id: uuid.UUID, adder_id: uuid.UUID, role: MemberRole = MemberRole.member) -> ProjectMember:
    project = get_project(db, project_id)
    # only owner/admin can add members
    adder = db.query(ProjectMember).filter_by(
        project_id=project.id, user_id=adder_id).first()
    if not adder or adder.role not in (MemberRole.owner, MemberRole.admin):
        raise HTTPException(
            status_code=403, detail="Not authorized to add members")

    existing = db.query(ProjectMember).filter_by(
        project_id=project.id, user_id=user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member")

    pm = ProjectMember(project_id=project.id, user_id=user_id, role=role)
    db.add(pm)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to add member")
    db.refresh(pm)
    return pm


def remove_member(db: Session, project_id: uuid.UUID, user_id: uuid.UUID, remover_id: uuid.UUID) -> None:
    project = get_project(db, project_id)
    remover = db.query(ProjectMember).filter_by(
        project_id=project.id, user_id=remover_id).first()
    if not remover or remover.role not in (MemberRole.owner, MemberRole.admin):
        raise HTTPException(
            status_code=403, detail="Not authorized to remove members")

    member = db.query(ProjectMember).filter_by(
        project_id=project.id, user_id=user_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.role == MemberRole.owner:
        raise HTTPException(
            status_code=400, detail="Cannot remove project owner")

    db.delete(member)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to remove member")


def change_member_role(db: Session, project_id: uuid.UUID, target_user_id: uuid.UUID, changer_id: uuid.UUID, new_role: MemberRole) -> ProjectMember:
    project = get_project(db, project_id)
    changer = db.query(ProjectMember).filter_by(
        project_id=project.id, user_id=changer_id).first()
    if not changer or changer.role not in (MemberRole.owner, MemberRole.admin):
        raise HTTPException(
            status_code=403, detail="Not authorized to change roles")

    member = db.query(ProjectMember).filter_by(
        project_id=project.id, user_id=target_user_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.role == MemberRole.owner and new_role != MemberRole.owner:
        # prevent demoting owner via this endpoint (owner transfer should be explicit)
        raise HTTPException(
            status_code=400, detail="Use transfer ownership to change owner")

    member.role = new_role
    db.commit()
    db.refresh(member)
    return member
