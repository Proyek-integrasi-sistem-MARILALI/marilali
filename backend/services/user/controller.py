"""
Module: services.user.controller
Deskripsi:
Berisi logika bisnis untuk pengelolaan profil pengguna,
termasuk update data, ubah password, dan hapus akun.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.models import User
from core.security import verify_password, hash_password


def get_user_profile(current_user: User, db: Session):
    """
    Mengambil profil pengguna saat ini.
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pengguna tidak ditemukan")
    return user


def update_user_profile(current_user: User, update_data, db: Session):
    """
    Memperbarui nama atau email pengguna.
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pengguna tidak ditemukan")

    if update_data.name:
        user.name = update_data.name
    if update_data.email:
        existing = db.query(User).filter(User.email == update_data.email).first()
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email sudah digunakan.")
        user.email = update_data.email

    db.commit()
    db.refresh(user)
    return user


def change_password(current_user: User, password_data, db: Session):
    """
    Mengubah password pengguna setelah memverifikasi password lama.
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pengguna tidak ditemukan")

    if not verify_password(password_data.old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password lama salah")

    user.hashed_password = hash_password(password_data.new_password)
    db.commit()
    return {"message": "Password berhasil diperbarui"}


def delete_user_account(current_user: User, db: Session):
    """
    Menghapus akun pengguna dari sistem.
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pengguna tidak ditemukan")

    db.delete(user)
    db.commit()
    return {"message": "Akun berhasil dihapus"}
