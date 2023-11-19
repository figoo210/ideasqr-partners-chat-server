from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from config import get_db
import models, schemas

router = APIRouter()


# API endpoint to create a role permission
@router.post("/role_permissions/", response_model=List[schemas.Role])
def create_role_permission(
    role_permission: schemas.RolePermission, db: Session = Depends(get_db)
):
    print("#################### role_permission: ", role_permission)
    # Delete existing permissions not in the array
    db.query(models.RolePermission) \
        .filter(models.RolePermission.role == role_permission.role) \
        .filter(models.RolePermission.permission.notin_(role_permission.permissions)) \
        .delete(synchronize_session=False)
    db.commit()
    # Loop over permissions array
    for permission in role_permission.permissions:
        # Check if permission exists for the role
        existing_permission = db.query(models.RolePermission) \
            .filter(models.RolePermission.role == role_permission.role) \
            .filter(models.RolePermission.permission == permission) \
            .first()

        if existing_permission:
            continue  # Skip if permission already exists for the role

        # Create new role permission
        new_role_permission = models.RolePermission(
            role=role_permission.role,
            permission=permission
        )
        db.add(new_role_permission)

        db.commit()
        db.refresh(new_role_permission)

    roles = db.query(models.Role).all()
    return roles



@router.get("/role_permissions/", response_model=schemas.RolePermissionResponse)
def get_role_permissions(db: Session = Depends(get_db)):
    # Query the database for all RolePermission objects
    role_permissions = db.query(models.RolePermission).all()

    # Map the results to RolePermissionResponses objects
    role_permissions_response = schemas.RolePermissionResponse(
        roles_permissions=[role_permission for role_permission in role_permissions]
    )
    return role_permissions_response


# Role Endpoints


@router.post("/roles/", response_model=schemas.Role)
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    db_role = models.Role(
        role=role.role, created_at=datetime.now(), last_modified_at=datetime.now()
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


@router.get("/roles/", response_model=List[schemas.Role])
def get_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    roles = db.query(models.Role).offset(skip).limit(limit).all()
    return roles


@router.get("/roles/{role_name}", response_model=schemas.Role)
def get_role(role_name: str, db: Session = Depends(get_db)):
    role = db.query(models.Role).filter(models.Role.role == role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.put("/roles/{role_name}", response_model=schemas.Role)
def update_role(
    role_name: str, role: schemas.RoleUpdate, db: Session = Depends(get_db)
):
    db_role = db.query(models.Role).filter(models.Role.role == role_name).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    db_role.role = role.role
    db_role.last_modified_at = datetime.now()
    db.commit()
    db.refresh(db_role)
    return db_role


@router.delete("/roles/{role_name}")
def delete_role(role_name: str, db: Session = Depends(get_db)):
    db_role = db.query(models.Role).filter(models.Role.role == role_name).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(db_role)
    db.commit()
    return {"message": "Role deleted"}


# Permission Endpoints


@router.post("/permissions/", response_model=schemas.Permission)
def create_permission(
    permission: schemas.PermissionCreate, db: Session = Depends(get_db)
):
    db_permission = models.Permission(
        permission=permission.permission,
        created_at=datetime.now(),
        last_modified_at=datetime.now(),
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


@router.get("/permissions/", response_model=List[schemas.Permission])
def get_permissions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    permissions = db.query(models.Permission).offset(skip).limit(limit).all()
    return permissions


@router.get("/permissions/{permission_name}", response_model=schemas.Permission)
def get_permission(permission_name: str, db: Session = Depends(get_db)):
    permission = (
        db.query(models.Permission)
        .filter(models.Permission.permission == permission_name)
        .first()
    )
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission


@router.put("/permissions/{permission_name}", response_model=schemas.Permission)
def update_permission(
    permission_name: str,
    permission: schemas.PermissionUpdate,
    db: Session = Depends(get_db),
):
    db_permission = (
        db.query(models.Permission)
        .filter(models.Permission.permission == permission_name)
        .first()
    )
    if not db_permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    db_permission.permission = permission.permission
    db_permission.last_modified_at = datetime.now()
    db.commit()
    db.refresh(db_permission)
    return db_permission


@router.delete("/permissions/{permission_name}")
def delete_permission(permission_name: str, db: Session = Depends(get_db)):
    db_permission = (
        db.query(models.Permission)
        .filter(models.Permission.permission == permission_name)
        .first()
    )
    if not db_permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    db.delete(db_permission)
    db.commit()
    return {"message": "Permission deleted"}
