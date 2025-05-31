from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, JsonResponse
from .models import Item, Price, UserProfile
from .forms import PriceForm

def item_list_view(request):
    items = Item.objects.all().order_by('name')
    context = {
        'items': items
    }
    return render(request, 'packer/item_list.html', context)

def item_detail_view(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    prices = item.prices.all().order_by('price', '-submitted_at')
    context = {
        'item': item,
        'prices': prices
    }
    return render(request, 'packer/item_detail.html', context)

def add_price_view(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        form = PriceForm(request.POST)
        if form.is_valid():
            price_instance = form.save(commit=False)
            price_instance.item = item

            submitted_name = form.cleaned_data.get('submitted_by_name')
            if submitted_name: # Ensure it's not empty or None
                UserProfile.objects.get_or_create(name=submitted_name, defaults={'reputation_score': 0})
            else: # Handle case where submitted_by_name might be optional or can be truly anonymous
                price_instance.submitted_by_name = "Anonymous" # Default if field left blank and model allows

            price_instance.save()
            return redirect('packer:item_detail', item_id=item.id)
    else:
        form = PriceForm()
    context = {
        'form': form,
        'item': item
    }
    return render(request, 'packer/add_price_form.html', context)

def vote_view(request, price_id, vote_type):
    if request.method != 'POST':
        return HttpResponseForbidden()

    price = get_object_or_404(Price, id=price_id)
    user_profile = None

    if price.submitted_by_name != "Anonymous":
        try:
            user_profile = UserProfile.objects.get(name=price.submitted_by_name)
        except UserProfile.DoesNotExist:
            # Or create one: user_profile = UserProfile.objects.create(name=price.submitted_by_name, reputation_score=0)
            # For now, if profile doesn't exist, we just skip reputation update.
            pass

    if vote_type == 'upvote':
        price.upvotes += 1
        if user_profile:
            user_profile.reputation_score += 1
    elif vote_type == 'downvote':
        price.downvotes += 1
        if user_profile:
            user_profile.reputation_score -= 1
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid vote type'}, status=400)

    price.save()
    if user_profile:
        user_profile.save()

    return JsonResponse({
        'status': 'success',
        'upvotes': price.upvotes,
        'downvotes': price.downvotes,
        'reputation_score': user_profile.reputation_score if user_profile else None
    })

def about_view(request):
    return render(request, 'packer/about.html')
