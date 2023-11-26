from model.detect import Detect, Coords
from model.recogn import Recogn
from fastapi import FastAPI, UploadFile, HTTPException
app = FastAPI()

detect = Detect("best.pt")
recog = Recogn()

@app.post("/image/", status_code=200)
def recogn_tag(file: UploadFile):
    if file is None:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        bin = file.file.read()
        with open("img.jpg", "wb") as f:
            f.write(bin)
        coord: list[Coords] = detect.detect("img.jpg", saveImagePath="img.jpg")
        if len(coord) == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        else:
            image = coord[0].cropImage(imgPath="./img.jpg")
            recog.preprocess(image, saveImagePath="./img.jpg")
            results = recog.read("img.jpg").result
            print(results)
            if len(results) == 0:
                raise HTTPException(status_code=404, detail="Item not found")
            resp = []
            for result in results:
                resp.append({"text": result[1], "confidence": result[2]})
            return resp
