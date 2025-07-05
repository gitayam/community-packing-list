from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages # For feedback to the user
from django.db import IntegrityError
from .models import PackingList, Item, PackingListItem, School, Price, Vote, Store
from .forms import PackingListForm, UploadFileForm, PriceForm, VoteForm, ConfigureUploadListForm, PackingListItemForm
from .parsers import parse_csv, parse_excel, parse_pdf, parse_text
import io
import uuid # For unique session keys
from django.http import Http404, JsonResponse

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


def upload_packing_list(request):
    """
    View for uploading a packing list file (CSV, Excel, PDF) or pasting text.
    Step 1: Parses the file/text.
    Step 2: Stores parsed items in session and redirects to configuration step.
    """
    error_message = None
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data.get('file')
            text_content = form.cleaned_data.get('text_content')
            parsed_items = []
            original_filename = None

            if file:
                original_filename = file.name
                filename_lower = original_filename.lower()
                try:
                    if filename_lower.endswith('.csv'):
                        file_content_string = file.read().decode('utf-8')
                        parsed_items, error_message = parse_csv(file_content_string)
                    elif filename_lower.endswith(('.xls', '.xlsx')):
                        parsed_items, error_message = parse_excel(file)
                    elif filename_lower.endswith('.pdf'):
                        parsed_items, error_message = parse_pdf(file)
                except Exception as e:
                    error_message = f"Error processing file: {str(e)}"
            elif text_content:
                original_filename = "Pasted Text"
                try:
                    parsed_items, error_message = parse_text(text_content)
                except Exception as e:
                    error_message = f"Error processing text: {str(e)}"

            if error_message:
                messages.error(request, error_message)
            elif not parsed_items:
                messages.warning(request, "No items were found in the provided data.")
            else:
                session_key_items = f"parsed_items_{uuid.uuid4().hex}"
                request.session[session_key_items] = parsed_items
                request.session['original_filename'] = original_filename
                messages.info(request, f"Successfully parsed {len(parsed_items)} items. Please configure the new list.")
                return redirect(reverse('configure_uploaded_list', args=[session_key_items]))
        else:
            # Handle form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f"{field}: {error}")
    else:
        form = UploadFileForm()

    context = {
        'form': form,
        'title': 'Upload Packing List',
        'error_message': error_message
    }
    return render(request, 'packing_lists/upload_form.html', context)


