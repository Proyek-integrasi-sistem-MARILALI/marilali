"""
Module: src.itinerary.constants
Deskripsi:
Constants untuk itinerary module.
"""

# Itinerary status options
STATUS_PLANNED = "planned"
STATUS_ONGOING = "ongoing"
STATUS_COMPLETED = "completed"
STATUS_CANCELLED = "cancelled"

VALID_STATUSES = [STATUS_PLANNED, STATUS_ONGOING, STATUS_COMPLETED, STATUS_CANCELLED]


class ErrorCode:
    """Error codes untuk itinerary module."""
    
    # Itinerary errors
    ITINERARY_NOT_FOUND = "ITINERARY_NOT_FOUND"
    NOT_ITINERARY_OWNER = "NOT_ITINERARY_OWNER"
    PRIVATE_ITINERARY = "PRIVATE_ITINERARY"
    
    # Validation errors
    INVALID_DATE_RANGE = "INVALID_DATE_RANGE"
    INVALID_STATUS = "INVALID_STATUS"
    INVALID_BUDGET = "INVALID_BUDGET"
    
    # Operation errors
    CANNOT_MODIFY_COMPLETED = "CANNOT_MODIFY_COMPLETED"
    ALREADY_COMPLETED = "ALREADY_COMPLETED"
