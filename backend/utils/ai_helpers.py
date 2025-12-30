from typing import List, Dict, Any
import math


def calculate_recommendation_score(
    item: Dict,
    user_budget: int,
    weather_score: float,
    user_preferences: Dict = None
) -> float:
    score = 0.0
    weights = {"budget": 0.4, "weather": 0.3, "rating": 0.2, "preferences": 0.1}
    
    # Budget score
    item_price = item.get("price", 0)
    if user_budget > 0:
        if item_price <= user_budget:
            budget_score = 1 - (item_price / user_budget)
        else:
            budget_score = 0.3  # Penalty for over-budget
        score += budget_score * weights["budget"]
    
    # Weather compatibility score
    score += weather_score * weights["weather"]
    
    # Rating score
    rating = item.get("rating", 0)
    if rating > 0:
        rating_score = rating / 5.0
        score += rating_score * weights["rating"]
    
    # User preferences score
    if user_preferences:
        preference_score = calculate_preference_match(item, user_preferences)
        score += preference_score * weights["preferences"]
    
    return round(min(1.0, max(0.0, score)), 2)


def calculate_preference_match(item: Dict, preferences: Dict) -> float:
    score = 0.0
    
    # Match categories/tags
    item_tags = set(item.get("tags", []))
    preferred_tags = set(preferences.get("preferred_tags", []))
    
    if item_tags and preferred_tags:
        match_count = len(item_tags.intersection(preferred_tags))
        score = match_count / len(preferred_tags) if preferred_tags else 0.5
    
    return score


def generate_recommendation_reason(item: Dict, scores: Dict) -> str:
    reasons = []
    
    if scores.get("budget_compatible", True):
        reasons.append("within your budget")
    
    if scores.get("weather_score", 0) > 0.7:
        reasons.append("suitable for weather conditions")
    
    rating = item.get("rating", 0)
    if rating >= 4.5:
        reasons.append("highly rated")
    elif rating >= 4.0:
        reasons.append("well-rated")
    
    if not reasons:
        reasons.append("matches your search criteria")
    
    return "Recommended because it's " + ", ".join(reasons)


def diversify_recommendations(items: List[Dict], max_results: int = 10) -> List[Dict]:
    if len(items) <= max_results:
        return items
    
    # Group by price range
    budget_items = [i for i in items if i.get("price", 0) < 100]
    mid_items = [i for i in items if 100 <= i.get("price", 0) < 300]
    luxury_items = [i for i in items if i.get("price", 0) >= 300]
    
    # Take proportional samples
    result = []
    result.extend(budget_items[:max_results // 3])
    result.extend(mid_items[:max_results // 3])
    result.extend(luxury_items[:max_results // 3])
    
    # Fill remaining with top-scored items
    remaining = max_results - len(result)
    if remaining > 0:
        other_items = [i for i in items if i not in result]
        result.extend(other_items[:remaining])
    
    return result[:max_results]


def predict_user_interest(user_history: List[Dict], new_item: Dict) -> float:
    if not user_history:
        return 0.5  # Neutral score
    
    # Analyze past preferences
    avg_price = sum(h.get("price", 0) for h in user_history) / len(user_history)
    avg_rating = sum(h.get("rating", 0) for h in user_history) / len(user_history)
    
    # Compare with new item
    price_similarity = 1 - abs(new_item.get("price", 0) - avg_price) / max(avg_price, 1)
    rating_similarity = 1 - abs(new_item.get("rating", 0) - avg_rating) / 5.0
    
    interest_score = (price_similarity + rating_similarity) / 2
    return round(min(1.0, max(0.0, interest_score)), 2)
