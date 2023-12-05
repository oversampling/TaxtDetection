import threading
import cv2
import numpy as np
import requests
import time
import os
from dotenv import load_dotenv
import logging
import pyttsx3
from sqlalchemy.orm import Session
from model import cache_controller

from controller.detect import Coords, Detect
from controller.recogn import Recogn

logging.basicConfig(filename='fetcher.log', encoding='utf-8', level=logging.DEBUG)

load_dotenv()

RECOGN_URL = os.getenv("RECOGN_URL")

class ImageFetcher(threading.Thread):
    def __init__(self, url, session_id, interval=5):
        super().__init__()
        self.url = url
        self.interval = interval
        self.session_id = session_id
        self._stop_event = threading.Event()
    
    def run(self):
        while not self._stop_event.is_set():
            try:
                response = requests.get(self.url)
                with open(f"static/img-{self.session_id}.jpg", "wb") as f:
                    f.write(response.content)
                # Send to recognition
            except Exception as e:
                print(f"Error fetching image: {e}")
            finally:
                pass
            # Wait for the specified interval
            time.sleep(self.interval)
    
    def stop(self):
        self._stop_event.set()

class Stream(threading.Thread):
    def __init__(self, url: str, tags: list[str], db: Session):
        super().__init__()
        self.url: str = url
        self.tags: list[str] = []
        self.db = db
        for tag in tags:
            processedTag = ''.join([char for char in tag if char.isalpha() or char.isdigit()])
            processedTag = processedTag.lower()
            self.tags.append(processedTag)
            cache_controller.add_tag(self.db, processedTag)
        self.resp = []
        self._stop_event = threading.Event()

    def run(self):
        # video = cv2.VideoCapture(0)
        model = Detect("best.pt")
        detected_tag = {tag: False for tag in self.tags}
        voice_engine = pyttsx3.init()
        recog = Recogn()
        try:
            while not self._stop_event.is_set():
                img_resp = requests.get(self.url) 
                img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8) 
                frame = cv2.imdecode(img_arr, -1) 
                cv2.imwrite('img.jpg', frame)
                coords: list[Coords] = model.detect('img.jpg', saveImagePath='img.jpg')
                if len(coords) > 0:
                    image = coords[0].cropImage(imgPath="img.jpg")
                    recog.preprocess(image, saveImagePath="img.jpg")
                    results = recog.read("img.jpg").result                    
                    if len(results) != 0:
                        for result in results:
                            resultText: str = result[1]
                            resultText = resultText.replace(" ", "")
                            resultText = resultText.lower()
                            # Remove all non-alphanumeric characters
                            resultText = ''.join([char for char in resultText if char.isalpha() or char.isdigit()])
                            if resultText in self.tags:
                                if detected_tag[resultText] != True:
                                    detected_tag[resultText] = True
                                    processedResultText = ' '.join(c for c in resultText)
                                    voice_response = f"Detected {processedResultText}"
                                    voice_engine.say(voice_response)
                                    voice_engine.runAndWait()
                                    cache_controller.change_tag(self.db, resultText, True)
                                    logging.info(f"Detected: {resultText} With Confidence of {result[2]}")
                                break
                            self.resp.append({"text": resultText, "confidence": result[2]})
                _, frame = cv2.imencode('.jpeg', frame)
                time.sleep(0.3)
        except KeyboardInterrupt:
            pass
        finally:
            pass
        pass
    
    def stop(self):
        self._stop_event.set()