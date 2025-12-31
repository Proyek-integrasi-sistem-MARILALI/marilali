"""
Module: core.security
Deskripsi:
Fungsi-fungsi keamanan untuk autentikasi dengan JWT dan password hashing.
Menggunakan async pattern untuk kompatibilitas dengan FastAPI async endpoints.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.user.models import User
from passlib.context import CryptContext
from src.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
# tokenUrl must match the mounted router prefix + endpoint path
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """
    Hash password menggunakan bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    password = password[:72]
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password terhadap hash.
    
    Args:
        plain_password: Plain text password dari user
        hashed_password: Hashed password dari database
        
    Returns:
        True jika password cocok, False jika tidak
    """
    plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Membuat JWT access token dengan expiration time.
    
    Args:
        data: Payload data untuk disimpan dalam token (biasanya {"sub": email})
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Membuat JWT refresh token dengan expiration time lebih panjang.
    
    Args:
        data: Payload data untuk disimpan dalam token (biasanya {"sub": email})
        
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency untuk mendapatkan user yang sedang login dari JWT token.
    
    Args:
        token: JWT token dari Authorization header
        db: Async database session
        
    Returns:
        User object dari database
        
    Raises:
        HTTPException: Jika token invalid atau user tidak ditemukan
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if email is None or token_type != "access":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception

    # Query user from database using async session
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    return user


def verify_refresh_token(token: str) -> str:
    """
    Verify refresh token dan extract email.
    
    Args:
        token: JWT refresh token
        
    Returns:
        Email dari token payload
        
    Raises:
        HTTPException: Jika token invalid atau bukan refresh token
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if email is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
            
        return email
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )