from typing import Union
import requests
import uvicorn
import os
from fastapi import Depends, FastAPI, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from uuid import UUID, uuid4
from fetcher import ImageFetcher, Stream
from session.camera import CameraSessionData, backend, cookie, verifier
from pydantic import BaseModel

load_dotenv()
CAM_URL = os.getenv("CAM_URL")
RECONG_URL = os.getenv("RECONG_URL")

app = FastAPI()

class TagDetail(BaseModel):
    tags: list[str]

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

imageFetchers: dict[str, ImageFetcher] = {}
streams: dict[str, Stream] = {}
@app.get("/ipcam", response_class=HTMLResponse)
async def tag_recogn(request: Request, tags: Union[str, str]):   
    session = uuid4()
    data = CameraSessionData(start=False)
    await backend.create(session, data)
    resp = templates.TemplateResponse("item.html", {"request": request, "img_url": f"/static/img-{session}.jpg", "tags": tags})
    cookie.attach_to_response(resp, session)
    return resp

@app.post("/stream/start", dependencies=[Depends(cookie)], status_code=200)
async def accessing_camera( tags: TagDetail, session_id: UUID = Depends(cookie)):
    session_id = str(session_id)
    fetcher = ImageFetcher(CAM_URL, session_id, 0.2)
    fetcher.start()
    stream = Stream(CAM_URL, tags.tags)
    stream.start()
    imageFetchers[session_id] = fetcher
    streams[session_id] = stream
    return session_id

@app.post("/stream/stop", dependencies=[Depends(cookie)], status_code=200)
async def accessing_camera(response: Response, session_id_uuid: UUID = Depends(cookie)):
    session_id = str(session_id_uuid)
    imageFetchers[session_id].stop()
    streams[session_id].stop()
    if os.path.exists(f"static/img-{session_id}.jpg"):
        os.remove(f"static/img-{session_id}.jpg") #img-448dbfd3-9923-4638-9d18-8b8e059fcbf2.jpg
    del imageFetchers[session_id]
    del streams[session_id]
    await backend.delete(session_id_uuid)
    cookie.delete_from_response(response)
    return "deleted session"

if __name__ == "__main__": 
    uvicorn.run(app, port=8080)