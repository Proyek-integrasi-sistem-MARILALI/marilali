"""
Utility functions for review service.
"""

def calculate_average_rating(reviews: list) -> float:
    """Calculate average rating from list of reviews."""
    if not reviews:
        return 0.0
    return sum(review.rating for review in reviews) / len(reviews)
