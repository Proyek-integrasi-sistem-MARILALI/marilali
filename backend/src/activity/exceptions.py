from fastapi import HTTPException, status


class ActivityNotFoundException(HTTPException):
    def __init__(self, activity_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with id {activity_id} not found"
        )


class NotActivityOwnerException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to modify this activity"
        )


class InvalidDateRangeException(HTTPException):
    def __init__(self, message: str = "Invalid date or time range"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


class ActivityDateOutOfRangeException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activity date must be within itinerary date range"
        )


class CannotModifyCompletedActivityException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify activities of a completed itinerary"
        )
