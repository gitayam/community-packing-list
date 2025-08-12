#!/usr/bin/env python
"""
Script to fix cloud database by applying migration and generating slugs
"""
import os
import sys
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'community_packing_list.settings_cloud')

try:
    print("=== Cloud Database Fix Starting ===")
    
    import django
    django.setup()
    
    print("1. Running migrations...")
    from django.core.management import call_command
    call_command('migrate', verbosity=1)
    
    print("2. Generating share slugs...")
    from packing_lists.models import PackingList
    from django.utils.text import slugify
    import uuid
    
    updated_count = 0
    for plist in PackingList.objects.filter(share_slug__isnull=True):
        base_slug = slugify(plist.name)[:50]
        plist.share_slug = f'{base_slug}-{uuid.uuid4().hex[:8]}'
        plist.save()
        updated_count += 1
        print(f'   Generated slug: {plist.name} -> {plist.share_slug}')
    
    print(f"3. Updated {updated_count} lists with share slugs")
    
    print("4. Database status check...")
    total_lists = PackingList.objects.count()
    public_lists = PackingList.objects.filter(is_public=True).count()
    lists_with_slugs = PackingList.objects.exclude(share_slug__isnull=True).count()
    
    print(f"   Total lists: {total_lists}")
    print(f"   Public lists: {public_lists}")
    print(f"   Lists with slugs: {lists_with_slugs}")
    
    print("=== Cloud Database Fix COMPLETED ===")
    
except Exception as e:
    print("=== Cloud Database Fix FAILED ===")
    print(f"ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)