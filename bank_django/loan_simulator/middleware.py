import jwt
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.models import User

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in ['/simulator/', '/login/', '/favicon.ico']: 
            return self.get_response(request)

        # Extract the token from the Authorization header
        token = request.headers.get('Authorization')
        if token:
            try:
                if token.startswith('Bearer '):
                    token = token[7:]  # Remove 'Bearer ' prefix

                # Decode the token using the secret key
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
                request.user = User.objects.get(username=payload['username'])  # Add user to the request object
            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "Token has expired"}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({"error": "Invalid token"}, status=401)
            except User.DoesNotExist:
                return JsonResponse({"error": "User not found"}, status=404)
        else:
            return JsonResponse({"error": "Authorization token required"}, status=401)

        return self.get_response(request)