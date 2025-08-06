"""
Celery configuration for Community Packing List.
Handles background tasks like price aggregation and cache warming.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'community_packing_list.settings_cloud')

app = Celery('community_packing_list')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    'update-price-scores': {
        'task': 'packing_lists.tasks.update_price_scores',
        'schedule': 900.0,  # Every 15 minutes
    },
    'warm-popular-items-cache': {
        'task': 'packing_lists.tasks.warm_popular_items_cache',
        'schedule': 3600.0,  # Every hour
    },
    'cleanup-old-sessions': {
        'task': 'packing_lists.tasks.cleanup_old_sessions',
        'schedule': 86400.0,  # Daily
    },
}

app.conf.timezone = 'UTC'

# Configure task routes for better performance
app.conf.task_routes = {
    'packing_lists.tasks.update_price_scores': {'queue': 'high_priority'},
    'packing_lists.tasks.process_uploaded_file': {'queue': 'file_processing'},
    'packing_lists.tasks.send_notification_email': {'queue': 'notifications'},
}

# Task serialization and compression
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.result_compression = 'gzip'
app.conf.task_compression = 'gzip'

# Result backend configuration
app.conf.result_expires = 3600  # 1 hour

# Task execution configuration
app.conf.task_always_eager = False
app.conf.task_acks_late = True
app.conf.worker_prefetch_multiplier = 1

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')