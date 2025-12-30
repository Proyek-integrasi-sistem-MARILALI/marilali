from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from fastapi import HTTPException

from src.notification.models import Notification


async def create_notification(
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
    db: AsyncSession
) -> Notification:
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        is_read=False
    )
    
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    
    return notification


async def get_user_notifications(
    user_id: int,
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False
) -> List[Notification]:
    query = select(Notification).where(Notification.user_id == user_id)
    
    if unread_only:
        query = query.where(Notification.is_read == False)
    
    query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def mark_notification_read(
    notification_id: int,
    user_id: int,
    db: AsyncSession
) -> Notification:
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if notification.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    
    return notification


async def mark_all_read(user_id: int, db: AsyncSession) -> dict:
    result = await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.commit()
    
    return {
        "message": "All notifications marked as read",
        "count": result.rowcount
    }


async def delete_notification(
    notification_id: int,
    user_id: int,
    db: AsyncSession
) -> dict:
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if notification.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.delete(notification)
    await db.commit()
    
    return {"message": "Notification deleted successfully"}


async def get_unread_count(user_id: int, db: AsyncSession) -> dict:
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)
    )
    unread_notifications = result.scalars().all()
    
    return {"unread_count": len(unread_notifications)}
