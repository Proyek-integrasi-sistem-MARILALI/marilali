"""
Module: services.auth.router
Deskripsi:
Mendefinisikan endpoint untuk fitur autentikasi pengguna,
termasuk registrasi, login, logout, dan refresh token.
Endpoint ini memanggil logika dari controller.
"""

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from services.auth import controller
from services.auth.schemas import UserCreate, UserLogin, UserResponse
from database.connection import get_db
from core.security import create_access_token
from core.config import SECRET_KEY, ALGORITHM
from core.security import get_current_user

# Router khusus untuk autentikasi
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrasi pengguna baru",
    description="Mendaftarkan akun baru dengan nama, email, dan password."
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint untuk registrasi pengguna baru.
    """
    return controller.register_user(user, db)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Login pengguna",
    description="Melakukan login dan menghasilkan JWT access serta refresh token."
)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Endpoint untuk login pengguna yang sudah terdaftar.
    """
    return controller.login_user(user.email, user.password, db)


@router.post(
    "/logout",
    summary="Logout pengguna",
    description="Logout dilakukan di sisi client dengan menghapus token dari penyimpanan."
)
def logout(token: str = Depends(oauth2_scheme)):
    """
    Logout simbolik: token tidak disimpan di server, cukup dihapus di sisi client.
    """
    return {"message": "Logout berhasil, silakan hapus token di sisi client."}


@router.post(
    "/refresh",
    summary="Perbarui Access Token",
    description="Menghasilkan access token baru berdasarkan refresh token yang valid."
)
def refresh_token(token: str):
    """
    Endpoint untuk memperbarui access token menggunakan refresh token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=401, detail="Token tidak valid")

        new_access = create_access_token({"sub": user_email})
        return {"access_token": new_access, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Token tidak valid atau kadaluarsa")

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Cek profil pengguna",
    description="Mengembalikan data user yang sedang login berdasarkan token JWT."
)
def get_me(current_user: UserResponse = Depends(get_current_user)):
    """
    Endpoint untuk mendapatkan data pengguna yang sedang login.
    """
    return current_user