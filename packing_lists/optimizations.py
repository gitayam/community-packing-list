"""
Query optimizations for scaling to 10,000+ users.
Contains optimized versions of views and database queries.
"""

from django.db.models import Prefetch, Count, Avg, F, Case, When, Value, FloatField, Q
from django.core.cache import cache
from django.db import connection
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from .models import PackingList, PackingListItem, Price, Store, Base


def get_optimized_packing_list_items(packing_list_id, base_filter_id=None, radius=50):
    """
    Optimized query for packing list detail view.
    Eliminates N+1 queries using prefetch_related and select_related.
    """
    
    # Base price query with vote aggregation
    price_query = Price.objects.select_related('store').annotate(
        upvotes=Count('votes', filter=Q(votes__is_correct_price=True)),
        downvotes=Count('votes', filter=Q(votes__is_correct_price=False)),
        price_per_unit=F('price') / F('quantity'),
        vote_confidence=Case(
            When(votes__count=0, then=Value(0.0)),
            default=(F('upvotes') - F('downvotes')) / F('votes__count'),
            output_field=FloatField()
        )
    ).order_by('-vote_confidence', 'price_per_unit')
    
    # Geographic filtering if base is specified
    if base_filter_id:
        try:
            base = Base.objects.get(id=base_filter_id)
            if base.latitude and base.longitude:
                # Use PostGIS for efficient geographic queries
                base_point = Point(base.longitude, base.latitude, srid=4326)
                price_query = price_query.filter(
                    store__location__distance_lte=(base_point, radius * 1609.34)  # Convert miles to meters
                ).annotate(
                    distance_from_base=Distance('store__location', base_point)
                ).order_by('distance_from_base', '-vote_confidence', 'price_per_unit')
        except Base.DoesNotExist:
            pass
    
    # Main query with all optimizations
    items = PackingListItem.objects.filter(packing_list_id=packing_list_id).select_related(
        'item', 'packing_list'
    ).prefetch_related(
        Prefetch('item__prices', queryset=price_query[:5])  # Limit to top 5 prices per item
    ).order_by('section', 'item__name')
    
    return items


def get_cached_store_distances(base_id, radius=50, cache_timeout=3600):
    """
    Cache store distances for a base to avoid recalculating.
    """
    cache_key = f'store_distances_{base_id}_{radius}'
    distances = cache.get(cache_key)
    
    if distances is None:
        try:
            base = Base.objects.get(id=base_id)
            if base.latitude and base.longitude:
                base_point = Point(base.longitude, base.latitude, srid=4326)
                
                # Use PostGIS to calculate all distances at once
                stores_with_distance = Store.objects.filter(
                    location__isnull=False
                ).annotate(
                    distance=Distance('location', base_point)
                ).filter(
                    distance__lte=radius * 1609.34  # Convert miles to meters
                ).values('id', 'distance')
                
                distances = {
                    store['id']: store['distance'].m / 1609.34  # Convert back to miles
                    for store in stores_with_distance
                }
                
                cache.set(cache_key, distances, cache_timeout)
        except Base.DoesNotExist:
            distances = {}
    
    return distances


def calculate_smart_scores(prices_data, base_distances=None):
    """
    Optimized smart score calculation using vectorized operations.
    """
    if not prices_data:
        return []
    
    base_price = 50.0  # Normalization constant
    
    for price_data in prices_data:
        price = price_data['price']
        
        # Price score (lower is better)
        price_score = max(0, 1.0 - (price.price_per_unit / base_price))
        
        # Vote score
        vote_score = (price.vote_confidence + 1) / 2  # Convert [-1,1] to [0,1]
        
        # Proximity score
        proximity_score = 0.5  # Default neutral
        if base_distances and price.store_id in base_distances:
            distance = base_distances[price.store_id]
            proximity_score = max(0, 1 - (distance / 50))  # Assuming 50 mile radius
        
        # Weighted smart score
        if base_distances:
            smart_score = (0.6 * price_score) + (0.25 * vote_score) + (0.15 * proximity_score)
        else:
            smart_score = (0.7 * price_score) + (0.3 * vote_score)
        
        price_data['smart_score'] = smart_score
        price_data['distance'] = base_distances.get(price.store_id) if base_distances else None
    
    # Sort by smart score
    prices_data.sort(key=lambda x: x['smart_score'], reverse=True)
    return prices_data


def get_popular_items(limit=50, cache_timeout=3600):
    """
    Get most popular items across all packing lists with caching.
    """
    cache_key = f'popular_items_{limit}'
    popular_items = cache.get(cache_key)
    
    if popular_items is None:
        popular_items = PackingListItem.objects.values(
            'item__id', 'item__name'
        ).annotate(
            usage_count=Count('packing_list', distinct=True),
            total_quantity=Count('id')
        ).order_by('-usage_count', '-total_quantity')[:limit]
        
        cache.set(cache_key, list(popular_items), cache_timeout)
    
    return popular_items


def bulk_update_price_scores():
    """
    Background task to pre-calculate price scores for better performance.
    Should be run periodically via Celery.
    """
    with connection.cursor() as cursor:
        # Update price scores using raw SQL for maximum performance
        cursor.execute("""
            UPDATE packing_lists_price 
            SET smart_score = (
                CASE 
                    WHEN vote_count > 0 THEN
                        0.7 * (1.0 - (price/quantity)/50.0) + 0.3 * ((upvotes - downvotes)::float / vote_count)
                    ELSE
                        0.7 * (1.0 - (price/quantity)/50.0) + 0.15
                END
            )
            FROM (
                SELECT 
                    p.id,
                    COALESCE(v.upvotes, 0) as upvotes,
                    COALESCE(v.downvotes, 0) as downvotes,
                    COALESCE(v.upvotes, 0) + COALESCE(v.downvotes, 0) as vote_count
                FROM packing_lists_price p
                LEFT JOIN (
                    SELECT 
                        price_id,
                        SUM(CASE WHEN is_correct_price THEN 1 ELSE 0 END) as upvotes,
                        SUM(CASE WHEN NOT is_correct_price THEN 1 ELSE 0 END) as downvotes
                    FROM packing_lists_vote 
                    GROUP BY price_id
                ) v ON p.id = v.price_id
            ) scores
            WHERE packing_lists_price.id = scores.id
        """)
        
        return cursor.rowcount


def get_item_price_statistics(item_id, cache_timeout=1800):
    """
    Get cached price statistics for an item.
    """
    cache_key = f'item_price_stats_{item_id}'
    stats = cache.get(cache_key)
    
    if stats is None:
        from django.db.models import Avg, Min, Max, Count, StdDev
        
        stats = Price.objects.filter(item_id=item_id).aggregate(
            avg_price=Avg('price_per_unit'),
            min_price=Min('price_per_unit'),
            max_price=Max('price_per_unit'),
            count=Count('id'),
            std_dev=StdDev('price_per_unit')
        )
        
        # Add confidence breakdown
        confidence_counts = Price.objects.filter(item_id=item_id).values(
            'confidence'
        ).annotate(count=Count('id'))
        
        stats['confidence_breakdown'] = {
            item['confidence']: item['count'] for item in confidence_counts
        }
        
        cache.set(cache_key, stats, cache_timeout)
    
    return stats