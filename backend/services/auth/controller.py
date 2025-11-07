"""
Module: services.auth.controller
Deskripsi:
Berisi logika bisnis untuk fitur autentikasi, termasuk proses registrasi, login pengguna,
serta pembuatan access token dan refresh token menggunakan JWT.
"""

from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from database.models import User
from database.connection import get_db
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)


def register_user(user_data, db: Session):
    """
    Mendaftarkan pengguna baru dengan validasi email unik dan hashing password.
    """
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sudah terdaftar."
        )

    hashed_pw = hash_password(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(email: str, password: str, db: Session):
    """
    Verifikasi kredensial pengguna dan hasilkan access token serta refresh token.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah."
        )

    # Buat token JWT
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def refresh_user_token(refresh_token: str):
    """
    Generate access token baru berdasarkan refresh token yang valid.
    """
    from jose import jwt, JWTError
    from core.config import SECRET_KEY, ALGORITHM

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")

        if user_email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak valid")

        # Buat access token baru
        new_access_token = create_access_token({"sub": user_email})
        return {"access_token": new_access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token refresh tidak valid atau kadaluarsa")
