from .settings import *
import os

# --- Production Security ---
DEBUG = False
ALLOWED_HOSTS = ['*']  # Set to your domain or Cloud Run URL in production

# --- Secret Key ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'unsafe-default-key')

# --- Database: Google Cloud SQL (Postgres) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', ''),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASS', ''),
        'HOST': os.environ.get('DB_HOST', ''),  # Use Cloud SQL Proxy socket or public IP
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# --- Google Cloud Storage for Static/Media ---
USE_GCS = os.environ.get('USE_GCS', 'true').lower() == 'true'
if USE_GCS:
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_BUCKET_NAME = os.environ.get('GS_BUCKET_NAME')
    GS_PROJECT_ID = os.environ.get('GS_PROJECT_ID')
    GS_DEFAULT_ACL = 'publicRead'
    GS_LOCATION = os.environ.get('GS_LOCATION', '')
    GS_CREDENTIALS = None  # Use default service account
    STATIC_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/static/'
    MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/media/'
else:
    # Fallback: WhiteNoise for static files
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- Security Settings ---
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# --- Logging (optional, can be expanded) ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
} 