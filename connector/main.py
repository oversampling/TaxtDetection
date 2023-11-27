from typing import Union
import uvicorn
import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
load_dotenv()
CAM_URL = os.getenv("CAM_URL")
print(CAM_URL)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/ipcam", response_class=HTMLResponse)
def read_root(request: Request):    
    return templates.TemplateResponse("item.html", {"request": request, "cam_url": CAM_URL})

if __name__ == "__main__":
    uvicorn.run(app, port=8080)