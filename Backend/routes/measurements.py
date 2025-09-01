from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(prefix="/measurements", tags=["Measurements"])

@router.get("/", response_model=list[schemas.MeasurementOut])
def get_measurements(db: Session = Depends(get_db)):
    return db.query(models.Measurement).limit(100).all()  # limit for performance
