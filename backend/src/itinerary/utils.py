"""
Utility functions for itinerary service.
"""
from datetime import date

def calculate_trip_duration(start_date: date, end_date: date) -> int:
    """Calculate number of days in a trip."""
    return (end_date - start_date).days + 1

def validate_date_range(start_date: date, end_date: date) -> bool:
    """Validate that start date is before or equal to end date."""
    return start_date <= end_date
