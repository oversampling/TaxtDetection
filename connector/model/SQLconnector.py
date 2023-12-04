import sqlite3
import logging

logging.basicConfig(filename='db.log', encoding='utf-8', level=logging.DEBUG)

class SQLconnector:
    def __init__(self, dbname):
        self.conn = sqlite3.connect(f'{dbname}.db')
        self.cursor = self.conn.cursor()
        logging.log("Open database successfully")

class DetectionCache(SQLconnector):
    def __init__(self):
        super("cache.db")
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS DETECTION_CACHE 
                            (
                                tag VARCHAR(20) PRIMARY KEY,
                                isDetected BOOLEAN
                            )
                            """)


    def addTagDetectionCache(self, tag):
        self.cursor.execute(f"INSERT INTO DETECTION_CACHE (tag, isDetected) VALUES ({tag}, false)")
        self.conn.commit()
        return True

    def changeTagDetection(self, tag, isDetected):
        self.cursor.execute(f"UPDATE DETECTION_CACHE SET isDetected = {isDetected} WHERE tag = {tag}")
        self.conn.commit()
        return True
        