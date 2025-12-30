from typing import Any, TypeVar, Generic
from datetime import datetime, timezone
from pydantic import BaseModel


T = TypeVar('T')


class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 100
    
    def __init__(self, skip: int = 0, limit: int = 100):
        super().__init__(skip=skip, limit=limit)
        if self.limit > 100:
            self.limit = 100
        if self.skip < 0:
            self.skip = 0


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int
    has_more: bool
    
    @classmethod
    def create(cls, items: list[T], total: int, skip: int, limit: int):
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + limit) < total
        )


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_string(text: str | None) -> str | None:
    if text is None:
        return None
    return text.strip().lower()


def sanitize_email(email: str) -> str:
    return email.strip().lower()


def calculate_average(values: list[int | float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def format_price(price: int) -> str:
    return f"Rp {price:,.0f}".replace(",", ".")


def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
    return end_date > start_date


def create_success_response(
    message: str,
    data: Any = None,
    status_code: int = 200
) -> dict[str, Any]:
    response = {
        "success": True,
        "message": message,
        "status_code": status_code
    }
    
    if data is not None:
        response["data"] = data
    
    return response


def create_error_response(
    message: str,
    error_code: str | None = None,
    status_code: int = 400
) -> dict[str, Any]:
    response = {
        "success": False,
        "message": message,
        "status_code": status_code
    }
    
    if error_code:
        response["error_code"] = error_code
    
    return response
