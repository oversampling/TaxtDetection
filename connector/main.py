from datetime import timedelta, datetime
from typing import Annotated, Union
from bs4 import BeautifulSoup
from fastapi.security import OAuth2PasswordBearer
import requests
import uvicorn
import os
from fastapi import Depends, FastAPI, Form, HTTPException, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from uuid import UUID, uuid4
# from model.SQLconnector import DetectionCache
from fetcher import ImageFetcher, Stream
from session.camera import CameraSessionData, backend, cookie, verifier
from pydantic import BaseModel
from model import cache_controller
from model.SQLconnector import Base, engine, SessionLocal
from sqlalchemy.orm import Session
import starlette.status as status
from controller.vis_connector import VIS
from jose import JWTError, jwt

Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

load_dotenv()
CAM_URL = os.getenv("CAM_URL")
RECONG_URL = os.getenv("RECONG_URL")
VIS_URL = os.getenv("VIS_URL")
VIS_USERLIST_URL = os.getenv("VIS_USERLIST_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 960

app = FastAPI()

class TagDetail(BaseModel):
    tags: list[str]

class TokenData(BaseModel):
    username: str
    name: str
    id: str

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

imageFetchers: dict[str, ImageFetcher] = {}
streams: dict[str, Stream] = {}

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def verify_token(request: Request) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = request.cookies.get("token")
    if token is None:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        name: str = payload.get("name")
        id: str = payload.get("id")
        if username is None or name is None or id is None:
            raise credentials_exception
        token_data = TokenData(username=username, name=name, id=id)
    except JWTError:
        # Delete session cookie 
        request.cookies.pop("token")
        raise credentials_exception
    except Exception as e:
        raise e
    return token_data

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

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    redirect_url = request.url_for("users_list")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post('/login', response_class=HTMLResponse)
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()], request: Request,  db: Session = Depends(get_db)):
    try:
        vis = VIS(VIS_URL, VIS_USERLIST_URL, username, password)
        print("VIS cookies")
        print(vis.cookies)
    except Exception as e:
        return templates.TemplateResponse("login.html", {"request": request, "msg": "Invalid username or password"}) 
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": vis.username, "name": vis.name, "id": str(uuid4())}, expires_delta=access_token_expires
    )
    # Turn vis.cookies dict into string
    cookies = ";".join([f"{key}={value}" for key, value in vis.cookies.items()])
    print(cookies)
    cookies_in_cache = cache_controller.get_cookie(db, username)
    print("Cookies in Cache")
    print(cookies_in_cache)
    if cookies_in_cache is None:
        print("Add cookies")
        cache_controller.add_cookie(db, username=username, cookie=cookies)
    else:
        print("Update cookies")
        cache_controller.update_cookie(db, username=username, cookie=cookies)
    print("Update cookies")
    redirect_url = request.url_for("users_list")
    redirect_response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    redirect_response.set_cookie("token", access_token)
    return redirect_response
    
@app.post('/logout', response_class=HTMLResponse)
async def logout(request: Request):
    # verifier.logout()
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/userslist", response_class=HTMLResponse)
async def users_list(request: Request, user: TokenData = Depends(verify_token), db: Session = Depends(get_db)):
    data = cache_controller.get_cookie(db, user.username)
    if data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if cache_controller.get_all_users(db) == []:
        content = VIS.getUserList(db, data.cookie, VIS_USERLIST_URL)
        employees = VIS.storeUserList(db, content)
    else:
        employees = cache_controller.get_all_users(db)
    # Get User list from cache, if don't have, get from vis
    return templates.TemplateResponse("userslist.html", {"request": request, "employees": employees})

@app.get("/userslist/{user_id}", response_class=HTMLResponse)
async def user_detail(request: Request, user_id: Union[str, str], user: TokenData = Depends(verify_token), db: Session = Depends(get_db)):
    data = cache_controller.get_cookie(db, user.username)
    user_infos = VIS.getUserDetails(user_id, data.cookie, VIS_USERLIST_URL)
    print(user_infos)
    return templates.TemplateResponse("user.html", {"request": request, "user_infos": user_infos, "tangible_assets_count": len(user_infos['assets'])})

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
async def accessing_camera( tags: TagDetail, session_id: UUID = Depends(cookie), db: Session = Depends(get_db)):
    session_id = str(session_id)
    cache_controller.remove_all_tags(db)
    fetcher = ImageFetcher(CAM_URL, session_id, 0.2)
    stream = Stream(CAM_URL, tags.tags, db)
    fetcher.start()
    stream.start()
    streams[session_id] = stream
    imageFetchers[session_id] = fetcher
    print(streams, imageFetchers)
    return session_id

@app.post("/stream/stop", dependencies=[Depends(cookie)], status_code=200)
async def accessing_camera(tags: TagDetail, response: Response, session_id_uuid: UUID = Depends(cookie)):
    session_id = str(session_id_uuid)
    imageFetchers[session_id].stop()
    streams[session_id].stop()
    cache_controller.remove_tags(streams[session_id].db, tags.tags)
    if os.path.exists(f"static/img-{session_id}.jpg"):
        os.remove(f"static/img-{session_id}.jpg") #img-448dbfd3-9923-4638-9d18-8b8e059fcbf2.jpg
    del imageFetchers[session_id]
    del streams[session_id]
    await backend.delete(session_id_uuid)
    cookie.delete_from_response(response)
    return "deleted session"

@app.post("/tag/detection/status", dependencies=[Depends(cookie)], status_code=200)
async def tag_detection_status(tags: TagDetail, db: Session = Depends(get_db)):
    response = []
    for tag in tags.tags:
        processedTag = ''.join([char for char in tag if char.isalpha() or char.isdigit()])
        processedTag = processedTag.lower()
        response.append(cache_controller.get_tag(db, processedTag))
        print("Processed Tag " + processedTag)
        print("All tags")
        print(cache_controller.get_tags(db))
        print("Response from db")
        print(cache_controller.get_tag(db, processedTag))
    return response

@app.get("/tag/detection")
def get_all_tags(db: Session = Depends(get_db)):
    response = cache_controller.get_tags(db)
    return response

@app.post("/cookie/add")
def add_cookie(username: str, cache: str, db: Session = Depends(get_db)):
    print(username, cache)
    cache_controller.add_cookie(db, username=username, cache=cache)
    result = cache_controller.get_cookies(db)
    print(result)
    return True

@app.post("/tag/add")
def add_tag(tag: str, db: Session = Depends(get_db)):
    print(tag)
    cache_controller.add_tag(db, tag=tag)
    result = cache_controller.get_tags(db)
    print(result)
    return True

@app.delete("/user/delete")
def delete_user(username: str, db: Session = Depends(get_db)):
    print(username)
    cache_controller.remove_user(db, username=username)
    result = cache_controller.get_all_users(db)
    print(result)
    return True

@app.delete("/user/delete/all")
def delete_all_users(db: Session = Depends(get_db)):
    cache_controller.remove_all_users(db)
    result = cache_controller.get_all_users(db)
    print(result)
    return True

if __name__ == "__main__": 
    uvicorn.run(app, port=8080)