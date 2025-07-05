#!/usr/bin/env python3
"""
Startup script for Community Packing List application.
This script runs migrations and creates example data.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'community_packing_list.settings')
    django.setup()
    
    # Run migrations
    print("Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Create example data
    print("Creating example data...")
    execute_from_command_line(['manage.py', 'create_example_data'])
    
    # Start the development server
    print("Starting development server...")
    execute_from_command_line(['manage.py', 'runserver'])

if __name__ == '__main__':
    main() 