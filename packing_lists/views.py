from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages # For feedback to the user
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from .models import PackingList, Item, PackingListItem, School, Price, Vote, Store, Base
from .forms import PackingListForm, PriceForm, VoteForm, PackingListItemForm, StoreForm, ItemForm
from django.db.models import Q
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime
from reportlab.lib.utils import simpleSplit
from django.template.loader import render_to_string
import logging

# Requires login for actions that modify data if user accounts are active
# from django.contrib.auth.decorators import login_required


def home(request):
    """
    Home page view.
    Displays existing packing lists and links to create/upload new ones.
    """
    try:
        packing_lists = PackingList.objects.all().order_by('-id') # Show newest first, or by name, etc.
    except Exception as e:
        # Handle case where database tables don't exist yet - try auto-migration
        if 'relation' in str(e) or 'table' in str(e).lower():
            try:
                from django.core.management import call_command
                call_command('migrate', verbosity=0)
                # Try again after migration
                packing_lists = PackingList.objects.all().order_by('-id')
            except Exception:
                packing_lists = []
        else:
            packing_lists = []
    
    context = {
        'packing_lists': packing_lists,
    }
    return render(request, 'packing_lists/home.html', context)

def create_packing_list(request):
    """
    View for creating a new PackingList manually.
    """
    if request.method == 'POST':
        form = PackingListForm(request.POST)
        if form.is_valid():
            packing_list = form.save()
            messages.success(request, f"Packing list '{packing_list.name}' created successfully!")
            # Redirect to the detail view of the newly created list, or to a page to add items
            # For now, redirecting to home. The detail view URL needs to be 'view_packing_list'
            return redirect(reverse('view_packing_list', args=[packing_list.id]))
    else:
        form = PackingListForm()

    context = {
        'form': form,
        'title': 'Create New Packing List'
    }
    return render(request, 'packing_lists/packing_list_form.html', context)


