from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class MeasurementBase(BaseModel):
    depth: float
    temperature: Optional[float]
    salinity: Optional[float]

class MeasurementOut(MeasurementBase):
    id: int
    class Config:
        orm_mode = True

class ProfileBase(BaseModel):
    date: datetime
    latitude: float
    longitude: float
    platform: str

class ProfileOut(ProfileBase):
    id: int
    measurements: List[MeasurementOut] = []
    class Config:
        orm_mode = True
