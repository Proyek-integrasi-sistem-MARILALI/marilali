"""
Module: services.user_preferences.controller
Deskripsi:
Berisi logika bisnis untuk mengelola preferensi pengguna,
mencakup pengambilan dan pembaruan preferensi perjalanan.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.models import UserPreference


# ================================
#        GET USER PREFERENCES
# ================================
def get_preferences(user_id: int, db: Session):
    """
    Mengambil preferensi user.
    Jika user belum punya preferensi, akan membuat default baru.
    """
    prefs = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user_id)
        .first()
    )

    # Optional behavior:
    # daripada error 404, kita auto create default agar UX lebih enak
    if not prefs:
        prefs = UserPreference(user_id=user_id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)

    return prefs


# ================================
#        UPDATE PREFERENCES
# ================================
def update_preferences(user_id: int, data, db: Session):
    """
    Update preferensi user.
    Jika belum ada preferensi → otomatis dibuat.
    """
    prefs = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user_id)
        .first()
    )

    if not prefs:
        prefs = UserPreference(user_id=user_id)
        db.add(prefs)

    # update hanya field yang dikirim client
    for key, value in data.dict(exclude_unset=True).items():
        setattr(prefs, key, value)

    db.commit()
    db.refresh(prefs)
    return prefs
