#!/usr/bin/env python
"""
Debug script to check what's wrong with the deployment
"""
import os
import django
import traceback
from django.conf import settings

try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'community_packing_list.settings_cloud')
    django.setup()
    
    print("Django setup successful!")
    print(f"Database URL: {getattr(settings, 'DATABASES', {})}")
    
    # Test database connection
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"Database connection successful: {result}")
    
    # Test basic model import
    from packing_lists.models import PackingList
    count = PackingList.objects.count()
    print(f"PackingList count: {count}")
    
    # Test model with new fields
    first_list = PackingList.objects.first()
    if first_list:
        print(f"First list: {first_list.name}")
        print(f"Share slug: {first_list.share_slug}")
        print(f"Is public: {first_list.is_public}")
    
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()