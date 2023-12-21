from model.cache_model import DetectionCache, CookiesCache, UserList
from sqlalchemy.orm import Session

def get_tags(db: Session):
    return db.query(DetectionCache).all()

def get_tag(db: Session, tag: str):
    return db.query(DetectionCache).filter(DetectionCache.tag == tag).first()

def add_tag(db: Session, tag: str):
    db_tag = DetectionCache(tag=tag, isDetected=False)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def remove_all_tags(db: Session):
    db.query(DetectionCache).delete()
    db.commit()
    return True

def change_tag(db: Session, tag: str, isDetected: bool):
    db_tag = db.query(DetectionCache).filter(DetectionCache.tag == tag).first()
    db_tag.isDetected = isDetected
    db.commit()
    db.refresh(db_tag)
    return db_tag

def remove_tags(db: Session, tags: list[str]):
    db.query(DetectionCache).filter(DetectionCache.tag.in_(tags)).delete(synchronize_session=False)
    db.commit()
    return True

def get_cookies(db: Session):
    return db.query(CookiesCache).all()

def get_cookie(db: Session, username: str):
    return db.query(CookiesCache).filter(CookiesCache.username == username).first()

def update_cookie(db: Session, username: str, cookie: str):
    db_cookie = db.query(CookiesCache).filter(CookiesCache.username == username).first()
    db_cookie.cookie = cookie
    db.commit()
    db.refresh(db_cookie)
    return db_cookie

def add_cookie(db: Session, username: str, cookie: str):
    db_cookie = CookiesCache(username=username, cookie=cookie)
    db.add(db_cookie)
    db.commit()
    db.refresh(db_cookie)
    return db_cookie

def remove_all_cookies(db: Session):
    db.query(CookiesCache).delete()
    db.commit()
    return True

def remove_cookie(db: Session, username: str):
    db.query(CookiesCache).filter(CookiesCache.username == username).delete()
    db.commit()
    return True

def get_all_users(db: Session):
    return db.query(UserList).all()

def add_user(db: Session, name: str, db_id: str, empl_id: str, department: str):
    db_user = UserList(name=name, db_id=db_id, empl_id=empl_id, department=department)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def remove_user(db: Session, name: str):
    db.query(UserList).filter(UserList.name == name).delete()
    db.commit()
    return True

def remove_all_users(db: Session):
    db.query(UserList).delete()
    db.commit()
    return True

def search_user(db: Session, name: str):
    return db.query(UserList).filter(UserList.name.like(f"%{name}%")).all()