from bank_website.settings import JWT_SECRET_KEY
from .models import LoanSimulation, LoanDetails, User
from boto3.dynamodb.conditions import Attr
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.views import View
import datetime
import base64
import os
import boto3
import json
import jwt

# Initialize Rekognition and DynamoDB clients
rekognition_client = boto3.client('rekognition', region_name=os.environ.get("AWS_DEFAULT_REGION"))
dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
print(f"DynamoDB client initialized: {dynamodb}")
table = dynamodb.Table('Users')

class LoanSimulationView(View):
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for loan simulation.
        """
        try:
            data = json.loads(request.body)
            loan_amount = int(data.get("loan_amount", 0))
            loan_duration = int(data.get("loan_duration", 0))
            
            # Validate inputs
            if loan_amount <= 0 or loan_duration <= 0:
                return JsonResponse({"error": "Invalid loan amount or duration"}, status=400)

            # Create a LoanSimulation object
            loan_simulation = LoanSimulation.objects.create(amount=loan_amount, duration=loan_duration)

            # Calculate loan details
            loan_details = LoanDetails.objects.create(loan_simulation=loan_simulation)
            loan_details.calculate_and_save_details()

            # Prepare response data
            result = {
                "interest_rate": loan_details.interest_rate,
                "total_repayment": loan_details.total_repayment,
                "monthly_installment": loan_details.monthly_payment
            }

            return JsonResponse(result)

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    def get(self, request, *args, **kwargs):
        """
        Optionally handle GET requests to provide simulator info (e.g., default values).
        """
        return JsonResponse({"message": "Loan Simulator API is active!"}, status=200)

class LoginView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        image_data = data.get('image')

        if not image_data:
            return JsonResponse({"error": "Image file is required"}, status=400)

        try:
            # Decode the base64 image data
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return JsonResponse({"error": "Error decoding image"}, status=400)

        try:
            # Search for the face in Rekognition's collection
            rekognition_client = boto3.client('rekognition', region_name=os.environ.get('AWS_DEFAULT_REGION'))
            response = rekognition_client.search_faces_by_image(
                CollectionId=os.environ.get('AWS_COLLECTION_NAME'),
                Image={'Bytes': image_bytes},
                MaxFaces=1,
                FaceMatchThreshold=70
            )

            if 'FaceMatches' in response and response['FaceMatches']:
                face_id = response['FaceMatches'][0]['Face']['FaceId']
                print(f"Rekognition Face ID: {face_id}")

                user = self.get_user_by_face_id(face_id)
                if user:
                    print(f"Found user: {user.username}")
                    # Generate JWT Token
                    token = generate_jwt_token(user)
                    return JsonResponse({"success": True, "token":token})
                
                else:
                    return JsonResponse({"error": "Face not recognized"}, status=401)
            else:
                return JsonResponse({"error": "No matching face found"}, status=401)

        except Exception as e:
            print(f"Error during Rekognition process: {str(e)}")
            return JsonResponse({"error": f"Rekognition error: {str(e)}"}, status=500)

    def get_user_by_face_id(self, face_id):
        """
        Recovers the Django user based on face_id.
        """
        try:
            dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
            table = dynamodb.Table(settings.AWS_DYNAMO_TABLE_NAME)
            print(f"Table initialized: {table}")
            print(f"Searching for user with face_id: {face_id} (type: {type(face_id)})")

            response = table.scan(
                FilterExpression=Attr('face_id').eq(str(face_id))
            )

            print(f"DynamoDB response: {response}")

            if 'Items' in response and response['Items']:
                user_data = response['Items'][0]
                # Create a User instance from the response
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    phone=user_data['phone'],
                    face_id=user_data['face_id']
                )
                return user
            else:
                return None

        except Exception as e:
            print(f"Error retrieving user from DynamoDB: {e}")
            return None

class ProtectedResourceView(View):
    def get(self, request, *args, **kwargs):
        # Check for the token in the Authorization header
        token = request.headers.get('Authorization')
        if not token:
            return JsonResponse({"error": "Token is required"}, status=401)

        try:
            # Remove the "Bearer " prefix from the token if present
            if token.startswith('Bearer '):
                token = token[7:]

            # Verify the JWT token
            payload = verify_jwt_token(token)
            username = payload.get('username')

            # Retrieve the user from the database using the username
            user = User.objects.get(username=username)

            # If the user is found, return the protected resource
            return JsonResponse({"message": f"Hello, {user.username}!"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=401)
    

# Functions -----------------------

def generate_jwt_token(user):
    """Generate JWT token for the user."""
    payload = {
        'username': user.username,
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)  # Set expiration time for token
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

    # Log the token for debugging (BE CAREFUL in production, as logging tokens can be a security risk)
    print(f"Generated JWT Token: {token}")

    return token

def index(request):
    return render(request, "login.html")

def verify_jwt_token(token):
    try:
        # Decode the token using the secret key
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload  # Return the decoded payload if the token is valid
    except jwt.ExpiredSignatureError:
        raise Exception('Token has expired')
    except jwt.InvalidTokenError:
        raise Exception('Invalid token')
