from .settings import *
import os
import dj_database_url
from google.cloud import secretmanager
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Production Security ---
DEBUG = False

# Cloud Run provides the service URL in environment
SERVICE_URL = os.environ.get('CLOUD_RUN_SERVICE_URL', '')
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.run.app',  # Cloud Run domains
    '.googleapis.com',
]

# Add custom domain if provided
CUSTOM_DOMAIN = os.environ.get('CUSTOM_DOMAIN')
if CUSTOM_DOMAIN:
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)

# --- Secret Management ---
def get_secret(secret_id, project_id=None):
    """Retrieve secret from Google Secret Manager"""
    try:
        if not project_id:
            project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        
        if not project_id:
            logger.warning(f"No project ID available for secret {secret_id}")
            return None
            
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.error(f"Failed to retrieve secret {secret_id}: {e}")
        return None

# Get secrets or fall back to environment variables
SECRET_KEY = (
    os.environ.get('DJANGO_SECRET_KEY') or 
    get_secret('django-secret-key') or 
    'unsafe-fallback-key-change-in-production'
)

# --- Database Configuration ---
DATABASE_URL = (
    os.environ.get('DATABASE_URL') or 
    get_secret('database-url')
)

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
    # Optimize for Cloud SQL
    DATABASES['default'].update({
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'sslmode': 'prefer',
        }
    })
else:
    logger.error("No DATABASE_URL found in environment or secrets")
    # Fallback to SQLite for development only
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --- Google Cloud Storage Configuration ---
GS_BUCKET_NAME = (
    os.environ.get('GS_BUCKET_NAME') or 
    get_secret('static-bucket-name')
)

GS_MEDIA_BUCKET_NAME = (
    os.environ.get('GS_MEDIA_BUCKET_NAME') or 
    get_secret('media-bucket-name')
)

# Configure Cloud Storage if buckets are available
if GS_BUCKET_NAME:
    # Static files configuration
    STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT')
    GS_DEFAULT_ACL = 'publicRead'
    GS_QUERYSTRING_AUTH = False
    GS_CACHE_CONTROL = 'public, max-age=31536000'  # 1 year cache
    STATIC_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/'
    
    # Media files configuration (separate bucket for security)
    if GS_MEDIA_BUCKET_NAME:
        DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
        GS_MEDIA_BUCKET_NAME = GS_MEDIA_BUCKET_NAME
        MEDIA_URL = f'https://storage.googleapis.com/{GS_MEDIA_BUCKET_NAME}/'
    
    logger.info(f"Using Cloud Storage: static={GS_BUCKET_NAME}, media={GS_MEDIA_BUCKET_NAME}")
else:
    # Fallback to WhiteNoise for static files
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = False
    logger.warning("Using WhiteNoise fallback for static files")

# --- Security Settings ---
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# --- CORS Configuration (if needed for API endpoints) ---
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    SERVICE_URL,
]
if CUSTOM_DOMAIN:
    CORS_ALLOWED_ORIGINS.append(f"https://{CUSTOM_DOMAIN}")

# --- Cache Configuration ---
# Use Redis if available, otherwise in-memory cache
REDIS_URL = os.environ.get('REDIS_URL')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'KEY_PREFIX': 'packing-list',
            'TIMEOUT': 300,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

# --- Performance Optimizations ---
# Connection pooling for database
DATABASES['default'].setdefault('OPTIONS', {})
DATABASES['default']['OPTIONS'].update({
    'MAX_CONNS': 20,
    'MIN_CONNS': 5,
})

# --- Logging Configuration ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'packing_lists': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# --- Email Configuration (optional) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@example.com')

# --- Django Settings Optimization ---
# Optimize sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 hours

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Internationalization
USE_TZ = True
TIME_ZONE = 'UTC'

logger.info("GCP production settings loaded successfully") 