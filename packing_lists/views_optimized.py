"""
Optimized views for scaling to 10,000+ users.
Uses query optimizations, caching, and efficient data structures.
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db.models import Q, Prefetch, Count, Avg
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.contrib import messages

from .models import PackingList, Item, Price, Store, Base
from .optimizations import (
    get_optimized_packing_list_items,
    get_cached_store_distances,
    calculate_smart_scores,
    get_popular_items,
    get_item_price_statistics
)
from .tasks import warm_item_price_statistics_cache


def optimized_packing_list_detail(request, list_id):
    """
    Optimized version of packing_list_detail view.
    Uses prefetch_related to eliminate N+1 queries.
    """
    packing_list = get_object_or_404(PackingList, id=list_id)
    
    # Get filter parameters
    base_filter_id = request.GET.get('base_filter')
    radius = int(request.GET.get('radius', 50))
    
    # Handle packed status toggle
    if request.method == 'POST':
        item_to_toggle_id = request.POST.get('toggle_packed_item_id')
        if item_to_toggle_id:
            try:
                from .models import PackingListItem
                pli = PackingListItem.objects.get(id=item_to_toggle_id, packing_list=packing_list)
                pli.packed = not pli.packed
                pli.save()
                
                messages.success(
                    request, 
                    f"Item '{pli.item.name}' marked as {'packed' if pli.packed else 'unpacked'}."
                )
                
                # Invalidate relevant caches
                cache.delete(f'packing_list_items_{list_id}')
                
            except PackingListItem.DoesNotExist:
                messages.error(request, "Item not found in this list.")
    
    # Use optimized query
    items = get_optimized_packing_list_items(list_id, base_filter_id, radius)
    
    # Get base information for filters
    available_bases = Base.objects.all().order_by('name')
    selected_base = None
    if base_filter_id:
        try:
            selected_base = Base.objects.get(id=base_filter_id)
        except Base.DoesNotExist:
            pass
    
    # Process items for template
    items_with_prices = []
    for item in items:
        prices_data = []
        
        for price in item.item.prices.all():
            prices_data.append({
                'price': price,
                'upvotes': price.upvotes,
                'downvotes': price.downvotes,
                'price_per_unit': price.price_per_unit,
                'vote_confidence': price.vote_confidence
            })
        
        # Calculate smart scores if needed
        if selected_base:
            base_distances = get_cached_store_distances(base_filter_id, radius)
            prices_data = calculate_smart_scores(prices_data, base_distances)
        else:
            prices_data = calculate_smart_scores(prices_data)
        
        items_with_prices.append({
            'pli': item,
            'item': item.item,
            'prices_with_votes': prices_data[:5]  # Limit to top 5 prices
        })
    
    context = {
        'packing_list': packing_list,
        'items_with_prices': items_with_prices,
        'title': packing_list.name,
        'available_bases': available_bases,
        'selected_base': selected_base,
        'selected_radius': radius,
        'base_filter_active': bool(selected_base),
    }
    
    return render(request, 'packing_lists/packing_list_detail.html', context)


@cache_page(60 * 5)  # Cache for 5 minutes
@vary_on_headers('User-Agent')
def optimized_items_page(request):
    """
    Optimized items page with caching and pagination.
    """
    # Get filter parameters
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    has_prices = request.GET.get('has_prices', '')
    store_filter = request.GET.get('store', '')
    base_filter = request.GET.get('base', '')
    
    # Build cache key based on filters
    cache_key = f"items_page_{hash((search_query, category_filter, price_min, price_max, has_prices, store_filter, base_filter))}"
    
    # Try to get from cache first
    cached_data = cache.get(cache_key)
    if cached_data and not request.GET.get('refresh'):
        items_with_data = cached_data['items_with_data']
        filter_data = cached_data['filter_data']
    else:
        # Build optimized query
        items_query = Item.objects.select_related().prefetch_related(
            Prefetch('prices', queryset=Price.objects.select_related('store').order_by('-confidence', 'price')[:3])
        )
        
        # Apply filters
        if search_query:
            items_query = items_query.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        if has_prices == 'yes':
            items_query = items_query.filter(prices__isnull=False).distinct()
        elif has_prices == 'no':
            items_query = items_query.filter(prices__isnull=True)
        
        # Price range filtering
        if price_min or price_max:
            price_filter = Q()
            if price_min:
                try:
                    min_price = float(price_min)
                    price_filter &= Q(prices__price__gte=min_price)
                except ValueError:
                    pass
            if price_max:
                try:
                    max_price = float(price_max)
                    price_filter &= Q(prices__price__lte=max_price)
                except ValueError:
                    pass
            if price_filter:
                items_query = items_query.filter(price_filter).distinct()
        
        # Store and location filtering
        if store_filter:
            items_query = items_query.filter(prices__store__id=store_filter).distinct()
        
        # Base proximity filtering
        if base_filter:
            try:
                base = Base.objects.get(id=base_filter)
                if base.latitude and base.longitude:
                    # Get stores within radius
                    nearby_stores = get_cached_store_distances(base_filter, radius=25)
                    if nearby_stores:
                        items_query = items_query.filter(
                            prices__store__id__in=nearby_stores.keys()
                        ).distinct()
            except Base.DoesNotExist:
                pass
        
        # Execute query with limits
        items = items_query[:200]  # Limit to 200 items max
        
        # Process items with price data
        items_with_data = []
        item_ids_for_cache_warming = []
        
        for item in items:
            prices = list(item.prices.all())
            
            if prices:
                # Calculate best price and aggregate stats
                best_price_data = None
                total_prices = len(prices)
                price_range = None
                
                if prices:
                    min_price = min(p.price_per_unit for p in prices)
                    max_price = max(p.price_per_unit for p in prices)
                    
                    if total_prices > 1:
                        price_range = f"${min_price:.2f} - ${max_price:.2f}"
                    
                    # Find best price (considering votes and confidence)
                    best_price = prices[0]  # Already sorted by confidence and price
                    
                    best_price_data = {
                        'price': best_price,
                        'price_per_unit': best_price.price_per_unit,
                        'vote_confidence': getattr(best_price, 'vote_confidence', 0)
                    }
                
                item_ids_for_cache_warming.append(item.id)
            else:
                best_price_data = None
                total_prices = 0
                price_range = None
            
            items_with_data.append({
                'item': item,
                'best_price': best_price_data,
                'total_prices': total_prices,
                'price_range': price_range,
            })
        
        # Warm cache for price statistics asynchronously
        if item_ids_for_cache_warming:
            warm_item_price_statistics_cache.delay(item_ids_for_cache_warming[:50])
        
        # Get filter data for dropdowns
        filter_data = {
            'available_stores': Store.objects.filter(prices__isnull=False).distinct().order_by('name')[:50],
            'available_bases': Base.objects.all().order_by('name'),
            'popular_items': get_popular_items(limit=20),
        }
        
        # Cache the results
        cache.set(cache_key, {
            'items_with_data': items_with_data,
            'filter_data': filter_data
        }, timeout=300)  # 5 minutes
    
    # Pagination
    paginator = Paginator(items_with_data, 20)  # Show 20 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'items_with_data': page_obj,
        'popular_items': filter_data['popular_items'],
        'available_stores': filter_data['available_stores'],
        'available_bases': filter_data['available_bases'],
        'search_query': search_query,
        'category_filter': category_filter,
        'price_min': price_min,
        'price_max': price_max,
        'has_prices': has_prices,
        'store_filter': store_filter,
        'base_filter': base_filter,
        'page_obj': page_obj,
    }
    
    return render(request, 'packing_lists/items.html', context)


class OptimizedPackingListListView(ListView):
    """
    Optimized list view for packing lists with caching.
    """
    model = PackingList
    template_name = 'packing_lists/lists.html'
    context_object_name = 'packing_lists'
    paginate_by = 20
    
    @method_decorator(cache_page(60 * 10))  # Cache for 10 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return PackingList.objects.select_related('school', 'base').prefetch_related(
            Prefetch('items', queryset=PackingListItem.objects.select_related('item')[:5])
        ).order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add statistics
        cache_key = 'packing_lists_stats'
        stats = cache.get(cache_key)
        
        if stats is None:
            stats = {
                'total_lists': PackingList.objects.count(),
                'total_items': Item.objects.count(),
                'total_prices': Price.objects.count(),
                'popular_items': get_popular_items(limit=10),
            }
            cache.set(cache_key, stats, timeout=1800)  # 30 minutes
        
        context.update(stats)
        return context


def get_item_price_data_api(request, item_id):
    """
    API endpoint for getting item price data with caching.
    """
    cache_key = f'item_price_api_{item_id}'
    data = cache.get(cache_key)
    
    if data is None:
        try:
            item = Item.objects.get(id=item_id)
            stats = get_item_price_statistics(item_id)
            
            # Get recent prices
            recent_prices = Price.objects.filter(item=item).select_related('store').order_by('-created_at')[:10]
            
            prices_data = []
            for price in recent_prices:
                prices_data.append({
                    'price': float(price.price),
                    'store_name': price.store.name,
                    'confidence': price.confidence,
                    'date': price.created_at.isoformat() if price.created_at else None,
                    'price_per_unit': float(price.price_per_unit),
                })
            
            data = {
                'item_name': item.name,
                'statistics': {
                    'avg_price': float(stats['avg_price']) if stats['avg_price'] else None,
                    'min_price': float(stats['min_price']) if stats['min_price'] else None,
                    'max_price': float(stats['max_price']) if stats['max_price'] else None,
                    'count': stats['count'],
                    'std_dev': float(stats['std_dev']) if stats['std_dev'] else None,
                },
                'recent_prices': prices_data,
                'confidence_breakdown': stats['confidence_breakdown'],
            }
            
            cache.set(cache_key, data, timeout=600)  # 10 minutes
            
        except Item.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=404)
    
    return JsonResponse(data)