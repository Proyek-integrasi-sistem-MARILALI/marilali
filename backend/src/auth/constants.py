"""
Module: src.auth.constants
Deskripsi:
Constants untuk authentication module - token types dan error codes.
"""

# Token Types
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


class ErrorCode:
    """Error codes untuk authentication module."""
    
    # Registration errors
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    INVALID_EMAIL_FORMAT = "INVALID_EMAIL_FORMAT"
    WEAK_PASSWORD = "WEAK_PASSWORD"
    
    # Login errors
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    INCORRECT_PASSWORD = "INCORRECT_PASSWORD"
    
    # Token errors
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    INVALID_TOKEN_TYPE = "INVALID_TOKEN_TYPE"
    TOKEN_REQUIRED = "TOKEN_REQUIRED"
    
    # Authorization errors
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"


# Password validation
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 100

# Strong password pattern (optional, can be used for validation)
STRONG_PASSWORD_PATTERN = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
STRONG_PASSWORD_MESSAGE = (
    "Password must contain at least 8 characters, "
    "one uppercase letter, one lowercase letter, "
    "one digit, and one special character"
)
