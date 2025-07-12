"""
Health check endpoint for Cloud Run
"""
import os
import sys
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for Cloud Run
    Returns 200 if all systems are healthy, 503 otherwise
    """
    checks = {
        'database': False,
        'cache': False,
        'environment': False
    }
    
    overall_status = 'healthy'
    status_code = 200
    
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            checks['database'] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks['database'] = False
        overall_status = 'unhealthy'
        status_code = 503
    
    try:
        # Check cache (if configured)
        cache.set('health_check', 'ok', 30)
        if cache.get('health_check') == 'ok':
            checks['cache'] = True
        else:
            checks['cache'] = False
    except Exception as e:
        logger.warning(f"Cache health check failed: {e}")
        checks['cache'] = False
        # Cache is not critical, don't fail health check
    
    # Check environment variables
    required_env_vars = [
        'GOOGLE_CLOUD_PROJECT',
        'DATABASE_URL',
        'DJANGO_SECRET_KEY'
    ]
    
    missing_env_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_env_vars.append(var)
    
    if missing_env_vars:
        checks['environment'] = False
        overall_status = 'unhealthy'
        status_code = 503
        logger.error(f"Missing environment variables: {missing_env_vars}")
    else:
        checks['environment'] = True
    
    response_data = {
        'status': overall_status,
        'checks': checks,
        'version': os.getenv('GAE_VERSION', 'unknown'),
        'service': os.getenv('GAE_SERVICE', 'community-packing-list'),
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }
    
    if missing_env_vars:
        response_data['missing_env_vars'] = missing_env_vars
    
    return JsonResponse(response_data, status=status_code)

@csrf_exempt 
@require_http_methods(["GET"])
def readiness_check(request):
    """
    Readiness check - simpler check for whether service can handle requests
    """
    try:
        # Just check if Django is responding
        return JsonResponse({
            'status': 'ready',
            'service': 'community-packing-list'
        })
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JsonResponse({
            'status': 'not ready',
            'error': str(e)
        }, status=503)