import os
import cv2
from doctr.models import detection_predictor
from PIL import Image, ExifTags
from matplotlib import patches
# Let's pick the desired backend
# os.environ['USE_TF'] = '1'
os.environ['USE_TORCH'] = '1'

import matplotlib.pyplot as plt

from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from doctr.models import recognition_predictor
import numpy as np


data_path = "./data/train/"
image_fns = os.listdir(data_path)
image_path = data_path + "VT-OE-201901902(Scaled).jpg"
doc = DocumentFile.from_images([image_path])
# predictor = detection_predictor('db_resnet50', pretrained=True, assume_straight_pages=False)
predictor = detection_predictor('db_resnet50_rotation', pretrained=True, assume_straight_pages=False)
img = cv2.imread(image_path)
rectangles = predictor([img])
height, width = img.shape[:2]
print(height, width)
normalized_coordinates = (rectangles[0]["words"])
pixel_coordinates = (normalized_coordinates * np.array([width, height])).astype(int)
print(pixel_coordinates)
isClosed = True
color = (0, 255, 0)
thickness = 2
img = cv2.polylines(img, [pixel_coordinates], isClosed, color, thickness)
cv2.imwrite(os.path.join(data_path , 'waka.jpg'), img)
cv2.waitKey(0)

# Crop image to bounding box
mask = np.zeros_like(img)
cv2.fillPoly(mask, pixel_coordinates, (255,255,255))
img = cv2.bitwise_and(img, mask)
x, y, w, h = cv2.boundingRect(pixel_coordinates)
cropped_img = img[y:y+h, x:x+w]
cv2.imwrite(os.path.join(data_path , 'waka2.jpg'), cropped_img)
cropped_img = cv2.imread(os.path.join(data_path , 'waka2.jpg'))
model = ocr_predictor(
    det_arch="db_resnet50_rotation",
    reco_arch="parseq",
    pretrained=True,
    det_bs=8,
    reco_bs=1024,
    assume_straight_pages=False,
    straighten_pages=True,
    detect_orientation=True,
)
result = model([cropped_img])
print(result)

# predictor = recognition_predictor('crnn_vgg16_bn')
# img2 = cv2.imread(os.path.join(data_path , 'waka2.jpg'))
# out = predictor ([img2])
# print(out)

# Get Image Info
# image = Image.open(image_path)
# exif = { ExifTags.TAGS[k]: v for k, v in image._getexif().items() if k in ExifTags.TAGS }
# print(exif)