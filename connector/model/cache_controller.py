from . import cache_model
from sqlalchemy.orm import Session

def get_tags(db: Session):
    return db.query(cache_model.DetectionCache).all()

def get_tag(db: Session, tag: str):
    return db.query(cache_model.DetectionCache).filter(cache_model.DetectionCache.tag == tag).first()

def add_tag(db: Session, tag: str):
    db_tag = cache_model.DetectionCache(tag=tag, isDetected=False)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def remove_all_tags(db: Session):
    db.query(cache_model.DetectionCache).delete()
    db.commit()
    return True

def change_tag(db: Session, tag: str, isDetected: bool):
    db_tag = db.query(cache_model.DetectionCache).filter(cache_model.DetectionCache.tag == tag).first()
    db_tag.isDetected = isDetected
    db.commit()
    db.refresh(db_tag)
    return db_tag

def remove_tags(db: Session, tags: list[str]):
    db.query(cache_model.DetectionCache).filter(cache_model.DetectionCache.tag.in_(tags)).delete(synchronize_session=False)
    db.commit()
    return True