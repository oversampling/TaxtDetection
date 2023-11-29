import threading
import cv2
import numpy as np
import requests
import time
import os
from dotenv import load_dotenv
import logging

from model.detect import Coords, Detect
from model.recogn import Recogn

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
    def __init__(self, url, tag):
        super().__init__()
        self.url = url
        self.tag = tag
        self.resp = []
        self._stop_event = threading.Event()

    def run(self):
        # video = cv2.VideoCapture(0)
        model = Detect("best.pt")

        # initial_frame = 
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
                            processedTag = ''.join([char for char in self.tag if char.isalpha() or char.isdigit()])
                            processedTag = processedTag.lower()
                            if resultText == processedTag:
                                print("!!!!!!!!!!!!!!!!!!!!!!!!DETECTED!!!!!!!!!!!!!!!!!!!!!!!!!!")
                                break
                            self.resp.append({"text": result[1], "confidence": result[2]})
                _, frame = cv2.imencode('.jpeg', frame)
                time.sleep(0.3)
        except KeyboardInterrupt:
            pass
        finally:
            pass
        pass
    
    def stop(self):
        self._stop_event.set()