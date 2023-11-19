import math
import numpy as np
from ultralytics import YOLO
from PIL import Image
import cv2

Mat = np.ndarray


class Coords:
    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        self.x1 = float(x1)
        self.y1 = float(y1)
        self.x2 = float(x2)
        self.y2 = float(y2)
    
    def __str__(self):
        return f'({self.x1}, {self.y1}, {self.x2}, {self.y2})'

    def drawBoundingBox(self, imgPath: str, saveImagePath: str = None, openImg: bool = False) -> Mat:
        img = cv2.imread(imgPath)
        bounding_box_img = cv2.rectangle(img, (math.floor(self.x1), math.ceil(self.y1)), (math.ceil(self.x2), math.floor(self.y2)), (0, 255, 0), 2)
        if openImg:
            cv2.imshow('image', bounding_box_img)
            cv2.waitKey(0)
        if saveImagePath:
            cv2.imwrite(img=bounding_box_img, filename=saveImagePath)
        return bounding_box_img
    
    def cropImage(self, imgPath: str, saveImagePath: str = None, openImg: bool = False) -> Mat:
        img = cv2.imread(imgPath)
        cropped_img = img[math.floor(self.y1):math.floor(self.y2), math.floor(self.x1):math.floor(self.x2)]
        if openImg:
            cv2.imshow('image', cropped_img)
            cv2.waitKey(0)
        if saveImagePath:
            cv2.imwrite(img=cropped_img, filename=saveImagePath)
        return cropped_img

class TrainYOLO:
    def __init__(self, model_fn='yolov8n.pt'):
        self.model = YOLO(model_fn)  # load a .pt file

    def train(self, dataConf, epochs, resume=False):
        self.model.train(data=dataConf, epochs=epochs, resume=resume)
        return self
    
    def export(self):
        self.model.export()
        return self

    def detect(self, imgPath: str, saveImagePath: str = None) -> list[Coords]:
        results = self.model(imgPath)
        Coords = []
        for result in results:
            boxes = result.boxes.xyxy[0].tolist()
            im_array = result.plot()  # plot a BGR numpy array of predictions
            im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
            if saveImagePath:
                im.save(saveImagePath)
        return Coords

    def export(self):
        import logging
        path = self.model.export(format="onnx")
        logging.info(f"Exported model to {path}")
        return self

if __name__ == "__main__":
    dataConf = 'config.yml'
    model = TrainYOLO()
    model.train(dataConf, 50).detect('./data/test/images/00053.jpg')
    # TrainYOLO().export()