from django.urls import path
from . import views

# We will define view_packing_list in a subsequent step.
# For now, to avoid NoReverseMatch if a list is created/uploaded,
# we can temporarily point its URL name to home, or a placeholder.
# path('list/<int:pk>/', views.packing_list_detail, name='view_packing_list'), # Correct target
# Temporary placeholder for view_packing_list until it's implemented:
# from django.http import HttpResponseTemporary
# def temp_packing_list_detail_view(request, list_id):
#    return HttpResponseTemporary(f"Placeholder for list ID: {list_id}. This view needs to be implemented.")


urlpatterns = [
    path('', views.home, name='home'),
    path('list/create/', views.create_packing_list, name='create_packing_list'),
    path('list/upload/', views.upload_packing_list, name='upload_packing_list'),
    path('list/<int:list_id>/', views.packing_list_detail, name='view_packing_list'),

    # URLs for managing prices
    path('item/<int:item_id>/add_price/', views.add_price_for_item, name='add_price_for_item_no_list'), # For adding price without list context
    path('item/<int:item_id>/add_price/to_list/<int:list_id>/', views.add_price_for_item, name='add_price_for_item'),
    path('vote/', views.handle_vote, name='handle_vote'),

    # URL for configuring uploaded list
    path('list/upload/configure/<str:session_key_items>/', views.configure_uploaded_list, name='configure_uploaded_list'),

    # URL for listing stores
    path('stores/', views.store_list, name='store_list'),

    path('add-store-ajax/', views.add_store_ajax, name='add_store_ajax'),

    path('list/<int:list_id>/add_item/', views.add_item_to_list, name='add_item_to_list'),
    path('list/<int:list_id>/edit_item/<int:pli_id>/', views.edit_item_in_list, name='edit_item_in_list'),
]
