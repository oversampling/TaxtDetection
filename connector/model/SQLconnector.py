from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(filename='db.log', encoding='utf-8', level=logging.DEBUG)

SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
# class SQLconnector:
#     def __init__(self, dbname):
#         self.conn = sqlite3.connect(f'{dbname}.db')
#         self.cursor = self.conn.cursor()
#         logging.info("Open database successfully")

# class DetectionCache(SQLconnector):
#     def __init__(self):
#         super().__init__("detection_cache")
#         self.cursor.execute("""
#                             CREATE TABLE IF NOT EXISTS DETECTION_CACHE 
#                             (
#                                 tag VARCHAR(20) PRIMARY KEY,
#                                 isDetected BOOLEAN
#                             )
#                             """)


#     def addTagDetectionCache(self, tag):
#         print("INSERT INTO DETECTION_CACHE (tag, isDetected) VALUES (\"{tag}\", false)")
#         # self.cursor.execute(f"INSERT INTO DETECTION_CACHE (tag, isDetected) VALUES (\"{tag}\", false)")
#         self.conn.commit()
#         return True

#     def changeTagDetection(self, tag, isDetected):
#         self.cursor.execute(f"UPDATE DETECTION_CACHE SET isDetected = {isDetected} WHERE tag = \"{tag}\"")
#         self.conn.commit()
#         return True
    
#     def getTagStatus(self, tag: str):
#         self.cursor.execute(f"SELECT isDetected FROM DETECTION_CACHE WHERE tag = \"{tag}\"")
#         return self.cursor.fetchone()[0]
    
#     def removeTagDetection(self, tags: list[str]):
#         sql_tags = ",".join([f"\"{tag}\"" for tag in tags])
#         self.cursor.execute(f"DELETE FROM DETECTION_CACHE WHERE tag IN ({sql_tags}) AND EXISTS(SELECT * FROM DETECTION_CACHE WHERE tag IN ({sql_tags}))")
#         self.conn.commit()
#         return True
    
#     def getAllTags(self):
#         self.cursor.execute(f"SELECT tag FROM DETECTION_CACHE")
#         return self.cursor.fetchall()
