from fastapi import HTTPException, status

class ExpenseNotFoundError(HTTPException):
    def __init__(self, expense_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id {expense_id} not found"
        )

class InvalidExpenseAmountError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expense amount must be greater than 0"
        )