def packing_list_detail(request, list_id):
    """
    Displays a single packing list, its items, and allows checking off items.
    Also shows current pricing information (voting/adding prices will be separate).
    """
    packing_list = get_object_or_404(PackingList, id=list_id)
    # Get all items for this list, ordered perhaps by 'id' or 'item__name'
    # .select_related('item') helps optimize by fetching related Item objects in the same query
    list_items = packing_list.items.select_related('item').order_by('item__name')

    # For each item, we might want to fetch its prices.
    # This can be done efficiently or less so. For now, let's prepare data for the template.
    # A more complex query or template tags might be needed for optimal price display.

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
        prices = pli.item.prices.select_related('store').all()
        
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
            # - Balance: 70% price, 30% vote confidence
            # - Use a base price for normalization (median price or $50 default)
            base_price = 50.0  # Default normalization price
            price_score = 1.0 - (price_per_unit / base_price)  # Lower price = higher score
            vote_score = (vote_confidence + 1) / 2  # Convert from [-1,1] to [0,1]
            
            smart_score = (0.7 * price_score) + (0.3 * vote_score)
            
            prices_with_votes.append({
                'price': price,
                'upvotes': upvotes,
                'downvotes': downvotes,
                'vote_confidence': vote_confidence,
                'price_per_unit': price_per_unit,
                'smart_score': smart_score
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
    }
    return render(request, 'packing_lists/packing_list_detail.html', context)

# @login_required (if user accounts are implemented)
def add_price_for_item(request, item_id, list_id=None): # list_id is for redirecting back
    item = get_object_or_404(Item, id=item_id)

    # Handle store creation first
    if request.method == 'POST' and 'new_store_name' in request.POST:
        store_name = request.POST.get('new_store_name', '').strip()
        store_address = request.POST.get('new_store_address', '').strip()
        
        if store_name:
            store, created = Store.objects.get_or_create(name=store_name, defaults={'address_line1': store_address})
            if created:
                messages.success(request, f"Store '{store.name}' created successfully.")
            # Redirect back to the same page to show the new store in the dropdown
            return redirect(request.path)

    if request.method == 'POST':
        form = PriceForm(request.POST)
        if form.is_valid():
            try:
                price = form.save(commit=False, item_instance=item)
                # If user accounts: price.user = request.user
                price.save()
                messages.success(request, f"Price for '{item.name}' at '{price.store.name}' added successfully.")
                if list_id:
                    return redirect(reverse('view_packing_list', args=[list_id]))
                else:
                    # Fallback if no list_id, maybe to an item detail page or home
                    return redirect(reverse('home'))
            except ValueError as e: # Catch missing item instance from form.save
                messages.error(request, str(e))
            except IntegrityError: # Catch other DB issues, e.g. if a unique constraint fails
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
        # Determine if it's an upvote or downvote based on the button name/value
        vote_type = None
        price_id = None
        
        if 'upvote_price_id' in request.POST:
            vote_type = 'up'
            price_id = request.POST.get('upvote_price_id')
        elif 'downvote_price_id' in request.POST:
            vote_type = 'down'
            price_id = request.POST.get('downvote_price_id')
        else:
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
                messages.error(request, "Price not found.")
                return redirect(request.META.get('HTTP_REFERER', reverse('home')))

            ip_address = request.META.get('REMOTE_ADDR')
            Vote.objects.create(
                price=price_instance,
                is_correct_price=is_correct,
                ip_address=ip_address
            )
            if is_correct:
                messages.success(request, f"Upvoted price for '{price_instance.item.name}' (from IP: {ip_address}).")
            else:
                messages.success(request, f"Downvoted price for '{price_instance.item.name}'.")
        else:
            messages.error(request, "Invalid vote data.")
        redirect_url = request.META.get('HTTP_REFERER', reverse('home'))
        return redirect(redirect_url)
    return redirect(reverse('home'))


def configure_uploaded_list(request, session_key_items):
    """
    Step 2 of upload process: Configure the PackingList (name, school)
    and then create the PackingList and its PackingListItems from session data.
    """
    parsed_items = request.session.get(session_key_items)
    original_filename = request.session.get('original_filename', 'Uploaded List')

    if not parsed_items:
        messages.error(request, "No items found to configure. Session may have expired or data was not passed correctly.")
        return redirect(reverse('upload_packing_list'))

    if request.method == 'POST':
        form = ConfigureUploadListForm(request.POST)
        if form.is_valid():
            list_name = form.cleaned_data['list_name']
            description = form.cleaned_data['description']
            school_instance = form.get_school_instance() # Gets or creates school

            # Create the PackingList
            try:
                packing_list = PackingList.objects.create(
                    name=list_name,
                    description=description,
                    school=school_instance
                    # user=request.user if request.user.is_authenticated else None # If user accounts
                )
            except IntegrityError: # Should be caught by form's unique name validation
                form.add_error('list_name', "A packing list with this name already exists. Please choose a different name.")
                # Fall through to re-render form with this error
            else:
                # Create Items and PackingListItems
                created_count = 0
                for item_data in parsed_items:
                    item_name_str = item_data.get('item_name')
                    quantity = item_data.get('quantity', 1)
                    notes = item_data.get('notes', '')

                    if not item_name_str:
                        continue

                    item, _ = Item.objects.get_or_create(
                        name=item_name_str.strip(),
                        defaults={'description': ''}
                    )

                    _, pli_created = PackingListItem.objects.get_or_create(
                        packing_list=packing_list,
                        item=item,
                        defaults={'quantity': quantity, 'notes': notes}
                    )
                    if pli_created:
                        created_count += 1

                # Clear session data for this upload
                del request.session[session_key_items]
                if 'original_filename' in request.session:
                    del request.session['original_filename']

                messages.success(request, f"Successfully created packing list '{packing_list.name}' with {created_count} item(s).")
                return redirect(reverse('view_packing_list', args=[packing_list.id]))
    else:
        # Pre-fill the form if possible
        initial_data = {'list_name': f"{original_filename} Packing List"}
        # Check if initial_data['list_name'] already exists, append number if so
        counter = 1
        base_name = initial_data['list_name']
        while PackingList.objects.filter(name=initial_data['list_name']).exists():
            initial_data['list_name'] = f"{base_name} ({counter})"
            counter +=1
            if counter > 100: # Safety break
                initial_data['list_name'] = f"{base_name} ({uuid.uuid4().hex[:6]})"
                break
        form = ConfigureUploadListForm(initial=initial_data)

    context = {
        'form': form,
        'title': 'Configure New Packing List',
        'num_items': len(parsed_items)
    }
    return render(request, 'packing_lists/configure_upload_form.html', context)


from django.db.models import Q
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in kilometers. Use 3959 for miles.

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

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
