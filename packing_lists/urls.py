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
    path('packer/', views.home, name='packer_home'),  # Alternative URL for home page
    path('lists/', views.lists_page, name='lists'),
    path('items/', views.items_page, name='items'),
    path('list/create/', views.create_packing_list, name='create_packing_list'),
    path('list/<int:list_id>/', views.packing_list_detail, name='view_packing_list'),
    path('list/<int:list_id>/edit/', views.edit_packing_list, name='edit_packing_list'),

    # URLs for managing prices
    path('item/<int:item_id>/add_price/', views.add_price_for_item, name='add_price_for_item_no_list'), # For adding price without list context
    path('item/<int:item_id>/add_price/to_list/<int:list_id>/', views.add_price_for_item, name='add_price_for_item'),
    path('vote/', views.handle_vote, name='handle_vote'),

    # URL for listing stores
    path('stores/', views.store_list, name='store_list'),

    # URLs for managing items
    path('list/<int:list_id>/add_item/', views.add_item_to_list, name='add_item_to_list'),
    path('list/<int:list_id>/edit_item/<int:pli_id>/', views.edit_item_in_list, name='edit_item_in_list'),
    path('stores/<int:store_id>/edit/', views.store_edit, name='edit_store'),

    path('item/<int:item_id>/add_price_modal/to_list/<int:list_id>/', views.price_form_partial, name='add_price_for_item_modal'),
    path('list/<int:list_id>/edit_item_modal/<int:pli_id>/', views.edit_item_modal, name='edit_item_modal'),

    path('stores/add/modal/', views.add_store_modal, name='add_store_modal'),
    path('create_packing_list_from_items/', views.create_packing_list_from_items, name='create_packing_list_from_items'),

    path('lists/merge/', views.merge_packing_lists, name='merge_packing_lists'),
    path('lists/delete/', views.delete_packing_lists, name='delete_packing_lists'),
    path('list/<int:list_id>/clone/', views.clone_packing_list, name='clone_packing_list'),
    path('list/<int:list_id>/export_pdf/', views.export_packing_list_pdf, name='export_packing_list_pdf'),
]
