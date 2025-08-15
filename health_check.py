#!/usr/bin/env python
"""
Simple health check script to isolate the 500 error cause
"""
import os
import sys
import traceback

# Set Django settings before importing anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'community_packing_list.settings_cloud')

try:
    print("=== Health Check Starting ===")
    
    print("1. Python version:", sys.version)
    print("2. Environment variables check...")
    print("   - SECRET_KEY set:", "SECRET_KEY" in os.environ)
    print("   - DEBUG:", os.environ.get('DEBUG', 'Not set'))
    
    print("3. Django setup...")
    import django
    django.setup()
    print("   - Django version:", django.get_version())
    print("   - Django setup: SUCCESS")
    
    print("4. Settings check...")
    from django.conf import settings
    print("   - SECRET_KEY length:", len(settings.SECRET_KEY))
    print("   - DEBUG:", settings.DEBUG)
    print("   - ALLOWED_HOSTS:", settings.ALLOWED_HOSTS)
    
    print("5. Database connection...")
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print("   - Database connection: SUCCESS", result)
    
    print("6. Model imports...")
    from packing_lists.models import PackingList, Item
    print("   - Models imported: SUCCESS")
    
    print("7. Basic model query...")
    count = PackingList.objects.count()
    print("   - PackingList count:", count)
    
    print("8. Check sharing fields...")
    first_list = PackingList.objects.first()
    if first_list:
        print("   - First list name:", first_list.name)
        print("   - Has share_slug:", hasattr(first_list, 'share_slug'))
        print("   - Share slug value:", getattr(first_list, 'share_slug', 'MISSING'))
        print("   - Has view_count:", hasattr(first_list, 'view_count'))
        print("   - View count value:", getattr(first_list, 'view_count', 'MISSING'))
    
    print("9. URL resolution test...")
    from django.urls import reverse
    home_url = reverse('home')
    print("   - Home URL:", home_url)
    
    # Test sharing URLs if they exist
    if first_list and hasattr(first_list, 'share_slug') and first_list.share_slug:
        try:
            public_url = reverse('public_list', kwargs={'share_slug': first_list.share_slug})
            print("   - Public list URL:", public_url)
        except Exception as e:
            print("   - Public URL error:", str(e))
    
    print("=== Health Check PASSED ===")
    
except Exception as e:
    print("=== Health Check FAILED ===")
    print(f"ERROR: {e}")
    print("TRACEBACK:")
    traceback.print_exc()
    sys.exit(1)