def packing_list_detail(request, list_id):
    """
    Displays a single packing list, its items, and allows checking off items.
    Also shows current pricing information (voting/adding prices will be separate).
    """
    packing_list = get_object_or_404(PackingList, id=list_id)
    
    # Get base filter parameters
    base_filter_id = request.GET.get('base_filter')
    radius = int(request.GET.get('radius', 50))  # Default 50 miles
    
    # Get all available bases for the dropdown
    available_bases = Base.objects.all().order_by('name')
    selected_base = None
    if base_filter_id:
        try:
            selected_base = Base.objects.get(id=base_filter_id)
        except Base.DoesNotExist:
            pass
    
    # Get all items for this list, ordered perhaps by 'id' or 'item__name'
    # .select_related('item') helps optimize by fetching related Item objects in the same query
    list_items = packing_list.items.select_related('item').order_by('item__name')

    # Handle toggling the 'packed' status of an item
    if request.method == 'POST':
        item_to_toggle_id = request.POST.get('toggle_packed_item_id')
        if item_to_toggle_id:
            try:
                pli_to_toggle = PackingListItem.objects.get(id=item_to_toggle_id, packing_list=packing_list)
                pli_to_toggle.packed = not pli_to_toggle.packed
                pli_to_toggle.save()
                messages.success(request, f"Item '{pli_to_toggle.item.name}' marked as {'packed' if pli_to_toggle.packed else 'unpacked'}.")
            except PackingListItem.DoesNotExist:
                messages.error(request, "Item not found in this list.")
            # Redirect to the same page to show the change and avoid form resubmission issues
            return redirect(reverse('view_packing_list', args=[list_id]))

    # Prepare items with their prices for the template
    # For each PackingListItem, we want to find prices for its Item.
    items_with_prices = []
    for pli in list_items:
        # Fetch all prices for the item
        prices_query = pli.item.prices.select_related('store').all()
        
        # Filter prices by base proximity if base filter is active
        if selected_base and selected_base.latitude and selected_base.longitude:
            # Filter stores within radius (simplified - in production would use proper geo queries)
            filtered_prices = []
            for price in prices_query:
                if price.store.latitude and price.store.longitude:
                    # Calculate distance using Haversine formula (simplified)
                    distance = calculate_distance(
                        selected_base.latitude, selected_base.longitude,
                        price.store.latitude, price.store.longitude
                    )
                    if distance <= radius:
                        price.distance_from_base = distance
                        filtered_prices.append(price)
            prices = filtered_prices
        else:
            prices = list(prices_query)
        
        # Calculate vote counts and smart score for each price
        prices_with_votes = []
        for price in prices:
            upvotes = price.votes.filter(is_correct_price=True).count()
            downvotes = price.votes.filter(is_correct_price=False).count()
            
            # Calculate vote confidence (net votes / total votes)
            total_votes = upvotes + downvotes
            vote_confidence = (upvotes - downvotes) / max(total_votes, 1)  # Avoid division by zero
            
            # Calculate price per unit
            price_per_unit = float(price.price) / max(price.quantity, 1)
            
            # Smart scoring algorithm:
            # - Lower price gets higher score (inverted)
            # - Higher vote confidence gets higher score
            # - Proximity bonus if base filtering is active
            # - Balance: 60% price, 25% vote confidence, 15% proximity
            base_price = 50.0  # Default normalization price
            price_score = 1.0 - (price_per_unit / base_price)  # Lower price = higher score
            vote_score = (vote_confidence + 1) / 2  # Convert from [-1,1] to [0,1]
            
            # Proximity bonus (closer stores get higher scores)
            proximity_score = 0.5  # Default neutral score
            if selected_base and hasattr(price, 'distance_from_base'):
                # Closer = higher score (max distance in radius gets 0, min gets 1)
                proximity_score = max(0, 1 - (price.distance_from_base / radius))
            
            if selected_base:
                smart_score = (0.6 * price_score) + (0.25 * vote_score) + (0.15 * proximity_score)
            else:
                smart_score = (0.7 * price_score) + (0.3 * vote_score)
            
            prices_with_votes.append({
                'price': price,
                'upvotes': upvotes,
                'downvotes': downvotes,
                'vote_confidence': vote_confidence,
                'price_per_unit': price_per_unit,
                'smart_score': smart_score,
                'distance_from_base': getattr(price, 'distance_from_base', None)
            })
        
        # Sort prices by smart score (highest first = best value)
        prices_with_votes.sort(key=lambda x: x['smart_score'], reverse=True)
        
        items_with_prices.append({
            'pli': pli, # The PackingListItem object (contains quantity, notes, packed status)
            'item': pli.item, # The Item object (name, description)
            'prices_with_votes': prices_with_votes # List of price dicts with vote counts, sorted by smart score
        })

    context = {
        'packing_list': packing_list,
        'items_with_prices': items_with_prices, # Use this in the template
        'title': packing_list.name,
        'available_bases': available_bases,
        'selected_base': selected_base,
        'selected_radius': radius,
        'base_filter_active': bool(selected_base),
    }
    return render(request, 'packing_lists/packing_list_detail.html', context)


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) using Haversine formula.
    Returns distance in miles.
    """
    import math
    
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in miles
    r = 3956
    
    return c * r

# @login_required (if user accounts are implemented)
def add_price_for_item(request, item_id, list_id=None): # list_id is for redirecting back
    from .security import should_block_submission, get_client_ip
    
    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST':
        # Security: Check if submission should be blocked
        ip_address = get_client_ip(request)
        is_blocked, block_reason = should_block_submission(ip_address)
        
        if is_blocked:
            messages.error(request, f"Submission blocked: {block_reason}")
            form = PriceForm()
            context = {
                'form': form,
                'item': item,
                'list_id': list_id,
                'title': f"Add Price for {item.name}"
            }
            return render(request, 'packing_lists/price_form.html', context)
        
        post_data = request.POST.copy()
        store_value = post_data.get('store')
        store_name = post_data.get('store_name', '').strip()
        # If user selected 'Add new store...'
        if store_value == '__add_new__':
            if not store_name:
                messages.error(request, "Please provide a name for the new store.")
                form = PriceForm(post_data)
                context = {
                    'form': form,
                    'item': item,
                    'list_id': list_id,
                    'title': f"Add Price for {item.name}"
                }
                return render(request, 'packing_lists/price_form.html', context)
            # Create store with just the name (form will handle this in its save method)
            # The form's save method will create the store if store_name is provided
            post_data['store'] = ''  # Clear store selection to force form to use store_name
        form = PriceForm(post_data)
        if form.is_valid():
            try:
                # Pass request for IP tracking and security
                price = form.save(commit=True, item_instance=item, request=request)
                messages.success(request, f"Price for '{item.name}' at '{price.store.name}' added successfully.")
                if list_id:
                    return redirect(reverse('view_packing_list', args=[list_id]))
                else:
                    return redirect(reverse('home'))
            except ValueError as e:
                messages.error(request, str(e))
            except IntegrityError:
                messages.error(request, "There was an error saving the price. It might already exist or there's a data conflict.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PriceForm() # No initial data needed unless editing

    context = {
        'form': form,
        'item': item,
        'list_id': list_id, # Pass for the "cancel" link or form action
        'title': f"Add Price for {item.name}"
    }
    return render(request, 'packing_lists/price_form.html', context)


# @login_required (if user accounts are implemented)
def handle_vote(request):
    if request.method == 'POST':
        # Support both AJAX and form submissions
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        # Determine if it's an upvote or downvote based on the button name/value
        vote_type = None
        price_id = None
        
        if 'upvote_price_id' in request.POST:
            vote_type = 'up'
            price_id = request.POST.get('upvote_price_id')
        elif 'downvote_price_id' in request.POST:
            vote_type = 'down'
            price_id = request.POST.get('downvote_price_id')
        elif 'price_id' in request.POST and 'vote_type' in request.POST:
            # AJAX format
            price_id = request.POST.get('price_id')
            vote_type = request.POST.get('vote_type')
        else:
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'Invalid vote submission.'})
            messages.error(request, "Invalid vote submission.")
            return redirect(request.META.get('HTTP_REFERER', reverse('home')))

        # Construct form data for VoteForm
        form_data = {
            'price_id': price_id,
            'is_correct_price': vote_type == 'up'
        }
        
        form = VoteForm(form_data, vote_type=vote_type)

        if form.is_valid():
            price_id = form.cleaned_data.get('price_id')
            is_correct = form.cleaned_data.get('is_correct_price')

            try:
                price_instance = Price.objects.get(id=price_id)
            except Price.DoesNotExist:
                if is_ajax:
                    return JsonResponse({'success': False, 'message': 'Price not found.'})
                messages.error(request, "Price not found.")
                return redirect(request.META.get('HTTP_REFERER', reverse('home')))

            ip_address = request.META.get('REMOTE_ADDR')
            Vote.objects.create(
                price=price_instance,
                is_correct_price=is_correct,
                ip_address=ip_address
            )
            
            if is_ajax:
                # Return updated vote counts
                upvotes = price_instance.votes.filter(is_correct_price=True).count()
                downvotes = price_instance.votes.filter(is_correct_price=False).count()
                return JsonResponse({
                    'success': True,
                    'message': f"{'Upvoted' if is_correct else 'Downvoted'} price for '{price_instance.item.name}'",
                    'upvotes': upvotes,
                    'downvotes': downvotes
                })
            else:
                if is_correct:
                    messages.success(request, f"Upvoted price for '{price_instance.item.name}' (from IP: {ip_address}).")
                else:
                    messages.success(request, f"Downvoted price for '{price_instance.item.name}'.")
        else:
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'Invalid vote data.'})
            messages.error(request, "Invalid vote data.")
        
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Unknown error occurred.'})
        
        redirect_url = request.META.get('HTTP_REFERER', reverse('home'))
        return redirect(redirect_url)
    return redirect(reverse('home'))


def store_list(request):
    """
    Displays a list of stores with filtering options:
    - By city, state, zip (text input)
    - By proximity to a selected School/Base
    - By proximity to user's current location (GPS)
    """
    stores_qs = Store.objects.all().order_by('name')
    schools = School.objects.filter(latitude__isnull=False, longitude__isnull=False).order_by('name')

    # Get filter parameters from GET request
    city_filter = request.GET.get('city', '').strip()
    state_filter = request.GET.get('state', '').strip()
    zip_filter = request.GET.get('zip_code', '').strip()
    selected_school_id = request.GET.get('school_id', '').strip()
    user_lat = request.GET.get('user_lat', '').strip()
    user_lon = request.GET.get('user_lon', '').strip()

    # Apply text filters
    if city_filter:
        stores_qs = stores_qs.filter(city__icontains=city_filter)
    if state_filter:
        stores_qs = stores_qs.filter(state__icontains=state_filter)
    if zip_filter:
        stores_qs = stores_qs.filter(zip_code__icontains=zip_filter)

    # Calculate distances if location is provided (either school or user GPS)
    # This list will hold (store, distance) tuples if sorting by distance
    stores_with_distance = []
    sort_by_distance = False

    target_lat, target_lon = None, None
    filter_description = "All Stores"

    if selected_school_id:
        try:
            selected_school = School.objects.get(id=selected_school_id, latitude__isnull=False, longitude__isnull=False)
            target_lat, target_lon = selected_school.latitude, selected_school.longitude
            filter_description = f"Stores near {selected_school.name}"
            sort_by_distance = True
        except School.DoesNotExist:
            messages.warning(request, "Selected school not found or has no location data.")
    elif user_lat and user_lon:
        try:
            target_lat, target_lon = float(user_lat), float(user_lon)
            filter_description = "Stores near your current location"
            sort_by_distance = True
        except ValueError:
            messages.warning(request, "Invalid GPS coordinates provided.")

    if sort_by_distance and target_lat is not None and target_lon is not None:
        temp_stores_with_distance = []
        for store in stores_qs.filter(latitude__isnull=False, longitude__isnull=False):
            distance = haversine(target_lat, target_lon, store.latitude, store.longitude)
            temp_stores_with_distance.append({'store': store, 'distance': distance})

        # Sort by distance
        temp_stores_with_distance.sort(key=lambda x: x['distance'])
        # stores_qs is now a list of dicts, not a queryset
        stores_to_display = temp_stores_with_distance
    else:
        # If not sorting by distance, stores_qs remains a queryset
        # To keep a consistent structure for the template, wrap in the same dict structure
        stores_to_display = [{'store': store, 'distance': None} for store in stores_qs]


    context = {
        'stores': stores_to_display,
        'schools': schools,
        'filter_description': filter_description,
        'current_filters': { # For repopulating form
            'city': city_filter,
            'state': state_filter,
            'zip_code': zip_filter,
            'school_id': selected_school_id,
            'user_lat': user_lat,
            'user_lon': user_lon,
        },
        'title': 'Find Stores'
    }
    return render(request, 'packing_lists/store_list.html', context)

def test_ajax(request):
    """Test view for debugging."""
    return JsonResponse({'success': True, 'message': 'Test response'})

def add_store_ajax(request):
    """Simple AJAX view for adding stores."""
    return JsonResponse({'success': True, 'message': 'Test response'})

def add_item_to_list(request, list_id):
    """
    View to add a new PackingListItem to a PackingList.
    """
    packing_list = get_object_or_404(PackingList, id=list_id)
    if request.method == 'POST':
        form = PackingListItemForm(request.POST)
        if form.is_valid():
            pli = form.save(commit=False)
            pli.packing_list = packing_list
            try:
                pli.save()
                messages.success(request, f"Item '{pli.item.name}' added to packing list '{packing_list.name}'.")
                return redirect(reverse('view_packing_list', args=[packing_list.id]))
            except IntegrityError:
                form.add_error('item', 'This item is already in the list.')
    else:
        form = PackingListItemForm()
    context = {
        'form': form,
        'packing_list': packing_list,
        'title': f"Add Item to {packing_list.name}",
    }
    return render(request, 'packing_lists/packing_listitem_form.html', context)


def edit_item_in_list(request, list_id, pli_id):
    """
    View to edit an existing PackingListItem in a PackingList.
    """
    packing_list = get_object_or_404(PackingList, id=list_id)
    pli = get_object_or_404(PackingListItem, id=pli_id, packing_list=packing_list)
    if request.method == 'POST':
        form = PackingListItemForm(request.POST, instance=pli)
        if form.is_valid():
            form.save()
            messages.success(request, f"Item '{pli.item.name}' updated in packing list '{packing_list.name}'.")
            return redirect(reverse('view_packing_list', args=[packing_list.id]))
    else:
        form = PackingListItemForm(instance=pli)
    context = {
        'form': form,
        'packing_list': packing_list,
        'pli': pli,
        'title': f"Edit Item in {packing_list.name}",
    }
    return render(request, 'packing_lists/packing_listitem_form.html', context)

def store_edit(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, f"Store '{store.name}' updated successfully.")
            return redirect('store_list')
    else:
        form = StoreForm(instance=store)
    return render(request, 'packing_lists/store_form.html', {'form': form, 'store': store, 'title': f"Edit Store: {store.name}"})

def price_form_partial(request, item_id, list_id=None):
    from .security import should_block_submission, get_client_ip
    import logging
    logger = logging.getLogger(__name__)
    item = get_object_or_404(Item, id=item_id)
    price_id = request.GET.get('price_id')
    price_instance = None
    if price_id:
        try:
            price_instance = Price.objects.get(id=price_id, item=item)
        except Price.DoesNotExist:
            pass
    if request.method == 'POST':
        if not price_instance:
            ip_address = get_client_ip(request)
            is_blocked, block_reason = should_block_submission(ip_address)
            if is_blocked:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'html': f'<div class="alert alert-danger">Submission blocked: {block_reason}</div>'})
                else:
                    messages.error(request, f"Submission blocked: {block_reason}")
                    return redirect('items')
        post_data = request.POST.copy()
        # Always ensure new fields are present
        for field in ['store_name', 'store_city', 'store_state']:
            if field not in post_data:
                post_data[field] = ''
        store_value = post_data.get('store')
        store_name = post_data.get('store_name', '').strip()
        if store_value == '__add_new__':
            if not store_name:
                form = PriceForm(post_data)
                context = {
                    'form': form,
                    'item': item,
                    'list_id': list_id,
                    'title': f"{'Edit' if price_instance else 'Add'} Price for {item.name}",
                    'is_modal': True,
                }
                html = render_to_string('packing_lists/price_form_modal.html', context, request=request)
                return JsonResponse({'success': False, 'html': html})
            post_data['store'] = ''
        if price_instance:
            form = PriceForm(post_data, instance=price_instance)
        else:
            form = PriceForm(post_data)
        if form.is_valid():
            try:
                price = form.save(commit=True, item_instance=item, request=request)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                else:
                    messages.success(request, f"Price for '{item.name}' saved successfully!")
                    return redirect('items')
            except ValueError as e:
                logger.error(f"ValueError in price_form_partial: {e}")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'html': f'<div class="alert alert-danger">{str(e)}</div>'})
                messages.error(request, str(e))
            except IntegrityError:
                error_msg = "There was an error saving the price. It might already exist or there's a data conflict."
                logger.error(f"IntegrityError in price_form_partial: {error_msg}")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'html': f'<div class="alert alert-danger">{error_msg}</div>'})
                messages.error(request, error_msg)
        else:
            logger.error(f"DEBUG: PriceForm errors: {form.errors.as_json()}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                context = {
                    'form': form,
                    'item': item,
                    'list_id': list_id,
                    'title': f"{'Edit' if price_instance else 'Add'} Price for {item.name}",
                    'is_modal': True,
                }
                html = render_to_string('packing_lists/price_form_modal.html', context, request=request)
                return JsonResponse({'success': False, 'html': html})
    else:
        # GET: always provide all fields for the form
        initial = {}
        for field in ['store_name', 'store_city', 'store_state']:
            initial[field] = ''
        if price_instance:
            form = PriceForm(instance=price_instance, initial=initial)
        else:
            form = PriceForm(initial=initial)
    context = {
        'form': form,
        'item': item,
        'list_id': list_id,
        'title': f"{'Edit' if price_instance else 'Add'} Price for {item.name}",
        'is_modal': True,
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('packing_lists/price_form_modal.html', context, request=request)
        return JsonResponse({'html': html})
    return render(request, 'packing_lists/price_form_modal.html', context)

def add_store_modal(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = StoreForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            html = render_to_string('packing_lists/store_form_modal.html', {'form': form, 'title': 'Add Store'}, request=request)
            return JsonResponse({'success': False, 'html': html})
    else:
        form = StoreForm()
        html = render_to_string('packing_lists/store_form_modal.html', {'form': form, 'title': 'Add Store'}, request=request)
        return JsonResponse({'html': html})

def edit_item_modal(request, list_id, pli_id):
    """
    Modal-based view for editing PackingListItem.
    """
    packing_list = get_object_or_404(PackingList, id=list_id)
    pli = get_object_or_404(PackingListItem, id=pli_id, packing_list=packing_list)
    
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = PackingListItemForm(request.POST, instance=pli)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            print('DEBUG: PackingListItemForm errors:', form.errors.as_json())  # Log form errors
            context = {
                'form': form,
                'packing_list': packing_list,
                'pli': pli,
                'title': f"Edit {pli.item.name}",
                'is_modal': True,
            }
            html = render_to_string('packing_lists/packing_listitem_form_modal.html', context, request=request)
            return JsonResponse({'success': False, 'html': html})
    else:
        form = PackingListItemForm(instance=pli)
        context = {
            'form': form,
            'packing_list': packing_list,
            'pli': pli,
            'title': f"Edit {pli.item.name}",
            'is_modal': True,
        }
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('packing_lists/packing_listitem_form_modal.html', context, request=request)
            return JsonResponse({'html': html})
        return render(request, 'packing_lists/packing_listitem_form_modal.html', context)

def lists_page(request):
    """
    Lists all packing lists and provides a button to create a new list.
    """
    packing_lists = PackingList.objects.all().order_by('-id')
    return render(request, 'packing_lists/lists.html', {
        'packing_lists': packing_lists,
    })


def anonymous_price_info(request, price_id):
    """API endpoint to get anonymous price submission details"""
    try:
        price = Price.objects.get(id=price_id)
        
        if not price.is_anonymous:
            return JsonResponse({'error': 'Price is not anonymous'}, status=400)
        
        anonymity_info = price.get_anonymity_info()
        
        return JsonResponse({
            'success': True,
            'data': anonymity_info
        })
        
    except Price.DoesNotExist:
        return JsonResponse({'error': 'Price not found'}, status=404)

def items_page(request):
    """
    Comprehensive items page showing all items with prices, notes, and packing list associations.
    Users can checkmark items and create new packing lists from selected items.
    Now supports filtering by store, city, state, and military installation (Base, within 15 miles).
    """
    # Get filter parameters
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    has_prices = request.GET.get('has_prices', '')
    in_packing_list = request.GET.get('in_packing_list', '')
    store_filter = request.GET.get('store', '')
    city_filter = request.GET.get('city', '')
    state_filter = request.GET.get('state', '')
    base_filter = request.GET.get('base', '')
    
    # Get all items with related data
    items = Item.objects.prefetch_related(
        'prices__store',
        'packing_list_items__packing_list'
    ).all()
    
    # Apply filters
    if search_query:
        items = items.filter(name__icontains=search_query)
    
    if category_filter:
        items = items.filter(packing_list_items__section=category_filter).distinct()
    
    if has_prices == 'yes':
        items = items.filter(prices__isnull=False).distinct()
    elif has_prices == 'no':
        items = items.filter(prices__isnull=True)
    
    if in_packing_list:
        items = items.filter(packing_list_items__packing_list_id=in_packing_list).distinct()
    
    # Filtering by store/city/state/base
    store_q = Q()
    base_obj = None
    if base_filter:
        try:
            base_obj = Base.objects.get(id=base_filter)
        except Base.DoesNotExist:
            base_obj = None
    if base_obj and base_obj.latitude and base_obj.longitude:
        # Find stores within 15 miles of the base
        store_ids_near_base = []
        for store in Store.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True):
            from math import radians, sin, cos, sqrt, atan2
            lat1, lon1 = radians(base_obj.latitude), radians(base_obj.longitude)
            lat2, lon2 = radians(store.latitude), radians(store.longitude)
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            r = 3956
            distance = c * r
            if distance <= 15:
                store_ids_near_base.append(store.id)
        if store_ids_near_base:
            store_q &= Q(prices__store_id__in=store_ids_near_base)
    else:
        if store_filter:
            store_q &= Q(prices__store_id=store_filter)
        if city_filter:
            store_q &= Q(prices__store__city__iexact=city_filter)
        if state_filter:
            store_q &= Q(prices__store__state__iexact=state_filter)
    if store_q:
        items = items.filter(store_q).distinct()
    
    # Get unique categories for filter dropdown
    categories = PackingListItem.objects.values_list('section', flat=True).exclude(
        section__isnull=True
    ).exclude(section='').distinct().order_by('section')
    
    # Get packing lists for filter dropdown
    packing_lists = PackingList.objects.all().order_by('name')
    
    # Get all stores, cities, states, and bases for filter dropdowns
    stores = Store.objects.all().order_by('name')
    cities = Store.objects.exclude(city__isnull=True).exclude(city='').values_list('city', flat=True).distinct().order_by('city')
    states = Store.objects.exclude(state__isnull=True).exclude(state='').values_list('state', flat=True).distinct().order_by('state')
    bases = Base.objects.all().order_by('name')
    
    # Prepare items with comprehensive data
    items_with_data = []
    for item in items:
        # Get all prices for this item with vote data
        prices_with_votes = []
        for price in item.prices.all():
            # Only include prices from stores matching the filter
            if base_obj and base_obj.latitude and base_obj.longitude:
                if not (price.store.latitude and price.store.longitude):
                    continue
                from math import radians, sin, cos, sqrt, atan2
                lat1, lon1 = radians(base_obj.latitude), radians(base_obj.longitude)
                lat2, lon2 = radians(price.store.latitude), radians(price.store.longitude)
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * atan2(sqrt(a), sqrt(1-a))
                r = 3956
                distance = c * r
                if distance > 15:
                    continue
            if store_filter and str(price.store.id) != str(store_filter):
                continue
            if city_filter and (not price.store.city or price.store.city.lower() != city_filter.lower()):
                continue
            if state_filter and (not price.store.state or price.store.state.lower() != state_filter.lower()):
                continue
            upvotes = price.votes.filter(is_correct_price=True).count()
            downvotes = price.votes.filter(is_correct_price=False).count()
            total_votes = upvotes + downvotes
            vote_confidence = (upvotes - downvotes) / max(total_votes, 1)
            prices_with_votes.append({
                'price': price,
                'upvotes': upvotes,
                'downvotes': downvotes,
                'vote_confidence': vote_confidence,
                'price_per_unit': float(price.price) / max(price.quantity, 1),
                'store_city': price.store.city,
                'store_state': price.store.state,
                'store_name': price.store.name
            })
        # Sort prices by vote confidence and price
        prices_with_votes.sort(key=lambda x: (x['vote_confidence'], -x['price_per_unit']), reverse=True)
        # Get all packing lists this item appears in
        packing_list_appearances = []
        for pli in item.packing_list_items.all():
            packing_list_appearances.append({
                'packing_list': pli.packing_list,
                'quantity': pli.quantity,
                'notes': pli.notes,
                'required': pli.required,
                'section': pli.section,
                'nsn_lin': pli.nsn_lin,
                'instructions': pli.instructions
            })
        # Calculate price range
        price_range = None
        if prices_with_votes:
            min_price = min(p['price_per_unit'] for p in prices_with_votes)
            max_price = max(p['price_per_unit'] for p in prices_with_votes)
            price_range = f"${min_price:.2f} - ${max_price:.2f}"
        # Apply price filters
        if price_min and prices_with_votes:
            min_item_price = min(p['price_per_unit'] for p in prices_with_votes)
            if min_item_price < float(price_min):
                continue
        if price_max and prices_with_votes:
            min_item_price = min(p['price_per_unit'] for p in prices_with_votes)
            if min_item_price > float(price_max):
                continue
        items_with_data.append({
            'item': item,
            'prices_with_votes': prices_with_votes,
            'packing_list_appearances': packing_list_appearances,
            'price_range': price_range,
            'best_price': prices_with_votes[0] if prices_with_votes else None,
            'total_prices': len(prices_with_votes),
            'total_packing_lists': len(packing_list_appearances)
        })
    # Sort items by name
    items_with_data.sort(key=lambda x: x['item'].name.lower())
    context = {
        'items_with_data': items_with_data,
        'categories': categories,
        'packing_lists': packing_lists,
        'stores': stores,
        'cities': cities,
        'states': states,
        'bases': bases,
        'filters': {
            'search': search_query,
            'category': category_filter,
            'price_min': price_min,
            'price_max': price_max,
            'has_prices': has_prices,
            'in_packing_list': in_packing_list,
            'store': store_filter,
            'city': city_filter,
            'state': state_filter,
            'base': base_filter,
        },
        'title': 'All Items'
    }
    return render(request, 'packing_lists/items.html', context)

def create_packing_list_from_items(request):
    """
    Create a new packing list from selected items on the items page.
    """
    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items')
        list_name = request.POST.get('list_name', '').strip()
        list_description = request.POST.get('list_description', '').strip()
        school_id = request.POST.get('school')
        base_id = request.POST.get('base')
        event_type = request.POST.get('event_type', 'school')
        
        if not selected_items:
            messages.error(request, "Please select at least one item.")
            return redirect('items_page')
        
        if not list_name:
            messages.error(request, "Please provide a name for the packing list.")
            return redirect('items_page')
        
        # Create the packing list
        packing_list = PackingList.objects.create(
            name=list_name,
            description=list_description,
            school_id=school_id if school_id else None,
            base_id=base_id if base_id else None,
            event_type=event_type
        )
        
        # Add selected items to the packing list
        items_added = 0
        for item_id in selected_items:
            try:
                item = Item.objects.get(id=item_id)
                # Get the most common quantity and notes from existing packing lists
                existing_pli = item.packing_list_items.first()
                if existing_pli:
                    PackingListItem.objects.create(
                        packing_list=packing_list,
                        item=item,
                        quantity=existing_pli.quantity,
                        notes=existing_pli.notes,
                        required=existing_pli.required,
                        section=existing_pli.section,
                        nsn_lin=existing_pli.nsn_lin,
                        instructions=existing_pli.instructions
                    )
                else:
                    PackingListItem.objects.create(
                        packing_list=packing_list,
                        item=item,
                        quantity=1,
                        required=True
                    )
                items_added += 1
            except Item.DoesNotExist:
                continue
        
        messages.success(request, f"Packing list '{packing_list.name}' created with {items_added} items!")
        return redirect(reverse('view_packing_list', args=[packing_list.id]))
    
    # GET request - show form
    selected_items = request.GET.getlist('selected_items')
    if not selected_items:
        messages.error(request, "No items selected.")
        return redirect('items_page')
    
    # Get the selected items
    items = Item.objects.filter(id__in=selected_items).order_by('name')
    
    # Get available schools and bases for the form
    schools = School.objects.all().order_by('name')
    bases = Base.objects.all().order_by('name')
    
    context = {
        'selected_items': items,
        'schools': schools,
        'bases': bases,
        'title': 'Create Packing List from Selected Items'
    }
    return render(request, 'packing_lists/create_packing_list_from_items.html', context)

def edit_packing_list(request, list_id):
    """
    View for editing an existing PackingList.
    """
    packing_list = get_object_or_404(PackingList, id=list_id)
    if request.method == 'POST':
        form = PackingListForm(request.POST, request.FILES, instance=packing_list)
        if form.is_valid():
            form.save()
            messages.success(request, f"Packing list '{packing_list.name}' updated successfully!")
            return redirect(reverse('view_packing_list', args=[packing_list.id]))
    else:
        form = PackingListForm(instance=packing_list)
    context = {
        'form': form,
        'title': f'Edit Packing List: {packing_list.name}',
        'packing_list': packing_list,
    }
    return render(request, 'packing_lists/packing_list_form.html', context)

def merge_packing_lists(request):
    """
    Merge two packing lists into one, deduping items and keeping highest quantity/required.
    """
    if request.method == 'POST':
        list1_id = request.POST.get('list1_id')
        list2_id = request.POST.get('list2_id')
        new_list_name = request.POST.get('new_list_name', '').strip()
        
        if not list1_id or not list2_id:
            messages.error(request, "Please select two lists to merge.")
            return redirect('lists')
        
        if list1_id == list2_id:
            messages.error(request, "Cannot merge a list with itself.")
            return redirect('lists')
        
        if not new_list_name:
            messages.error(request, "Please provide a name for the merged list.")
            return redirect('lists')
        
        try:
            list1 = PackingList.objects.get(id=list1_id)
            list2 = PackingList.objects.get(id=list2_id)
        except PackingList.DoesNotExist:
            messages.error(request, "One or both lists not found.")
            return redirect('lists')
        
        # Create the merged list
        merged_list = PackingList.objects.create(
            name=new_list_name,
            description=f"Merged from '{list1.name}' and '{list2.name}'",
            school=list1.school or list2.school,
            base=list1.base or list2.base,
            event_type=list1.event_type or list2.event_type
        )
        
        # Track items by their ID to handle duplicates
        merged_items = {}
        
        # Process items from both lists
        for pli in list1.items.all():
            item_id = pli.item.id
            if item_id not in merged_items:
                merged_items[item_id] = pli
            else:
                # Merge with existing item - keep highest quantity and required=True if either is True
                existing = merged_items[item_id]
                merged_items[item_id] = PackingListItem(
                    packing_list=merged_list,
                    item=pli.item,
                    quantity=max(existing.quantity, pli.quantity),
                    required=existing.required or pli.required,
                    notes=existing.notes if existing.notes else pli.notes,
                    section=existing.section if existing.section else pli.section,
                    nsn_lin=existing.nsn_lin if existing.nsn_lin else pli.nsn_lin,
                    instructions=existing.instructions if existing.instructions else pli.instructions
                )
        
        for pli in list2.items.all():
            item_id = pli.item.id
            if item_id not in merged_items:
                merged_items[item_id] = pli
            else:
                # Merge with existing item
                existing = merged_items[item_id]
                merged_items[item_id] = PackingListItem(
                    packing_list=merged_list,
                    item=pli.item,
                    quantity=max(existing.quantity, pli.quantity),
                    required=existing.required or pli.required,
                    notes=existing.notes if existing.notes else pli.notes,
                    section=existing.section if existing.section else pli.section,
                    nsn_lin=existing.nsn_lin if existing.nsn_lin else pli.nsn_lin,
                    instructions=existing.instructions if existing.instructions else pli.instructions
                )
        
        # Save all merged items
        for pli in merged_items.values():
            pli.packing_list = merged_list
            pli.save()
        
        messages.success(request, f"Successfully merged '{list1.name}' and '{list2.name}' into '{merged_list.name}' with {len(merged_items)} items.")
        return redirect(reverse('view_packing_list', args=[merged_list.id]))
    
    # GET request - show merge form
    packing_lists = PackingList.objects.all().order_by('name')
    return render(request, 'packing_lists/merge_lists.html', {
        'packing_lists': packing_lists,
        'title': 'Merge Packing Lists'
    })

def delete_packing_lists(request):
    """
    Delete one or more packing lists.
    """
    if request.method == 'POST':
        list_ids = request.POST.getlist('list_ids')
        
        if not list_ids:
            messages.error(request, "Please select at least one list to delete.")
            return redirect('lists')
        
        deleted_count = 0
        deleted_names = []
        
        for list_id in list_ids:
            try:
                packing_list = PackingList.objects.get(id=list_id)
                deleted_names.append(packing_list.name)
                packing_list.delete()
                deleted_count += 1
            except PackingList.DoesNotExist:
                continue
        
        if deleted_count == 1:
            messages.success(request, f"Successfully deleted '{deleted_names[0]}'.")
        elif deleted_count > 1:
            messages.success(request, f"Successfully deleted {deleted_count} lists: {', '.join(deleted_names)}.")
        else:
            messages.error(request, "No lists were deleted.")
        
        return redirect('lists')
    
    # GET request - show delete confirmation
    list_ids = request.GET.getlist('list_ids')
    if not list_ids:
        messages.error(request, "No lists selected for deletion.")
        return redirect('lists')
    
    packing_lists = PackingList.objects.filter(id__in=list_ids).order_by('name')
    if len(packing_lists) != len(list_ids):
        messages.warning(request, "Some selected lists were not found.")
    
    return render(request, 'packing_lists/delete_lists.html', {
        'packing_lists': packing_lists,
        'title': 'Delete Packing Lists'
    })

def clone_packing_list(request, list_id):
    """
    Clone a packing list and all its items.
    """
    try:
        original_list = PackingList.objects.get(id=list_id)
    except PackingList.DoesNotExist:
        messages.error(request, "Packing list not found.")
        return redirect('lists')
    
    if request.method == 'POST':
        new_name = request.POST.get('new_name', '').strip()
        
        if not new_name:
            messages.error(request, "Please provide a name for the cloned list.")
            return redirect('lists')
        
        # Create the cloned list
        cloned_list = PackingList.objects.create(
            name=new_name,
            description=f"Cloned from '{original_list.name}'",
            school=original_list.school,
            base=original_list.base,
            event_type=original_list.event_type
        )
        
        # Clone all items from the original list
        cloned_items_count = 0
        for original_pli in original_list.items.all():
            PackingListItem.objects.create(
                packing_list=cloned_list,
                item=original_pli.item,
                quantity=original_pli.quantity,
                required=original_pli.required,
                notes=original_pli.notes,
                section=original_pli.section,
                nsn_lin=original_pli.nsn_lin,
                instructions=original_pli.instructions
            )
            cloned_items_count += 1
        
        messages.success(request, f"Successfully cloned '{original_list.name}' as '{cloned_list.name}' with {cloned_items_count} items.")
        return redirect(reverse('view_packing_list', args=[cloned_list.id]))
    
    # GET request - show clone form
    return render(request, 'packing_lists/clone_list.html', {
        'original_list': original_list,
        'title': f'Clone Packing List: {original_list.name}'
    })

def export_packing_list_pdf(request, list_id):
    """
    Export a packing list as a PDF.
    """
    try:
        packing_list = PackingList.objects.get(id=list_id)
    except PackingList.DoesNotExist:
        messages.error(request, "Packing list not found.")
        return redirect('lists')
    
    # Create the PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{packing_list.name.replace(" ", "_")}_packing_list.pdf"'
    
    # Create the PDF document
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20
    )
    normal_style = styles['Normal']
    
    # Add title with military branding
    story.append(Paragraph("🎖️ MILITARY PACKING LIST", ParagraphStyle('MilitaryHeader', parent=title_style, fontSize=16, textColor=colors.darkblue, spaceAfter=5)))
    story.append(Paragraph(f"{packing_list.name}", title_style))
    story.append(Spacer(1, 20))
    
    # Add list details
    details_data = []
    if packing_list.description:
        details_data.append(['Description:', packing_list.description])
    if packing_list.school:
        details_data.append(['School:', packing_list.school.name])
    if packing_list.base:
        details_data.append(['Base:', packing_list.base.name])
    if packing_list.event_type:
        details_data.append(['Event Type:', packing_list.event_type])
    if packing_list.last_updated:
        details_data.append(['Last Updated:', packing_list.last_updated])
    
    if details_data:
        details_table = Table(details_data, colWidths=[1.5*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 20))
    
    # Get items with prices
    list_items = packing_list.items.select_related('item').prefetch_related('item__prices__store').order_by('item__name')
    
    if list_items:
        story.append(Paragraph("Items Checklist", heading_style))
        story.append(Paragraph("✓ = Packed | ☐ = Not Packed | ✎ = Manual Check", ParagraphStyle('Legend', parent=normal_style, fontSize=8, textColor=colors.grey, spaceAfter=10)))
        
        # Create items table with packed status
        items_data = [
            [Paragraph('<b>Packed</b>', normal_style), Paragraph('<b>Item</b>', normal_style), Paragraph('<b>Qty</b>', normal_style), Paragraph('<b>Required</b>', normal_style), Paragraph('<b>Notes</b>', normal_style), Paragraph('<b>Best Price</b>', normal_style), Paragraph('<b>Store</b>', normal_style)]
        ]

        for pli in list_items:
            # Determine checkbox status based on packed status
            if pli.packed:
                checkbox = '✓'  # Checked box for packed items
            else:
                checkbox = '☐'  # Empty box for unpacked items
            
            best_price = None
            if pli.item.prices.exists():
                prices = pli.item.prices.all()
                best_price = min(prices, key=lambda p: p.price)
            
            # Use Paragraph for all cells to enable wrapping
            packed_cell = Paragraph(f'<font size="14">{checkbox}</font>', normal_style)
            item_name = Paragraph(pli.item.name, normal_style)
            qty = Paragraph(str(pli.quantity), normal_style)
            required = Paragraph("Yes" if pli.required else "No", normal_style)
            notes = Paragraph((pli.notes or ""), normal_style)
            price_info = Paragraph(f"${best_price.price:.2f}" if best_price else "", normal_style)
            store_info = Paragraph(best_price.store.name if best_price and best_price.store else "", normal_style)
            items_data.append([packed_cell, item_name, qty, required, notes, price_info, store_info])
        
        # Add extra rows for manual checking
        story.append(Spacer(1, 10))
        manual_check_style = ParagraphStyle('ManualCheck', parent=normal_style, fontSize=9, textColor=colors.grey)
        story.append(Paragraph("Additional Items (Manual Entry):", manual_check_style))
        
        # Add 5 blank rows for manual additions
        for i in range(5):
            blank_checkbox = '☐'
            items_data.append([
                Paragraph(f'<font size="14">{blank_checkbox}</font>', normal_style),
                Paragraph('_' * 30, normal_style),  # Blank line for item name
                Paragraph('___', normal_style),     # Blank for quantity
                Paragraph('___', normal_style),     # Blank for required
                Paragraph('_' * 20, normal_style),  # Blank for notes
                Paragraph('_____', normal_style),   # Blank for price
                Paragraph('_' * 15, normal_style)   # Blank for store
            ])
        
        # Create table with proper styling - adjusted column widths for packed status
        items_table = Table(items_data, colWidths=[0.6*inch, 2.2*inch, 0.5*inch, 0.7*inch, 1.2*inch, 0.8*inch, 1.0*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Center align packed column
            ('ALIGN', (1, 0), (-1, -1), 'LEFT'),   # Left align other columns
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Highlight packed items with light green background
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 20))
        
        # Add summary with packing progress
        total_items = len(list_items)
        required_items = sum(1 for pli in list_items if pli.required)
        packed_items = sum(1 for pli in list_items if pli.packed)
        packed_required = sum(1 for pli in list_items if pli.packed and pli.required)
        items_with_prices = sum(1 for pli in list_items if pli.item.prices.exists())
        
        # Calculate completion percentage
        completion_percentage = round((packed_items / total_items) * 100) if total_items > 0 else 0
        required_completion = round((packed_required / required_items) * 100) if required_items > 0 else 0
        
        summary_data = [
            ['Total Items:', str(total_items)],
            ['Required Items:', str(required_items)],
            ['Items with Prices:', str(items_with_prices)],
            ['', ''],  # Spacer row
            ['Packed Items:', f'{packed_items} ({completion_percentage}%)'],
            ['Required Packed:', f'{packed_required} ({required_completion}%)'],
            ['Remaining to Pack:', str(total_items - packed_items)],
        ]
        
        summary_table = Table(summary_data, colWidths=[1.5*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(Paragraph("Packing Summary", heading_style))
        story.append(summary_table)
        story.append(Spacer(1, 30))
    else:
        story.append(Paragraph("No items in this packing list.", normal_style))
        story.append(Spacer(1, 30))
    
    # Add instructions and footer
    instructions_style = ParagraphStyle('Instructions', parent=normal_style, fontSize=9, textColor=colors.grey)
    story.append(Paragraph("<b>Instructions:</b>", instructions_style))
    story.append(Paragraph("• Check (✓) items as you pack them", instructions_style))
    story.append(Paragraph("• Use the manual entry rows for additional items", instructions_style))
    story.append(Paragraph("• Verify all required items are packed before departure", instructions_style))
    story.append(Spacer(1, 20))
    
    # Add footer
    footer_style = ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey, alignment=1)
    from datetime import datetime
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')} | Community Packing List System", footer_style))
    
    # Build the PDF
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    
    response.write(pdf)
    return response

def create_item(request):
    """
    View for creating a new standalone item.
    """
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, f"Item '{item.name}' created successfully!")
            return redirect('items')  # Redirect to items page
    else:
        form = ItemForm()

    context = {
        'form': form,
        'title': 'Create New Item'
    }
    return render(request, 'packing_lists/item_form.html', context)

def add_item_modal(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            return JsonResponse({'success': True, 'item_id': item.id})
        else:
            print('DEBUG: ItemForm errors:', form.errors.as_json())  # Log form errors
            context = {
                'form': form,
                'title': 'Add Item',
                'is_modal': True,
            }
            html = render_to_string('packing_lists/item_form_modal.html', context, request=request)
            return JsonResponse({'success': False, 'html': html})
    else:
        form = ItemForm()
        context = {
            'form': form, 
            'title': 'Add Item', 
            'is_modal': True
        }
        html = render_to_string('packing_lists/item_form_modal.html', context, request=request)
        return JsonResponse({'html': html})

def health_check(request):
    """Health check endpoint for Cloud Run"""
    from django.http import JsonResponse
    return JsonResponse({'status': 'healthy', 'service': 'community-packing-list'})

def run_migrations(request):
    """Run database migrations via web endpoint - for debugging only"""
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        from django.core.management import call_command
        from io import StringIO
        import sys
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = output = StringIO()
        
        # Run migrations
        call_command('migrate', verbosity=2)
        
        # Restore stdout
        sys.stdout = old_stdout
        
        return JsonResponse({
            'status': 'success',
            'output': output.getvalue()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)

def test_database_write(request):
    """Test database write functionality - for debugging only"""
    from django.http import JsonResponse
    from django.utils import timezone
    
    try:
        # Try to create a simple test record
        from .models import PackingList
        
        test_list = PackingList.objects.create(
            name=f"Test List {timezone.now().strftime('%Y%m%d-%H%M%S')}",
            description="Test database write functionality"
        )
        
        # Try to update it
        test_list.description = "Updated test description"
        test_list.save()
        
        # Clean up
        test_list.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Database write operations working correctly',
            'test_id': test_list.id if test_list else 'deleted'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)

def public_list_view(request, share_slug):
    """Public view of a packing list for sharing"""
    try:
        packing_list = PackingList.objects.get(share_slug=share_slug, is_public=True)
        packing_list.increment_view_count()  # Track views for analytics
    except PackingList.DoesNotExist:
        return render(request, 'packing_lists/list_not_found.html', status=404)
    
    # Get completion stats for display
    completion_stats = packing_list.get_completion_stats()
    
    # Get items with prices for public view
    list_items = packing_list.items.select_related('item').order_by('section', 'item__name')
    items_with_prices = []
    
    for pli in list_items:
        # Get prices for this item, ordered by best value
        prices = pli.item.prices.select_related('store').order_by('price')
        prices_with_votes = []
        
        for price in prices:
            # Get vote counts
            upvotes = price.votes.filter(is_correct_price=True).count()
            downvotes = price.votes.filter(is_correct_price=False).count()
            price_per_unit = price.price / price.quantity if price.quantity > 0 else price.price
            
            prices_with_votes.append({
                'price': price,
                'upvotes': upvotes,
                'downvotes': downvotes,
                'price_per_unit': price_per_unit,
            })
        
        items_with_prices.append({
            'pli': pli,
            'item': pli.item,
            'prices_with_votes': prices_with_votes,
        })
    
    context = {
        'packing_list': packing_list,
        'items_with_prices': items_with_prices,
        'completion_stats': completion_stats,
        'is_public_view': True,
    }
    
    return render(request, 'packing_lists/public_list.html', context)

def embed_list_view(request, share_slug):
    """Embeddable widget view of a packing list"""
    try:
        packing_list = PackingList.objects.get(share_slug=share_slug, is_public=True)
        packing_list.increment_view_count()
    except PackingList.DoesNotExist:
        return render(request, 'packing_lists/embed_not_found.html', status=404)
    
    # Get completion stats for display
    completion_stats = packing_list.get_completion_stats()
    
    # Get items with prices for embedding (limited set)
    list_items = packing_list.items.select_related('item').order_by('item__name')[:20]
    items_with_prices = []
    
    for pli in list_items:
        # Get best price for this item
        best_price = pli.item.prices.select_related('store').order_by('price').first()
        prices_with_votes = []
        
        if best_price:
            # Get vote counts for best price
            upvotes = best_price.votes.filter(is_correct_price=True).count()
            downvotes = best_price.votes.filter(is_correct_price=False).count()
            price_per_unit = best_price.price / best_price.quantity if best_price.quantity > 0 else best_price.price
            
            prices_with_votes.append({
                'price': best_price,
                'upvotes': upvotes,
                'downvotes': downvotes,
                'price_per_unit': price_per_unit,
            })
        
        items_with_prices.append({
            'pli': pli,
            'item': pli.item,
            'prices_with_votes': prices_with_votes,
        })
    
    context = {
        'packing_list': packing_list,
        'items_with_prices': items_with_prices,
        'completion_stats': completion_stats,
    }
    
    # Return minimal HTML for embedding
    response = render(request, 'packing_lists/embed_list.html', context)
    response['X-Frame-Options'] = 'ALLOWALL'  # Allow embedding in iframes
    return response

def discover_lists(request):
    """Community discovery page showing popular and recent lists"""
    from django.db.models import Count, Sum
    
    # Get filter parameters
    search_query = request.GET.get('search', '').strip()
    event_type = request.GET.get('event_type', '')
    sort_by = request.GET.get('sort', 'views')
    
    # Base queryset for public lists
    packing_lists = PackingList.objects.filter(is_public=True).select_related('school')
    
    # Apply search filter
    if search_query:
        packing_lists = packing_lists.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(school__name__icontains=search_query)
        )
    
    # Apply event type filter
    if event_type:
        packing_lists = packing_lists.filter(event_type=event_type)
    
    # Apply sorting
    if sort_by == 'views':
        packing_lists = packing_lists.order_by('-view_count', '-created_at')
    elif sort_by == 'recent':
        packing_lists = packing_lists.order_by('-updated_at', '-created_at')
    elif sort_by == 'name':
        packing_lists = packing_lists.order_by('name')
    elif sort_by == 'items':
        packing_lists = packing_lists.annotate(item_count=Count('items')).order_by('-item_count')
    
    # Limit results for performance
    packing_lists = packing_lists[:50]
    
    # Get stats for header
    all_public_lists = PackingList.objects.filter(is_public=True)
    total_lists = all_public_lists.count()
    total_items = all_public_lists.aggregate(
        total=Count('items', distinct=True)
    )['total'] or 0
    total_views = all_public_lists.aggregate(
        total=Sum('view_count')
    )['total'] or 0
    
    context = {
        'packing_lists': packing_lists,
        'search_query': search_query,
        'event_type': event_type,
        'sort_by': sort_by,
        'total_lists': total_lists,
        'total_items': total_items,
        'total_views': total_views,
    }
    
    return render(request, 'packing_lists/discover.html', context)
