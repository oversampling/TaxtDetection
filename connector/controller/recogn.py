import cv2
from cv2.typing import MatLike
import easyocr
import numpy as np

class Recogn:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])
        self.result = None

    def read(self, imgPath: str) -> str:
        self.result = self.reader.readtext(imgPath)
        return self

    def preprocess(self, image: MatLike, imgPath: str = None, saveImagePath = None) -> MatLike:
        if imgPath:
            image = cv2.imread(imgPath)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        image = self.remove_shadow(image)
        mean = image.mean()
        if mean < 100:
            image = 255-image
        image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 101, 21)
        if saveImagePath:
            cv2.imwrite(saveImagePath, image)
        return self
    
    def remove_shadow(self, img: MatLike) -> MatLike:

        rgb_planes = cv2.split(img)

        result_planes = []
        result_norm_planes = []
        for plane in rgb_planes:
            dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
            bg_img = cv2.medianBlur(dilated_img, 21)
            diff_img = 255 - cv2.absdiff(plane, bg_img)
            norm_img = cv2.normalize(diff_img,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
            result_planes.append(diff_img)
            result_norm_planes.append(norm_img)
            
        # result = cv2.merge(result_planes)
        result_norm = cv2.merge(result_norm_planes)
        return result_norm