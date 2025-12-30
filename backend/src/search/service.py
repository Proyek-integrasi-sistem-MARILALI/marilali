from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from src.search.models import SearchHistory, PopularSearch


async def log_search(
    user_id: int,
    search_type: str,
    query: str,
    filters: Optional[Dict],
    results_count: int,
    db: AsyncSession
) -> SearchHistory:
    search = SearchHistory(
        user_id=user_id,
        search_type=search_type,
        query=query,
        filters=filters,
        results_count=results_count,
        timestamp=datetime.utcnow()
    )
    
    db.add(search)
    
    # Update popular searches
    await _update_popular_searches(search_type, query, db)
    
    await db.commit()
    await db.refresh(search)
    
    return search


async def _update_popular_searches(
    search_type: str,
    query: str,
    db: AsyncSession
):
    # Normalize query
    normalized_query = query.lower().strip()
    
    if not normalized_query:
        return
    
    # Check if exists
    result = await db.execute(
        select(PopularSearch).where(
            and_(
                PopularSearch.search_type == search_type,
                PopularSearch.query == normalized_query
            )
        )
    )
    
    popular = result.scalar_one_or_none()
    
    if popular:
        popular.search_count += 1
        popular.last_searched = datetime.utcnow()
    else:
        popular = PopularSearch(
            search_type=search_type,
            query=normalized_query,
            search_count=1,
            first_searched=datetime.utcnow(),
            last_searched=datetime.utcnow()
        )
        db.add(popular)


async def get_user_search_history(
    user_id: int,
    search_type: Optional[str],
    limit: int,
    db: AsyncSession
) -> List[SearchHistory]:
    query = select(SearchHistory).where(SearchHistory.user_id == user_id)
    
    if search_type:
        query = query.where(SearchHistory.search_type == search_type)
    
    query = query.order_by(SearchHistory.timestamp.desc()).limit(limit)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_popular_searches(
    search_type: str,
    limit: int,
    min_count: int,
    db: AsyncSession
) -> List[PopularSearch]:
    query = (
        select(PopularSearch)
        .where(
            and_(
                PopularSearch.search_type == search_type,
                PopularSearch.search_count >= min_count
            )
        )
        .order_by(desc(PopularSearch.search_count))
        .limit(limit)
    )
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_trending_searches(
    search_type: str,
    days: int,
    limit: int,
    db: AsyncSession
) -> List[Dict]:
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # Query searches in time period
    result = await db.execute(
        select(
            SearchHistory.query,
            func.count(SearchHistory.id).label("count")
        )
        .where(
            and_(
                SearchHistory.search_type == search_type,
                SearchHistory.timestamp >= since_date
            )
        )
        .group_by(SearchHistory.query)
        .order_by(desc("count"))
        .limit(limit)
    )
    
    trending = []
    for row in result.all():
        trending.append({
            "query": row.query,
            "count": row.count,
            "period_days": days
        })
    
    return trending


async def get_search_analytics(
    user_id: int,
    days: int,
    db: AsyncSession
) -> Dict:
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # Total searches
    total_result = await db.execute(
        select(func.count(SearchHistory.id))
        .where(
            and_(
                SearchHistory.user_id == user_id,
                SearchHistory.timestamp >= since_date
            )
        )
    )
    total_searches = total_result.scalar()
    
    # By type
    type_result = await db.execute(
        select(
            SearchHistory.search_type,
            func.count(SearchHistory.id).label("count")
        )
        .where(
            and_(
                SearchHistory.user_id == user_id,
                SearchHistory.timestamp >= since_date
            )
        )
        .group_by(SearchHistory.search_type)
    )
    
    by_type = {}
    for row in type_result.all():
        by_type[row.search_type] = row.count
    
    # Average results
    avg_result = await db.execute(
        select(func.avg(SearchHistory.results_count))
        .where(
            and_(
                SearchHistory.user_id == user_id,
                SearchHistory.timestamp >= since_date
            )
        )
    )
    avg_results = avg_result.scalar() or 0
    
    # Most common filters
    filters_result = await db.execute(
        select(SearchHistory.filters)
        .where(
            and_(
                SearchHistory.user_id == user_id,
                SearchHistory.timestamp >= since_date,
                SearchHistory.filters.isnot(None)
            )
        )
    )
    
    all_filters = []
    for row in filters_result.scalars().all():
        if row:
            all_filters.extend(row.keys())
    
    filter_counts = {}
    for f in all_filters:
        filter_counts[f] = filter_counts.get(f, 0) + 1
    
    return {
        "period_days": days,
        "total_searches": total_searches,
        "by_type": by_type,
        "avg_results_per_search": round(avg_results, 1),
        "common_filters": dict(sorted(filter_counts.items(), key=lambda x: x[1], reverse=True)[:5])
    }


async def clear_search_history(
    user_id: int,
    db: AsyncSession
) -> Dict:
    result = await db.execute(
        select(SearchHistory).where(SearchHistory.user_id == user_id)
    )
    searches = result.scalars().all()
    
    count = len(searches)
    
    for search in searches:
        await db.delete(search)
    
    await db.commit()
    
    return {
        "message": f"Cleared {count} search records",
        "deleted_count": count
    }


async def get_search_suggestions(
    query: str,
    search_type: str,
    limit: int,
    db: AsyncSession
) -> List[str]:
    normalized_query = query.lower().strip()
    
    if not normalized_query:
        # Return top popular searches
        popular = await get_popular_searches(search_type, limit, 3, db)
        return [p.query for p in popular]
    
    # Find matching popular searches
    result = await db.execute(
        select(PopularSearch.query)
        .where(
            and_(
                PopularSearch.search_type == search_type,
                PopularSearch.query.like(f"%{normalized_query}%")
            )
        )
        .order_by(desc(PopularSearch.search_count))
        .limit(limit)
    )
    
    suggestions = [row[0] for row in result.all()]
    
    return suggestions
