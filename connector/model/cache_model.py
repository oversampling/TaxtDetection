from model.SQLconnector import Base
from sqlalchemy import Boolean, Column, String

class DetectionCache(Base):
    __tablename__ = "DETECTION_CACHE"
    tag = Column(String, primary_key=True)
    isDetected = Column(Boolean)

class CookiesCache(Base):
    __tablename__ = "COOKIES_CACHE"
    username = Column(String, primary_key=True)
    cookie = Column(String)

class UserList(Base):
    __tablename__ = "USER_LIST"
    db_id = Column(String, primary_key=True)
    name = Column(String)
    empl_id = Column(String)
    department = Column(String)
