def calculate_average_rating(reviews: list) -> float:
    if not reviews:
        return 0.0
    return sum(review.rating for review in reviews) / len(reviews)
