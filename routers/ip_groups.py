from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from config import get_db
import models, schemas

router = APIRouter()

# IP Groups Endpoints


@router.post("/ip_groups")
def create_ip_group(ip_group: schemas.IPGroupBase, db: Session = Depends(get_db)):
    try:
        new_ip_group = models.IPGroup(ip=ip_group.ip, name=ip_group.name)
        db.add(new_ip_group)
        db.commit()
        db.refresh(new_ip_group)
        return {"message": "IP Group created successfully"}
    except:
        db.rollback()
        return {"message": "Failed to create IP Group"}


@router.get("/ip_groups")
def get_ip_groups(db: Session = Depends(get_db)):
    ip_groups = db.query(models.IPGroup).all()
    return ip_groups


@router.put("/ip_groups")
def update_ip_group(
    updated_ip_group: schemas.IPGroupBase, db: Session = Depends(get_db)
):
    ip_group = (
        db.query(models.IPGroup)
        .filter(models.IPGroup.ip == updated_ip_group.ip)
        .first()
    )
    if ip_group:
        ip_group.name = updated_ip_group.name
        db.commit()
        db.refresh(ip_group)
        return {"message": "IP Group updated successfully"}
    else:
        return {"message": "IP Group not found"}


@router.delete("/ip_groups/{ip}")
def delete_ip_group(ip: str, db: Session = Depends(get_db)):
    ip_group = db.query(models.IPGroup).filter(models.IPGroup.ip == ip).first()
    if ip_group:
        db.delete(ip_group)
        db.commit()
        return {"message": "IP Group deleted successfully"}
    else:
        return {"message": "IP Group not found"}
