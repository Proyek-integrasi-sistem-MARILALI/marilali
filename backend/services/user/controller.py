from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.models import User
from core.security import verify_password, hash_password

def get_user_profile(current_user: User, db: Session):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")
    return user


def update_user_profile(current_user: User, update_data, db: Session):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")

    if update_data.name:
        user.name = update_data.name
    if update_data.email:
        user.email = update_data.email

    db.commit()
    db.refresh(user)
    return user


def change_password(current_user: User, password_data, db: Session):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")

    if not verify_password(password_data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Password lama salah")

    user.hashed_password = hash_password(password_data.new_password)
    db.commit()
    db.refresh(user)
    return {"message": "Password berhasil diperbarui"}

def delete_user_account(current_user: User, db: Session):
    """
    Menghapus akun pengguna beserta datanya.
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")

    db.delete(user)
    db.commit()
    return {"message": "Akun berhasil dihapus"}
