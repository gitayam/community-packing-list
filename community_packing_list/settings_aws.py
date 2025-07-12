from .settings import *
import os
import dj_database_url

# --- Production Security ---
DEBUG = False
ALLOWED_HOSTS = ['*']  # API Gateway handles host validation

# --- Secret Key ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'unsafe-fallback-key-change-in-production')

# --- Database Configuration ---
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # Construct from individual components
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'packinglist_dev'),
            'USER': os.environ.get('DB_USER', 'packinglist_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'OPTIONS': {
                'sslmode': 'require',
            }
        }
    }

# Optimize database connections for Lambda
DATABASES['default'].update({
    'CONN_MAX_AGE': 0,  # Don't persist connections in Lambda
    'OPTIONS': {
        'sslmode': 'require',
        'connect_timeout': 10,
        'options': '-c default_transaction_isolation=serializable'
    }
})

# --- AWS S3 Configuration ---
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('STATIC_BUCKET')
AWS_S3_REGION_NAME = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
AWS_S3_CUSTOM_DOMAIN = os.environ.get('CLOUDFRONT_DOMAIN')

# S3 Static Files Configuration
if AWS_STORAGE_BUCKET_NAME:
    # Static files
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  # 24 hours
    }
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False
    
    if AWS_S3_CUSTOM_DOMAIN:
        STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    else:
        STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/'
    
    # Media files (separate bucket for security)
    MEDIA_BUCKET = os.environ.get('MEDIA_BUCKET')
    if MEDIA_BUCKET:
        DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
        MEDIA_URL = f'https://{MEDIA_BUCKET}.s3.amazonaws.com/media/'
else:
    # Fallback to local storage (not recommended for production)
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'

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

# Trust API Gateway headers
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# --- Cache Configuration ---
# Use local memory cache for Lambda (Redis would require VPC)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    }
}

# --- Session Configuration ---
# Use database sessions for Lambda
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True

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
        'lambda_handler': {
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

# --- Lambda-specific optimizations ---
# Disable migrations check in Lambda
MIGRATION_MODULES = {
    'packing_lists': None,
}

# Optimize for cold starts
CONN_MAX_AGE = 0
DATABASES['default']['CONN_MAX_AGE'] = 0

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Timezone
USE_TZ = True
TIME_ZONE = 'UTC'

# Email Configuration (using SES)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('SES_USERNAME', '')
EMAIL_HOST_PASSWORD = os.environ.get('SES_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@example.com')

# --- CORS Configuration ---
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://localhost:3000",  # For local development
    "https://localhost:8000",  # For local development
]

# Add custom domains from environment
CUSTOM_DOMAINS = os.environ.get('CUSTOM_DOMAINS', '').split(',')
for domain in CUSTOM_DOMAINS:
    if domain.strip():
        CORS_ALLOWED_ORIGINS.append(f"https://{domain.strip()}")

print(f"AWS Lambda Django settings loaded successfully")
print(f"Database: {DATABASES['default']['HOST']}")
print(f"Static URL: {STATIC_URL}")
print(f"Debug: {DEBUG}") 