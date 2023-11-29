import threading
import cv2
import numpy as np
import requests
import time
import imutils
class ImageFetcher(threading.Thread):
    def __init__(self, url, session_id, interval=5):
        super().__init__()
        self.url = url
        self.interval = interval
        self.session_id = session_id
        self._stop_event = threading.Event()
    
    def run(self):
        while not self._stop_event.is_set():
            # Fetch image from URL
            try:
                response = requests.get(self.url)
                with open(f"static/img-{self.session_id}.jpg", "wb") as f:
                    f.write(response.content)
                files = {'file': open(f'img-{self.session_id}.jpg', 'rb')}
                # Send to recognition
            except Exception as e:
                print(f"Error fetching image: {e}")
            
            # Wait for the specified interval
            time.sleep(self.interval)
    
    def stop(self):
        self._stop_event.set()