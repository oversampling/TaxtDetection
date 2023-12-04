from typing import Union
from bs4 import BeautifulSoup
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

def user_table_to_dict(table_index, soup):
    user_table = soup.find_all('table')[table_index] 
    user_detail = {}
    for row in user_table.find_all('tr'):
        columns = row.find_all('td')
        if len(columns) == 3:
            user_detail[columns[1].text.strip().replace(":", "")] = columns[2].text.strip()
        elif len(columns) == 2:
            user_detail[columns[0].text.strip().replace(":", "")] = columns[1].text.strip()
    return user_detail

def table_to_dict(table_index, soup):
    table = soup.find_all('table')[table_index]
    table_keys = []
    for row in table.find_all('tr'):
        columns = row.find_all("th")
        for column in columns:
            if column.text != "Acknowledge":
                table_keys.append(column.text)
    table_details = []
    for row in (table.find_all('tr')):
        columns = row.find_all('td')
        if len(columns) > 1:
            table_detail = {
                table_keys[0]: columns[0].text.strip(),
                table_keys[1]: columns[1].text,
                table_keys[2]: columns[2].text,
                table_keys[3]: columns[3].text,
                table_keys[4]: columns[4].find('input').get("value"),
                table_keys[5]: columns[5].find('input').get("value") if len(columns) > 5 else "",
                table_keys[6]: columns[6].find('input').get("value") if len(columns) > 6 else "",
                table_keys[7]: columns[7].find('input').get("value") if len(columns) > 7 else "",
                table_keys[8]: columns[8].find('input').get("value") if len(columns) > 8 else "",
            }
            table_details.append(table_detail)
    
    return table_details

def get_user_detail(username: str):
    file_path = "./static/user_list/" + username + ".htm"
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    return user_table_to_dict(0, soup)

def get_user_info(username: str, table_index: int):
    file_path = "./static/user_list/" + username + ".htm"
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    return table_to_dict(table_index, soup)


@app.get("/ipcam", response_class=HTMLResponse)
async def tag_recogn(request: Request, user: Union[str, str]):   
    session = uuid4()
    data = CameraSessionData(start=False)
    await backend.create(session, data)
    tags: list[str] = []
    user_details = get_user_detail(user)
    user_infos = get_user_info(user, 1)
    for info in user_infos:
        if info["Asset Tag"] != "":
            tags.append(info["Asset Tag"])
    tags = ",".join(tags)
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