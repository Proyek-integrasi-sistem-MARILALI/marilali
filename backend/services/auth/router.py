"""
Module: services.auth.router
Deskripsi:
Endpoint autentikasi (register, login, logout, refresh token, profile).
"""

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from services.auth import controller
from services.auth.schemas import UserCreate, UserLogin, UserResponse
from database.connection import get_db
from core.security import create_access_token, get_current_user
from core.config import SECRET_KEY, ALGORITHM
from database.models import User

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# -------------------------------
# Optional: Token blacklist
# -------------------------------
TOKEN_BLACKLIST = set()


# ================================
#            REGISTER
# ================================
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrasi pengguna baru"
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return controller.register_user(user, db)


# ================================
#              LOGIN
# ================================
@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Login pengguna"
)
def login(user: UserLogin, db: Session = Depends(get_db)):
    return controller.login_user(user.email, user.password, db)


# ================================
#              LOGOUT
# ================================
@router.post(
    "/logout",
    summary="Logout pengguna"
)
def logout(token: str = Depends(oauth2_scheme)):
    """
    Logout versi server: token dimasukkan blacklist.
    Client tetap harus menghapus token di local storage.
    """
    TOKEN_BLACKLIST.add(token)
    return {"message": "Logout berhasil. Token diblokir."}


# ================================
#         REFRESH TOKEN
# ================================
@router.post(
    "/refresh",
    summary="Perbarui Access Token"
)
def refresh_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Membuat access token baru dari refresh token yang valid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")

        if not user_email:
            raise HTTPException(status_code=401, detail="Token tidak valid")

        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")

        new_access = create_access_token({"sub": user_email})

        return {
            "access_token": new_access,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Token refresh tidak valid atau kadaluarsa")


# ================================
#          CURRENT USER
# ================================
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Mendapatkan profil user"
)
def get_me(
    current_user: UserResponse = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    # Cek apakah token sudah logout
    if token in TOKEN_BLACKLIST:
        raise HTTPException(status_code=401, detail="Token sudah logout")

    return current_user
