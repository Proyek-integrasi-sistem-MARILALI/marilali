from pydantic import Field, ConfigDict
from typing import Optional
from datetime import date, datetime
from src.schemas import CustomModel


class ExpenseBase(CustomModel):
    category: str = Field(..., max_length=100)
    description: str = Field(..., min_length=1, max_length=200)
    amount: int = Field(..., gt=0)
    expense_date: date
    payment_method: Optional[str] = Field(None, max_length=50)
    receipt_url: Optional[str] = None
    notes: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    activity_id: Optional[int] = None


class ExpenseUpdate(CustomModel):
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    amount: Optional[int] = Field(None, gt=0)
    expense_date: Optional[date] = None
    payment_method: Optional[str] = Field(None, max_length=50)
    receipt_url: Optional[str] = None
    notes: Optional[str] = None


class ExpenseResponse(ExpenseBase):
    id: int
    itinerary_id: int
    activity_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BudgetSummary(CustomModel):
    itinerary_id: int
    planned_budget: Optional[int] = None
    total_expenses: int
    remaining_budget: Optional[int] = None
    budget_utilization_percentage: Optional[float] = None
    is_over_budget: bool
    expenses_by_category: dict[str, int]


class BudgetReport(CustomModel):
    summary: BudgetSummary
    expenses: list[ExpenseResponse]
    top_expense_categories: list[dict[str, int]]
