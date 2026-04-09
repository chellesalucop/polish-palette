from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache

def health_check(request):
    """Lightweight health check endpoint"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Test cache
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'cache': 'working'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)

class HealthCheckMiddleware:
    """Bypass middleware for health checks to improve performance"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/health/':
            # Skip all middleware for health checks
            return health_check(request)
        return self.get_response(request)
