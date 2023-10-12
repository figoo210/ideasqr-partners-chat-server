from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from config import get_db
import models, schemas

router = APIRouter()

# Message Reaction Endpoints


@router.post("/message_reactions/", response_model=schemas.MessageReaction)
def create_message_reaction(
    reaction: schemas.MessageReactionCreate, db: Session = Depends(get_db)
):
    db_reaction = models.MessageReaction(
        message_id=reaction.message_id,
        user_id=reaction.user_id,
        reaction=reaction.reaction,
        created_at=datetime.now(),
        last_modified_at=datetime.now(),
    )
    db.add(db_reaction)
    db.commit()
    db.refresh(db_reaction)
    return db_reaction


@router.get("/message_reactions/", response_model=List[schemas.MessageReaction])
def get_message_reactions(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    reactions = db.query(models.MessageReaction).offset(skip).limit(limit).all()
    return reactions


@router.get(
    "/message_reactions/{message_id}", response_model=List[schemas.MessageReaction]
)
def get_message_reaction(message_id: int, db: Session = Depends(get_db)):
    reaction = (
        db.query(models.MessageReaction)
        .filter(models.MessageReaction.id == message_id)
        .all()
    )

    if not reaction:
        raise HTTPException(status_code=404, detail="Message Reaction not found")
    return reaction


@router.put("/message_reactions/{reaction_id}", response_model=schemas.MessageReaction)
def update_message_reaction(
    reaction_id: int,
    reaction: schemas.MessageReactionUpdate,
    db: Session = Depends(get_db),
):
    db_reaction = (
        db.query(models.MessageReaction)
        .filter(models.MessageReaction.id == reaction_id)
        .first()
    )
    if not db_reaction:
        raise HTTPException(status_code=404, detail="Message Reaction not found")
    db_reaction.message_id = reaction.message_id
    db_reaction.user_id = reaction.user_id
    db_reaction.reaction = reaction.reaction
    db_reaction.last_modified_at = datetime.now()
    db.commit()
    db.refresh(db_reaction)
    return db_reaction


@router.delete("/message_reactions/{reaction_id}")
def delete_message_reaction(reaction_id: int, db: Session = Depends(get_db)):
    db_reaction = (
        db.query(models.MessageReaction)
        .filter(models.MessageReaction.id == reaction_id)
        .first()
    )
    if not db_reaction:
        raise HTTPException(status_code=404, detail="Message Reaction not found")
    db.delete(db_reaction)
    db.commit()
    return {"message": "Message Reaction deleted"}
