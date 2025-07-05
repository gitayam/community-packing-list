from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages # For feedback to the user
from django.db import IntegrityError
from .models import PackingList, Item, PackingListItem, School, Price, Vote, Store, Base
from .forms import PackingListForm, PriceForm, VoteForm, PackingListItemForm, StoreForm

# Requires login for actions that modify data if user accounts are active
# from django.contrib.auth.decorators import login_required


def home(request):
    """
    Home page view.
    Displays existing packing lists and links to create/upload new ones.
    """
    packing_lists = PackingList.objects.all().order_by('-id') # Show newest first, or by name, etc.
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
    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST':
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
            # Gather all store fields
            store_data = {
                'name': store_name,
                'address_line1': post_data.get('store_address_line1', '').strip(),
                'address_line2': post_data.get('store_address_line2', '').strip(),
                'city': post_data.get('store_city', '').strip(),
                'state': post_data.get('store_state', '').strip(),
                'zip_code': post_data.get('store_zip_code', '').strip(),
                'country': post_data.get('store_country', '').strip() or 'USA',
                'url': post_data.get('store_url', '').strip(),
                'is_online': bool(post_data.get('store_is_online')),
                'is_in_person': bool(post_data.get('store_is_in_person', '1')),
            }
            store, _ = Store.objects.get_or_create(name=store_name, defaults=store_data)
            # If store already exists, update its fields with new data
            if not _:
                for k, v in store_data.items():
                    setattr(store, k, v)
                store.save()
            post_data['store'] = store.id
        form = PriceForm(post_data)
        if form.is_valid():
            try:
                price = form.save(commit=False, item_instance=item)
                price.save()
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
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = PriceForm(request.POST)
        if form.is_valid():
            price = form.save(commit=False)
            price.item = item
            price.save()
            return JsonResponse({'success': True})
        else:
            print('DEBUG: PriceForm errors:', form.errors.as_json())  # Log form errors
            context = {
                'form': form,
                'item': item,
                'list_id': list_id,
                'title': f"Add Price for {item.name}",
                'is_modal': True,
            }
            html = render_to_string('packing_lists/price_form_modal.html', context, request=request)
            return JsonResponse({'success': False, 'html': html})
    else:
        form = PriceForm()
        context = {
            'form': form,
            'item': item,
            'list_id': list_id,
            'title': f"Add Price for {item.name}",
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
            html = render_to_string('packing_lists/store_form.html', {'form': form, 'title': 'Add Store', 'is_modal': True}, request=request)
            return JsonResponse({'success': False, 'html': html})
    else:
        form = StoreForm()
        html = render_to_string('packing_lists/store_form.html', {'form': form, 'title': 'Add Store', 'is_modal': True}, request=request)
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

def items_page(request):
    """
    Placeholder for items page.
    """
    return render(request, 'packing_lists/items.html')

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
