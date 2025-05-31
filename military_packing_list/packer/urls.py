from django.urls import path
from . import views

app_name = 'packer'

urlpatterns = [
    path('', views.item_list_view, name='item_list'),
    path('item/<int:item_id>/', views.item_detail_view, name='item_detail'),
    path('item/<int:item_id>/add_price/', views.add_price_view, name='add_price'),
    path('price/<int:price_id>/vote/<str:vote_type>/', views.vote_view, name='vote_price'),
]
