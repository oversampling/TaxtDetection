import cv2
import easyocr
import numpy as np

Mat = np.ndarray

class Recogn:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])
        self.result = None

    def read(self, imgPath: str) -> str:
        self.result = self.reader.readtext(imgPath)
        return self

    def preprocess(self, imgPath: str, saveImagePath = None) -> Mat:
        image = cv2.imread(imgPath)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        binary = cv2.medianBlur(binary, 5)
        if saveImagePath:
            cv2.imwrite(saveImagePath, binary)
        return self
    