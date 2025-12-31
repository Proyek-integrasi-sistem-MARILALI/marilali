"""
Module: services.auth.controller
Deskripsi:
Async business logic untuk autentikasi - registrasi, login, dan refresh token.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.user.models import User
from src.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)


async def register_user(user_data, db: AsyncSession):
    """
    Mendaftarkan pengguna baru dengan validasi email unik.
    
    Args:
        user_data: UserCreate schema dengan name, email, password
        db: Async database session
        
    Returns:
        User object yang baru dibuat
        
    Raises:
        HTTPException: Jika email sudah terdaftar
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_pw = hash_password(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_pw
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


async def login_user(email: str, password: str, db: AsyncSession):
    """
    Verify credentials dan generate JWT tokens.
    
    Args:
        email: User email
        password: Plain text password
        db: Async database session
        
    Returns:
        Dict dengan access_token, refresh_token, dan token_type
        
    Raises:
        HTTPException: Jika credentials invalid
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Generate tokens
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


async def refresh_access_token(refresh_token: str):
    """
    Generate access token baru dari refresh token yang valid.
    
    Args:
        refresh_token: JWT refresh token
        
    Returns:
        Dict dengan access_token baru dan token_type
        
    Raises:
        HTTPException: Jika refresh token invalid
    """
    # Verify and extract email from refresh token
    user_email = verify_refresh_token(refresh_token)
    
    # Generate new access token
    new_access_token = create_access_token({"sub": user_email})
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }
