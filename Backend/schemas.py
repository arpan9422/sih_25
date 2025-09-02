from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class MeasurementBase(BaseModel):
    depth: float
    temperature: Optional[float]
    salinity: Optional[float]

class MeasurementOut(MeasurementBase):
    id: Optional[int] = None  # make optional since DB has no id
    class Config:
        orm_mode = True

class ProfileBase(BaseModel):
    date: datetime
    latitude: float
    longitude: float
    platform: str

class ProfileOut(ProfileBase):
    id: Optional[int] = None  # make optional
    measurements: List[MeasurementOut] = []
    class Config:
        orm_mode = True
