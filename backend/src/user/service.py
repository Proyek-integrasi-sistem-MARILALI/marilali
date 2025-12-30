from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.user.models import User
from src.auth.security import verify_password, hash_password


async def get_user_profile(current_user: User, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def update_user_profile(current_user: User, update_data, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update fields if provided
    if update_data.name is not None:
        user.name = update_data.name
    if update_data.phone is not None:
        user.phone = update_data.phone
    if update_data.date_of_birth is not None:
        user.date_of_birth = update_data.date_of_birth
    if update_data.gender is not None:
        user.gender = update_data.gender
    if update_data.country is not None:
        user.country = update_data.country
    if update_data.city is not None:
        user.city = update_data.city
    if update_data.bio is not None:
        user.bio = update_data.bio

    await db.commit()
    await db.refresh(user)
    return user


async def change_password(current_user: User, password_data, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(password_data.old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password")

    user.hashed_password = hash_password(password_data.new_password)
    await db.commit()
    return {"message": "Password updated successfully"}


async def delete_user_account(current_user: User, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await db.delete(user)
    await db.commit()
    return {"message": "Account deleted successfully"}


async def update_profile_picture(current_user: User, profile_picture: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.profile_picture = profile_picture
    await db.commit()
    await db.refresh(user)
    return user


async def change_email(current_user: User, new_email: str, password: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Verify password
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")

    # Check if email already exists
    existing_result = await db.execute(select(User).where(User.email == new_email))
    existing = existing_result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")

    user.email = new_email
    user.is_verified = 0  # Require re-verification
    await db.commit()
    
    # MVP: Auto-verify for testing, Production: send verification email
    
    return {"message": "Email updated successfully. Please verify your new email."}


async def verify_email(user_id: int, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user.is_verified == 1:
        return {"message": "Email already verified"}
    
    user.is_verified = 1
    await db.commit()
    
    return {"message": "Email verified successfully"}


async def request_password_reset(email: str, db: AsyncSession):
    from datetime import datetime, timedelta
    import secrets
    from src.auth.models import PasswordResetToken
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    # Always return success to prevent email enumeration attacks
    if not user:
        return {"message": "If that email exists, a password reset link has been sent."}
    
    # Generate secure reset token
    reset_token = secrets.token_urlsafe(32)
    
    # Token expires in 1 hour
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    # Store token in database
    token_record = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at,
        used=0
    )
    db.add(token_record)
    await db.commit()
    
    # MVP: Return token for testing
    # Production: Send email with link: https://yourapp.com/reset-password?token={reset_token}
    return {
        "message": "Password reset link sent to your email.",
        "reset_token": reset_token,  # For MVP testing only!
        "expires_in": "1 hour"
    }


async def reset_password_with_token(token: str, new_password: str, db: AsyncSession):
    from datetime import datetime
    from src.auth.models import PasswordResetToken
    
    # Find token in database
    result = await db.execute(
        select(PasswordResetToken)
        .where(PasswordResetToken.token == token)
        .where(PasswordResetToken.used == 0)
    )
    token_record = result.scalar_one_or_none()
    
    # Validate token exists
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token expired
    if datetime.utcnow() > token_record.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired. Please request a new one."
        )
    
    # Get user
    user_result = await db.execute(select(User).where(User.id == token_record.user_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Update password
    user.hashed_password = hash_password(new_password)
    
    # Mark token as used
    token_record.used = 1
    
    await db.commit()
    
    return {"message": "Password reset successfully. You can now login with your new password."}
