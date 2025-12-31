"""
Module: src.review.exceptions
Deskripsi:
Custom exception classes untuk review module.
"""

from fastapi import HTTPException, status
from src.review.constants import ErrorCode


class DuplicateReviewError(HTTPException):
    """Exception raised when user tries to review the same destination twice."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this destination",
            headers={"X-Error-Code": ErrorCode.DUPLICATE_REVIEW}
        )


class ReviewNotFoundError(HTTPException):
    """Exception raised when review is not found."""
    
    def __init__(self, review_id: int = None):
        detail = "Review not found"
        if review_id:
            detail = f"Review with id {review_id} not found"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers={"X-Error-Code": ErrorCode.REVIEW_NOT_FOUND}
        )


class DestinationNotFoundError(HTTPException):
    """Exception raised when destination is not found."""
    
    def __init__(self, destination_id: int = None):
        detail = "Destination not found"
        if destination_id:
            detail = f"Destination with id {destination_id} not found"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers={"X-Error-Code": ErrorCode.DESTINATION_NOT_FOUND}
        )


class InvalidRatingError(HTTPException):
    """Exception raised when rating is out of valid range."""
    
    def __init__(self, min_rating: int = 1, max_rating: int = 5):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rating must be between {min_rating} and {max_rating}",
            headers={"X-Error-Code": ErrorCode.INVALID_RATING}
        )


class NotReviewOwnerError(HTTPException):
    """Exception raised when user tries to modify a review they don't own."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to modify this review",
            headers={"X-Error-Code": ErrorCode.NOT_REVIEW_OWNER}
        )
