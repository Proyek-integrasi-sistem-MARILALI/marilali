"""
Module: services.auth.controller
Deskripsi:
Logika bisnis untuk autentikasi, termasuk register, login, dan refresh token.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.models import User
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)
from jose import jwt, JWTError
from core.config import SECRET_KEY, ALGORITHM


# ====================================
#           REGISTER USER
# ====================================
def register_user(user_data, db: Session):
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
        hashed_password=hashed_pw   # FIXED
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ====================================
#              LOGIN USER
# ====================================
def login_user(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    
    # Mengecek apakah email terdaftar dan password valid
    if not user or not verify_password(password, user.hashed_password): 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah."
        )
    
    # Jika valid, sistem menghasilkan access token dan refresh token
    return {
        "access_token": create_access_token({"sub": user.email}),
        "refresh_token": create_refresh_token({"sub": user.email}),
        "token_type": "bearer"
    }


# ====================================
#         REFRESH ACCESS TOKEN
# ====================================
def refresh_user_token(refresh_token: str, db: Session):
    """
    Membuat access token baru berdasarkan refresh token valid.
    Mengecek apakah user masih ada di database.
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")

        if not user_email:
            raise HTTPException(status_code=401, detail="Token tidak valid")

        # Verifikasi apakah user masih eksis
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")

        # Generate access token baru
        new_access = create_access_token({"sub": user_email})

        return {
            "access_token": new_access,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token refresh tidak valid atau kadaluarsa"
        )
