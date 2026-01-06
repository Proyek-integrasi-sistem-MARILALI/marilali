from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from src.user.models import User
from src.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)


async def register_user(user_data, db: AsyncSession):
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


async def login_user(email_or_username: str, password: str, db: AsyncSession):
    # Try to find user by email first (email is unique)
    result = await db.execute(
        select(User).where(User.email == email_or_username)
    )
    user = result.scalar_one_or_none()
    
    # If not found by email, try by name (username)
    # Use .first() since names might not be unique
    if not user:
        result = await db.execute(
            select(User).where(User.name == email_or_username)
        )
        user = result.first()
        if user:
            user = user[0]  # Extract user from tuple
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password"
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
    # Verify and extract email from refresh token
    user_email = verify_refresh_token(refresh_token)
    
    # Generate new access token
    new_access_token = create_access_token({"sub": user_email})
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }
