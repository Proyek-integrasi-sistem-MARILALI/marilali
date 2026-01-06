
# Rating constraints
MIN_RATING = 1
MAX_RATING = 5

# Comment length
MAX_COMMENT_LENGTH = 1000


class ErrorCode:
    # Review errors
    DUPLICATE_REVIEW = "DUPLICATE_REVIEW"
    REVIEW_NOT_FOUND = "REVIEW_NOT_FOUND"
    DESTINATION_NOT_FOUND = "DESTINATION_NOT_FOUND"
    
    # Validation errors
    INVALID_RATING = "INVALID_RATING"
    COMMENT_TOO_LONG = "COMMENT_TOO_LONG"
    
    # Authorization errors
    NOT_REVIEW_OWNER = "NOT_REVIEW_OWNER"
