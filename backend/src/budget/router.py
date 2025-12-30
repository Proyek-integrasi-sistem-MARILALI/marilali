from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.budget import service
from src.budget.schemas import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    BudgetSummary,
    BudgetReport
)
from src.auth.security import get_current_user
from src.database import get_db
from src.user.models import User


router = APIRouter()


@router.post("/itinerary/{itinerary_id}/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    itinerary_id: int,
    expense_data: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.create_expense(itinerary_id, current_user.id, expense_data, db)


@router.get("/itinerary/{itinerary_id}/expenses", response_model=List[ExpenseResponse])
async def get_expenses(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_expenses(itinerary_id, current_user.id, db)


@router.get("/itinerary/{itinerary_id}/budget/summary", response_model=BudgetSummary)
async def get_budget_summary(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_budget_summary(itinerary_id, current_user.id, db)


@router.get("/itinerary/{itinerary_id}/budget/report", response_model=BudgetReport)
async def get_budget_report(
    itinerary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_budget_report(itinerary_id, current_user.id, db)


@router.put("/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.update_expense(expense_id, current_user.id, expense_data, db)


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_200_OK)
async def delete_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.delete_expense(expense_id, current_user.id, db)
