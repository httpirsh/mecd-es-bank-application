from django.conf import settings
from django.http import JsonResponse
import datetime
import jwt

def generate_jwt_token(user):
    """Generate JWT token for the user."""
    payload = {
        'username': user.username,
        'email': user.email,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)  # Use timezone-aware datetime
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
    print(f"Generated JWT Token: {token}")
    return token

def verify_jwt_token(request):
    """Verify the JWT token from the Authorization header or cookies."""
    # Check for token in cookies
    token = request.COOKIES.get('jwt_token')
    
    # If no token in cookies, try to get it from the Authorization header
    if not token:
        authorization_header = request.headers.get('Authorization')
        if authorization_header:
            # Extract token from the "Bearer <token>" format
            token = authorization_header.split(' ')[1] if authorization_header.startswith('Bearer ') else None

    if not token:
        return JsonResponse({"error": "Authorization token is required"}, status=401)

    try:
        # Decode the token using the secret key to get the user data
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload  # Return the decoded payload (user data)
    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Token has expired"}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid token"}, status=401)
