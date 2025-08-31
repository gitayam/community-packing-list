"""
URL configuration for community_packing_list project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("packing_lists.urls")),
]

# Serve static files during development and production
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve media files during development
if settings.DEBUG and hasattr(settings, 'MEDIA_URL'):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)