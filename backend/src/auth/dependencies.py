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
    return current_user


# Type aliases untuk cleaner route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
ActiveUser = Annotated[User, Depends(get_active_user)]
