from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from .api_views import (
    SchoolViewSet, BaseViewSet, StoreViewSet, PackingListViewSet,
    ItemViewSet, PackingListItemViewSet, PriceViewSet, VoteViewSet
)

def health_check(request):
    """Simple health check endpoint for Docker and monitoring"""
    return JsonResponse({"status": "healthy", "service": "community-packing-list-api"})

router = DefaultRouter()
router.register(r'schools', SchoolViewSet, basename='school')
router.register(r'bases', BaseViewSet, basename='base')
router.register(r'stores', StoreViewSet, basename='store')
router.register(r'packing-lists', PackingListViewSet, basename='packing-list')
router.register(r'items', ItemViewSet, basename='item')
router.register(r'packing-list-items', PackingListItemViewSet, basename='packing-list-item')
router.register(r'prices', PriceViewSet, basename='price')
router.register(r'votes', VoteViewSet, basename='vote')

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('', include(router.urls)),
]
