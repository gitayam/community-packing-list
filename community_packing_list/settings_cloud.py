"""
Django settings for cloud deployment (Google Cloud Run, App Engine, etc.)
"""

import os
import dj_database_url
from .settings import *

# Override settings for cloud deployment
DEBUG = False

# Cloud environment variables
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

# Allowed hosts for cloud deployment
ALLOWED_HOSTS = [
    '.run.app',
    '.appspot.com',
    'localhost',
    '127.0.0.1',
]

# Add any custom domain hosts from environment
CUSTOM_DOMAIN = os.environ.get('CUSTOM_DOMAIN')
if CUSTOM_DOMAIN:
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)

# Add WhiteNoise middleware for static file serving
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CSRF trusted origins for cloud deployment
CSRF_TRUSTED_ORIGINS = [
    'https://*.run.app',
    'https://*.appspot.com',
]

if CUSTOM_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f'https://{CUSTOM_DOMAIN}')

# Database configuration using DATABASE_URL with PostgreSQL optimizations
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,
        # PostgreSQL optimizations
        options={
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        } if 'mysql' in dj_database_url.config().get('ENGINE', '') else {}
    )
}

# PostgreSQL-specific optimizations when using PostgreSQL
db_config = dj_database_url.config()
if 'postgresql' in db_config.get('ENGINE', ''):
    DATABASES['default']['OPTIONS'] = {
        'init_command': "SET default_transaction_isolation='read committed'",
        'options': '-c default_transaction_isolation=serializable'
    }
    
    # Enable connection pooling for PostgreSQL
    DATABASES['default']['CONN_MAX_AGE'] = 0  # Use persistent connections
    
    # Add read replica support (when available)
    read_replica_url = os.environ.get('DATABASE_READ_REPLICA_URL')
    if read_replica_url:
        DATABASES['read_replica'] = dj_database_url.parse(read_replica_url)
        DATABASE_ROUTERS = ['packing_lists.routers.DatabaseRouter']

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Use HTTPS in production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static files configuration for cloud storage
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Include only necessary directories in static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'packing_lists', 'static'),
    os.path.join(BASE_DIR, 'src', 'styles'),  # Only include the styles directory from src
]

# WhiteNoise configuration for static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Static files optimization
WHITENOISE_USE_FINDERS = False  # Disable in production for better performance
WHITENOISE_AUTOREFRESH = False  # Disable auto-refresh in production
WHITENOISE_MAX_AGE = 31536000  # Cache static files for 1 year

# Add .js and .css MIME types for compression
WHITENOISE_MIMETYPES = {
    '.js': 'application/javascript',
    '.css': 'text/css',
    '.map': 'application/json',
    '.svg': 'image/svg+xml',
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Media files configuration - Cloud Storage for production
USE_CLOUD_STORAGE = os.environ.get('USE_CLOUD_STORAGE', 'false').lower() == 'true'

if USE_CLOUD_STORAGE:
    # Google Cloud Storage settings
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_BUCKET_NAME = os.environ.get('GS_BUCKET_NAME', 'community-packing-list-media')
    GS_PROJECT_ID = os.environ.get('GS_PROJECT_ID')
    GS_DEFAULT_ACL = 'publicRead'
    GS_FILE_OVERWRITE = False
    GS_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
    
    # CDN for media files
    GS_CUSTOM_ENDPOINT = os.environ.get('GS_CUSTOM_ENDPOINT')  # CDN endpoint
    MEDIA_URL = f'https://{GS_CUSTOM_ENDPOINT}/' if GS_CUSTOM_ENDPOINT else f'https://storage.googleapis.com/{GS_BUCKET_NAME}/'
    
    # Static files via Cloud Storage + CDN
    STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_STATIC_BUCKET_NAME = os.environ.get('GS_STATIC_BUCKET_NAME', 'community-packing-list-static')
    STATIC_URL = f'https://storage.googleapis.com/{GS_STATIC_BUCKET_NAME}/'
    
else:
    # Local development settings
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Cache configuration - Redis for production, LocMem for development
REDIS_URL = os.environ.get('REDIS_URL')
if REDIS_URL:
    # Production Redis configuration
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                },
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                'IGNORE_EXCEPTIONS': True,  # Don't fail if Redis is down
            },
            'TIMEOUT': 300,  # Default timeout
            'KEY_PREFIX': 'cpl',
        }
    }
    
    # Use Redis for sessions as well
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
else:
    # Fallback to local memory cache for development
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
            'TIMEOUT': 300,
        }
    }

# Cache middleware settings
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 300  # 5 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = 'cpl'

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', REDIS_URL)

if CELERY_BROKER_URL:
    # Celery task configuration
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'UTC'
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
    CELERY_WORKER_PREFETCH_MULTIPLIER = 1
    CELERY_TASK_ACKS_LATE = True
    
    # Configure task routing
    CELERY_TASK_ROUTES = {
        'packing_lists.tasks.update_price_scores': {'queue': 'high_priority'},
        'packing_lists.tasks.process_uploaded_file': {'queue': 'file_processing'},
        'packing_lists.tasks.send_notification_email': {'queue': 'notifications'},
    }