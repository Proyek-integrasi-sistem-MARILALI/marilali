from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from collections import defaultdict

from src.budget.models import Expense
from src.itinerary.models import Itinerary
from src.budget.schemas import ExpenseCreate, ExpenseUpdate, BudgetSummary, BudgetReport
from src.activity.exceptions import NotActivityOwnerException
from fastapi import HTTPException


async def verify_itinerary_ownership(itinerary_id: int, user_id: int, db: AsyncSession) -> Itinerary:
    result = await db.execute(
        select(Itinerary).where(Itinerary.id == itinerary_id)
    )
    itinerary = result.scalar_one_or_none()
    
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
    if itinerary.user_id != user_id:
        raise NotActivityOwnerException()
    
    return itinerary


async def create_expense(
    itinerary_id: int,
    user_id: int,
    expense_data: ExpenseCreate,
    db: AsyncSession
) -> Expense:
    itinerary = await verify_itinerary_ownership(itinerary_id, user_id, db)
    
    # Validate expense date is within itinerary range
    if not (itinerary.start_date <= expense_data.expense_date <= itinerary.end_date):
        raise HTTPException(
            status_code=400,
            detail="Expense date must be within itinerary date range"
        )
    
    expense = Expense(
        itinerary_id=itinerary_id,
        activity_id=expense_data.activity_id,
        category=expense_data.category,
        description=expense_data.description,
        amount=expense_data.amount,
        expense_date=expense_data.expense_date,
        payment_method=expense_data.payment_method,
        receipt_url=expense_data.receipt_url,
        notes=expense_data.notes
    )
    
    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    
    return expense


async def get_expenses(
    itinerary_id: int,
    user_id: int,
    db: AsyncSession
) -> List[Expense]:
    await verify_itinerary_ownership(itinerary_id, user_id, db)
    
    result = await db.execute(
        select(Expense)
        .where(Expense.itinerary_id == itinerary_id)
        .order_by(Expense.expense_date.desc(), Expense.created_at.desc())
    )
    
    return list(result.scalars().all())


async def update_expense(
    expense_id: int,
    user_id: int,
    expense_data: ExpenseUpdate,
    db: AsyncSession
) -> Expense:
    result = await db.execute(
        select(Expense)
        .join(Itinerary)
        .where(Expense.id == expense_id)
    )
    expense = result.scalar_one_or_none()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Verify ownership
    itinerary_result = await db.execute(
        select(Itinerary).where(Itinerary.id == expense.itinerary_id)
    )
    itinerary = itinerary_result.scalar_one()
    
    if itinerary.user_id != user_id:
        raise NotActivityOwnerException()
    
    # Update fields
    update_data = expense_data.model_dump(exclude_unset=True)
    
    # Validate date if provided
    if "expense_date" in update_data:
        if not (itinerary.start_date <= update_data["expense_date"] <= itinerary.end_date):
            raise HTTPException(
                status_code=400,
                detail="Expense date must be within itinerary date range"
            )
    
    for field, value in update_data.items():
        setattr(expense, field, value)
    
    await db.commit()
    await db.refresh(expense)
    
    return expense


async def delete_expense(
    expense_id: int,
    user_id: int,
    db: AsyncSession
) -> dict:
    result = await db.execute(
        select(Expense)
        .join(Itinerary)
        .where(Expense.id == expense_id)
    )
    expense = result.scalar_one_or_none()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Verify ownership
    itinerary_result = await db.execute(
        select(Itinerary).where(Itinerary.id == expense.itinerary_id)
    )
    itinerary = itinerary_result.scalar_one()
    
    if itinerary.user_id != user_id:
        raise NotActivityOwnerException()
    
    await db.delete(expense)
    await db.commit()
    
    return {"message": "Expense deleted successfully"}


async def get_budget_summary(
    itinerary_id: int,
    user_id: int,
    db: AsyncSession
) -> BudgetSummary:
    itinerary = await verify_itinerary_ownership(itinerary_id, user_id, db)
    
    # Get all expenses
    expenses_result = await db.execute(
        select(Expense)
        .where(Expense.itinerary_id == itinerary_id)
    )
    expenses = expenses_result.scalars().all()
    
    # Calculate totals
    total_expenses = sum(expense.amount for expense in expenses)
    
    # Group by category
    expenses_by_category = defaultdict(int)
    for expense in expenses:
        expenses_by_category[expense.category] += expense.amount
    
    # Calculate budget metrics
    planned_budget = itinerary.budget
    remaining_budget = (planned_budget - total_expenses) if planned_budget else None
    budget_utilization = (
        (total_expenses / planned_budget * 100) if planned_budget and planned_budget > 0 else None
    )
    is_over_budget = (total_expenses > planned_budget) if planned_budget else False
    
    return BudgetSummary(
        itinerary_id=itinerary_id,
        planned_budget=planned_budget,
        total_expenses=total_expenses,
        remaining_budget=remaining_budget,
        budget_utilization_percentage=round(budget_utilization, 2) if budget_utilization else None,
        is_over_budget=is_over_budget,
        expenses_by_category=dict(expenses_by_category)
    )


async def get_budget_report(
    itinerary_id: int,
    user_id: int,
    db: AsyncSession
) -> BudgetReport:
    summary = await get_budget_summary(itinerary_id, user_id, db)
    expenses = await get_expenses(itinerary_id, user_id, db)
    
    # Get top categories sorted by amount
    top_categories = sorted(
        [{"category": cat, "amount": amt} for cat, amt in summary.expenses_by_category.items()],
        key=lambda x: x["amount"],
        reverse=True
    )
    
    return BudgetReport(
        summary=summary,
        expenses=expenses,
        top_expense_categories=top_categories
    )
