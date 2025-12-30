from fastapi import HTTPException, status
from src.user.constants import ErrorCode


class UserNotFoundError(HTTPException):
    def __init__(self, user_id: int = None):
        detail = "User not found"
        if user_id:
            detail = f"User with id {user_id} not found"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers={"X-Error-Code": ErrorCode.USER_NOT_FOUND}
        )


class IncorrectOldPasswordError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
            headers={"X-Error-Code": ErrorCode.INCORRECT_OLD_PASSWORD}
        )


class SamePasswordError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as current password",
            headers={"X-Error-Code": ErrorCode.SAME_PASSWORD}
        )


class ProfileUpdateFailedError(HTTPException):
    def __init__(self, message: str = "Failed to update profile"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message,
            headers={"X-Error-Code": ErrorCode.PROFILE_UPDATE_FAILED}
        )


class AccountDeletionFailedError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account",
            headers={"X-Error-Code": ErrorCode.ACCOUNT_DELETION_FAILED}
        )
