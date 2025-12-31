"""
Module: src.itinerary.exceptions
Deskripsi:
Custom exception classes untuk itinerary module.
"""

from fastapi import HTTPException, status
from src.itinerary.constants import ErrorCode


class ItineraryNotFoundError(HTTPException):
    """Exception raised when itinerary is not found."""
    
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
    """Exception raised when user tries to access/modify an itinerary they don't own."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this itinerary",
            headers={"X-Error-Code": ErrorCode.NOT_ITINERARY_OWNER}
        )


class PrivateItineraryError(HTTPException):
    """Exception raised when user tries to access a private itinerary."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This itinerary is private",
            headers={"X-Error-Code": ErrorCode.PRIVATE_ITINERARY}
        )


class InvalidDateRangeError(HTTPException):
    """Exception raised when date range is invalid."""
    
    def __init__(self, message: str = "End date must be after start date"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
            headers={"X-Error-Code": ErrorCode.INVALID_DATE_RANGE}
        )


class InvalidStatusError(HTTPException):
    """Exception raised when status is invalid."""
    
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
    """Exception raised when trying to modify a completed itinerary."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify a completed itinerary",
            headers={"X-Error-Code": ErrorCode.CANNOT_MODIFY_COMPLETED}
        )


class AlreadyCompletedError(HTTPException):
    """Exception raised when trying to mark an already completed itinerary as complete."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Itinerary is already marked as completed",
            headers={"X-Error-Code": ErrorCode.ALREADY_COMPLETED}
        )
