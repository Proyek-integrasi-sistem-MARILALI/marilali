from typing import List, Dict, Any


def calculate_total_budget(flights: List[Dict], accommodations: List[Dict], activities: List[Dict]) -> Dict[str, Any]:
    flight_total = sum(f.get("price", 0) for f in flights)
    accommodation_total = sum(a.get("total_price", 0) for a in accommodations)
    activity_total = sum(act.get("price", 0) for act in activities)
    
    total = flight_total + accommodation_total + activity_total
    
    return {
        "flights": flight_total,
        "accommodations": accommodation_total,
        "activities": activity_total,
        "total": total,
        "breakdown": {
            "flights_percentage": round((flight_total / total * 100) if total > 0 else 0, 2),
            "accommodations_percentage": round((accommodation_total / total * 100) if total > 0 else 0, 2),
            "activities_percentage": round((activity_total / total * 100) if total > 0 else 0, 2)
        }
    }


def optimize_budget_allocation(total_budget: int, trip_days: int) -> Dict[str, int]:
    # Typical allocation: 40% flights, 35% accommodation, 25% activities/food
    return {
        "suggested_flight_budget": int(total_budget * 0.40),
        "suggested_accommodation_budget": int(total_budget * 0.35),
        "suggested_activity_budget": int(total_budget * 0.25),
        "daily_budget": int(total_budget / trip_days) if trip_days > 0 else total_budget
    }


def check_budget_status(spent: int, budget: int) -> Dict[str, Any]:
    remaining = budget - spent
    percentage_used = (spent / budget * 100) if budget > 0 else 0
    
    status = "healthy"
    if percentage_used >= 90:
        status = "critical"
    elif percentage_used >= 75:
        status = "warning"
    
    return {
        "spent": spent,
        "budget": budget,
        "remaining": remaining,
        "percentage_used": round(percentage_used, 2),
        "status": status,
        "message": get_budget_message(status, remaining)
    }


def get_budget_message(status: str, remaining: int) -> str:
    if status == "critical":
        return f"Budget almost exhausted! Only Rp {remaining:,} remaining."
    elif status == "warning":
        return f"Approaching budget limit. Rp {remaining:,} remaining."
    else:
        return f"Budget is healthy. Rp {remaining:,} remaining."


def find_budget_friendly_alternatives(items: List[Dict], max_price: int) -> List[Dict]:
    affordable = [item for item in items if item.get("price", 0) <= max_price]
    return sorted(affordable, key=lambda x: x.get("price", 0))
