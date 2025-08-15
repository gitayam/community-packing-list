#!/usr/bin/env python
"""
Script to generate share_slug values for existing packing lists
"""
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'community_packing_list.settings_cloud')
django.setup()

from packing_lists.models import PackingList
from django.utils.text import slugify
import uuid

print("Generating share slugs for existing packing lists...")

# Generate slugs for existing lists that don't have them
for plist in PackingList.objects.filter(share_slug__isnull=True):
    base_slug = slugify(plist.name)[:50]
    plist.share_slug = f'{base_slug}-{uuid.uuid4().hex[:8]}'
    plist.save()
    print(f'Generated slug for "{plist.name}": {plist.share_slug}')

print("Slug generation completed!")

# Also list all public lists with their share URLs
print("\nPublic packing lists:")
for plist in PackingList.objects.filter(is_public=True):
    print(f"- {plist.name}: /share/{plist.share_slug}/")