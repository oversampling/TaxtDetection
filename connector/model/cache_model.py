from model.SQLconnector import Base
from sqlalchemy import Boolean, Column, String

class DetectionCache(Base):
    __tablename__ = "DETECTION_CACHE"
    tag = Column(String, primary_key=True)
    isDetected = Column(Boolean)

