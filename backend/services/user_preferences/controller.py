from sqlalchemy.orm import Session
from database.models import UserPreference
from fastapi import HTTPException

def get_preferences(user_id: int, db: Session):
    prefs = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferensi belum diatur.")
    return prefs

def update_preferences(user_id: int, data, db: Session):
    prefs = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    if not prefs:
        prefs = UserPreference(user_id=user_id)
        db.add(prefs)

    for key, value in data.dict(exclude_unset=True).items():
        setattr(prefs, key, value)

    db.commit()
    db.refresh(prefs)
    return prefs
