from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Draft
from app.schemas import DraftCreate, DraftDetail, DraftSummary

router = APIRouter(prefix="/api/drafts", tags=["drafts"])


@router.post("", response_model=DraftDetail, status_code=201)
def create_draft(draft_in: DraftCreate, db: Session = Depends(get_db)) -> Draft:
    draft = Draft(**draft_in.model_dump())
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


@router.get("", response_model=list[DraftSummary])
def list_drafts(db: Session = Depends(get_db)) -> list[Draft]:
    return db.query(Draft).order_by(Draft.created_at.desc()).all()


@router.get("/{draft_id}", response_model=DraftDetail)
def get_draft(draft_id: int, db: Session = Depends(get_db)) -> Draft:
    draft = db.get(Draft, draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft


@router.delete("/{draft_id}", status_code=204)
def delete_draft(draft_id: int, db: Session = Depends(get_db)) -> None:
    draft = db.get(Draft, draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    db.delete(draft)
    db.commit()
