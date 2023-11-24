import logging
import cv2
from typing import Annotated, Union
from model.detect import TrainYOLO, Coords
from model.recogn import Recogn
from fastapi import FastAPI, File, Response, UploadFile
app = FastAPI()


@app.post("/image/", status_code=200)
def recogn_tag(file: UploadFile | None, response: Response):
    if not file:
        response.status_code = 404
        return 404
    else:
        bin = file.file.read()
        with open("img.jpg", "wb") as f:
            f.write(bin)
        return {"filename": file.filename}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}