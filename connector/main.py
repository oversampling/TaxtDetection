from typing import Union
import requests
import uvicorn
import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()
CAM_URL = os.getenv("CAM_URL")
RECONG_URL = os.getenv("RECONG_URL")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/ipcam", response_class=HTMLResponse)
def tag_recong(request: Request, tag: Union[str, str]):   
    return templates.TemplateResponse("item.html", {"request": request, "img_url": "/static/img.jpg", "tag": tag})

@app.post("/stream", status_code=200)
def accessing_camera():
    photo = requests.get(CAM_URL)
    with open("static/img.jpg", "wb") as f:
        f.write(photo)
    files = {'file': open('img.jpg', 'rb')}
    response = requests.post(RECONG_URL, files=files)
    return "OK"

if __name__ == "__main__": 
    uvicorn.run(app, port=8080)