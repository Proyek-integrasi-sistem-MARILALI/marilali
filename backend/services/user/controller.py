"""
Module: services.user.controller
Deskripsi:
Logika bisnis untuk pengelolaan profil pengguna:
update data, ubah password, dan hapus akun.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.models import User
from core.security import verify_password, hash_password


# =====================================
#        GET USER PROFILE
# =====================================
def get_user_profile(current_user: User, db: Session):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")
    return user


# =====================================
#       UPDATE USER PROFILE
# =====================================
def update_user_profile(current_user: User, update_data, db: Session):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")

    # Update name
    if update_data.name:
        user.name = update_data.name

    # Update email (cek apakah email dipakai user lain)
    if update_data.email:
        existing = db.query(User).filter(User.email == update_data.email).first()
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email sudah digunakan.")
        user.email = update_data.email

    db.commit()
    db.refresh(user)
    return user


# =====================================
#          CHANGE PASSWORD
# =====================================
def change_password(current_user: User, password_data, db: Session):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")

    # VERIFY OLD PASSWORD
    if not verify_password(password_data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Password lama salah")

    # SET NEW PASSWORD
    user.hashed_password = hash_password(password_data.new_password)
    db.commit()

    return {"message": "Password berhasil diperbarui"}


# =====================================
#        DELETE USER ACCOUNT
# =====================================
def delete_user_account(current_user: User, db: Session):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")

    db.delete(user)
    db.commit()
    return {"message": "Akun berhasil dihapus"}
