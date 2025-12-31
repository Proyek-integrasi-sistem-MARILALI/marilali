"""
Module: services.auth.dependencies
Deskripsi:
Reusable dependencies untuk authentication dan validation.
Implements dependency chaining pattern untuk code reuse.
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.config import settings
from src.database import get_db
from src.user.models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def parse_jwt_data(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> dict:
    """
    Parse and validate JWT token.
    
    Dependency yang extract user_id dari JWT token.
    Dapat di-reuse oleh dependencies lain untuk validation lebih lanjut.
    
    Args:
        token: JWT token dari OAuth2PasswordBearer
        
    Returns:
        Dict berisi user_id dan data lain dari token
        
    Raises:
        HTTPException: Jika token invalid atau expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
            
        return {"user_id": int(user_id), "email": payload.get("email")}
        
    except JWTError:
        raise credentials_exception


async def get_current_user(
    token_data: Annotated[dict, Depends(parse_jwt_data)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    Get current authenticated user from database.
    
    Dependency yang menggunakan parse_jwt_data untuk mendapatkan user dari DB.
    Dependency chaining: parse_jwt_data -> get_current_user
    
    Args:
        token_data: Dict dari parse_jwt_data dependency
        db: Database session
        
    Returns:
        User object dari database
        
    Raises:
        HTTPException: Jika user tidak ditemukan
    """
    result = await db.execute(
        select(User).where(User.id == token_data["user_id"])
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Validate that user is active.
    
    Dependency chaining example: parse_jwt_data -> get_current_user -> get_active_user
    
    Args:
        current_user: User object dari get_current_user dependency
        
    Returns:
        Active user object
        
    Raises:
        HTTPException: Jika user tidak aktif (bisa di-extend dengan field is_active)
    """
    # Example validation - extend User model dengan is_active field jika diperlukan
    # if not current_user.is_active:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Inactive user"
    #     )
    
    return current_user


# Type aliases untuk cleaner route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
ActiveUser = Annotated[User, Depends(get_active_user)]
