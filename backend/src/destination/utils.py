def filter_by_price_range(destinations: list, min_price: int, max_price: int):
    return [d for d in destinations if min_price <= (d.price or 0) <= max_price]
