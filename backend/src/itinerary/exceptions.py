from fastapi import HTTPException, status
from src.itinerary.constants import ErrorCode


class ItineraryNotFoundError(HTTPException):
    def __init__(self, itinerary_id: int = None):
        detail = "Itinerary not found"
        if itinerary_id:
            detail = f"Itinerary with id {itinerary_id} not found"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers={"X-Error-Code": ErrorCode.ITINERARY_NOT_FOUND}
        )


class NotItineraryOwnerError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this itinerary",
            headers={"X-Error-Code": ErrorCode.NOT_ITINERARY_OWNER}
        )


class PrivateItineraryError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This itinerary is private",
            headers={"X-Error-Code": ErrorCode.PRIVATE_ITINERARY}
        )


class InvalidDateRangeError(HTTPException):
    def __init__(self, message: str = "End date must be after start date"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
            headers={"X-Error-Code": ErrorCode.INVALID_DATE_RANGE}
        )


class InvalidStatusError(HTTPException):
    def __init__(self, valid_statuses: list = None):
        detail = "Invalid itinerary status"
        if valid_statuses:
            detail += f". Valid statuses: {', '.join(valid_statuses)}"
        
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers={"X-Error-Code": ErrorCode.INVALID_STATUS}
        )


class CannotModifyCompletedError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify a completed itinerary",
            headers={"X-Error-Code": ErrorCode.CANNOT_MODIFY_COMPLETED}
        )


class AlreadyCompletedError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Itinerary is already marked as completed",
            headers={"X-Error-Code": ErrorCode.ALREADY_COMPLETED}
        )
