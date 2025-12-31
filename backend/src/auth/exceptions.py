"""
Module: src.auth.exceptions
Deskripsi:
Custom exception classes untuk authentication module.
"""

from fastapi import HTTPException, status
from src.auth.constants import ErrorCode


class EmailAlreadyExistsError(HTTPException):
    """Exception raised when email already exists in database."""
    
    def __init__(self, email: str = None):
        detail = "Email already registered"
        if email:
            detail = f"Email '{email}' is already registered"
        
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers={"X-Error-Code": ErrorCode.EMAIL_ALREADY_EXISTS}
        )


class InvalidCredentialsError(HTTPException):
    """Exception raised when login credentials are invalid."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer",
                "X-Error-Code": ErrorCode.INVALID_CREDENTIALS
            }
        )


class UserNotFoundError(HTTPException):
    """Exception raised when user is not found."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"X-Error-Code": ErrorCode.USER_NOT_FOUND}
        )


class InvalidTokenError(HTTPException):
    """Exception raised when token is invalid."""
    
    def __init__(self, message: str = "Invalid token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={
                "WWW-Authenticate": "Bearer",
                "X-Error-Code": ErrorCode.INVALID_TOKEN
            }
        )


class TokenExpiredError(HTTPException):
    """Exception raised when token has expired."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={
                "WWW-Authenticate": "Bearer",
                "X-Error-Code": ErrorCode.TOKEN_EXPIRED
            }
        )


class InvalidTokenTypeError(HTTPException):
    """Exception raised when token type is invalid (e.g., using refresh token as access token)."""
    
    def __init__(self, expected: str, got: str = None):
        detail = f"Invalid token type. Expected '{expected}' token"
        if got:
            detail += f", got '{got}'"
        
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={
                "WWW-Authenticate": "Bearer",
                "X-Error-Code": ErrorCode.INVALID_TOKEN_TYPE
            }
        )


class WeakPasswordError(HTTPException):
    """Exception raised when password doesn't meet requirements."""
    
    def __init__(self, message: str = None):
        detail = message or "Password does not meet security requirements"
        
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers={"X-Error-Code": ErrorCode.WEAK_PASSWORD}
        )


class UnauthorizedError(HTTPException):
    """Exception raised when user is not authorized."""
    
    def __init__(self, message: str = "Not authorized"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
            headers={"X-Error-Code": ErrorCode.UNAUTHORIZED}
        )
