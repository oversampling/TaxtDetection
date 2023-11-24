import os
from detect import TrainYOLO, Coords
from pathlib import Path

def create_dataset():
    images = os.listdir("./data/detect/train/images")
    images = [os.path.join("./data/detect/train/images", image) for image in images]
    recog_dp = "./data/recog/train/images"
    model = TrainYOLO("best.pt")
    # remove all file in recog_dp
    for f in os.listdir(recog_dp):
        os.remove(os.path.join(recog_dp, f))
    Path(recog_dp).mkdir(parents=True, exist_ok=True)
    for image in images:
        bbs: list[Coords] = model.detect(image)
        for bb in bbs:
            bb.cropImage(image, saveImagePath=os.path.join(recog_dp, os.path.basename(image)))

if __name__ == "__main__":
    create_dataset()
