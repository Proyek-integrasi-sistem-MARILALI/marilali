from fastapi import HTTPException, status

class NotificationNotFoundError(HTTPException):
    def __init__(self, notification_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with id {notification_id} not found"
        )
