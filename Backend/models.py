from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    platform = Column(String)

    measurements = relationship("Measurement", back_populates="profile")

class Measurement(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    depth = Column(Float)
    temperature = Column(Float)
    salinity = Column(Float)

    profile = relationship("Profile", back_populates="measurements")
