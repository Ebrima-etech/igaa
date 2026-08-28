import os

class SimpleCORSMiddleware:
    """Simple CORS middleware to handle preflight requests."""

    def __init__(self, get_response):
        self.get_response = get_response
        cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003')
        self.allowed_origins = [origin.strip() for origin in cors_origins.split(',')]

    def __call__(self, request):
        origin = request.META.get('HTTP_ORIGIN', '')

        # Handle preflight requests
        if request.method == 'OPTIONS':
            response = self.get_response(request)
        else:
            response = self.get_response(request)

        # Add CORS headers if origin is allowed
        if origin in self.allowed_origins:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Methods'] = 'DELETE, GET, OPTIONS, PATCH, POST, PUT'
            response['Access-Control-Allow-Headers'] = 'accept, accept-encoding, authorization, content-type, dnt, origin, user-agent, x-csrftoken, x-requested-with'
            response['Access-Control-Max-Age'] = '86400'

        return response
