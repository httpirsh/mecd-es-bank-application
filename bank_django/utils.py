from api.models import LoanApplication
from django.conf import settings
from django.http import JsonResponse
import boto3
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
    
def decode_jwt_token(token):
    """
    Decodes the JWT token and returns the payload (user data).
    """
    try:
        # Decode JWT using the secret key and algorithm
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
    

def get_user_from_dynamodb(username):
    """
    Retrieves a user from DynamoDB based on username.
    """
    try:
        dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        table = dynamodb.Table(settings.AWS_DYNAMO_TABLE_NAME)

        response = table.get_item(Key={'username': username})
        if 'Item' in response:
            return response['Item']
        return None
    except Exception as e:
        print(f"Error retrieving user from DynamoDB: {e}")
        return None

def save_loan_application(user, monthly_income, monthly_expenses, loan_amount, loan_duration, credit_score, application_status):
    """
    Saves the loan application linked to the user in database.
    """
    loan_application = LoanApplication(
        username=user['username'],  # Link the application to the user
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        loan_amount=loan_amount,
        loan_duration=loan_duration,
        credit_score=credit_score,
        application_status=application_status
    )

    loan_application.save()  # Save the loan application to database
    return loan_application