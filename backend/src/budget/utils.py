def calculate_total_expenses(expenses: list) -> int:
    return sum(expense.amount for expense in expenses)

def calculate_remaining_budget(budget: int, expenses: list) -> int:
    total_expenses = calculate_total_expenses(expenses)
    return budget - total_expenses
