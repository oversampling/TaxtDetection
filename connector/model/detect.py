import logging
import math
import numpy as np
from ultralytics import YOLO
from PIL import Image
import cv2
from cv2.typing import MatLike

class Coords:
    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        self.x1 = float(x1)
        self.y1 = float(y1)
        self.x2 = float(x2)
        self.y2 = float(y2)
    
    def __str__(self):
        return f'({self.x1}, {self.y1}, {self.x2}, {self.y2})'

    def drawBoundingBox(self, imgPath: str, saveImagePath: str = None, openImg: bool = False) -> MatLike:
        img = cv2.imread(imgPath)
        bounding_box_img = cv2.rectangle(img, (math.floor(self.x1), math.ceil(self.y1)), (math.ceil(self.x2), math.floor(self.y2)), (0, 255, 0), 2)
        if openImg:
            cv2.imshow('image', bounding_box_img)
            cv2.waitKey(0)
        if saveImagePath:
            logging.log(1, "Saving image to {saveImagePath}")
            cv2.imwrite(img=bounding_box_img, filename=saveImagePath)
        return bounding_box_img
    
    def cropImage(self, imgPath: str, saveImagePath: str = None, openImg: bool = False) -> MatLike:
        img = cv2.imread(imgPath)
        cropped_img = img[math.floor(self.y1):math.floor(self.y2), math.floor(self.x1):math.floor(self.x2)]
        if openImg:
            cv2.imshow('image', cropped_img)
            cv2.waitKey(0)
        if saveImagePath:
            cv2.imwrite(img=cropped_img, filename=saveImagePath)
        return cropped_img

class Detect:
    def __init__(self, model_fn='yolov8n.pt'):
        self.load(model_fn)

    def train(self, dataConf, epochs, amp, resume=False):
        self.model.train(data=dataConf, epochs=epochs, resume=resume, amp=amp)
        return self

    def detect(self, imgPath: str, saveImagePath: str = None) -> list[Coords]:
        results = self.model(imgPath)
        bounding_box: list[Coords] = []
        for result in results:
            for box in result.boxes:
                for xyxy in box.xyxy:
                    coord = Coords(xyxy[0], xyxy[1], xyxy[2], xyxy[3])
                    bounding_box.append(coord)
            im_array = result.plot()  # plot a BGR numpy array of predictions
            im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
            if saveImagePath:
                logging.info(f"Saving image to {saveImagePath}")
                im.save(saveImagePath)
        return bounding_box

    def export(self):
        path = self.model.export(format="onnx")
        logging.info(1, f"Exported model to {path}")
        return self

    def load(self, model_fn='yolov8n.pt'):
        self.model = YOLO(model_fn)
        return self
    
    def validate(self):
        metrics = self.model.val()
        print(metrics)
        return self