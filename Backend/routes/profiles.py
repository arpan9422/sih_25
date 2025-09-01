from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.get("/", response_model=list[schemas.ProfileOut])
def get_profiles(db: Session = Depends(get_db)):
    return db.query(models.Profile).all()

@router.get("/{profile_id}", response_model=schemas.ProfileOut)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    return db.query(models.Profile).filter(models.Profile.id == profile_id).first()
