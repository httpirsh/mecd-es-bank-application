from .models import LoanSimulation, LoanDetails, User, LoanApplication, LoanEvaluation
from boto3.dynamodb.conditions import Attr
from django.http import JsonResponse
from django.conf import settings
from django.views import View
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from utils import generate_jwt_token, get_jwt_decoded, decode_jwt_token, get_user_from_dynamodb, save_loan_application
from .serializers import LoanApplicationSerializer, LoanEvaluationSerializer
import datetime
import base64
import os
import boto3
import json
import logging

logger = logging.getLogger('bank.api')

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
            loan_simulation = LoanSimulation(amount=loan_amount, duration=loan_duration)

            # Calculate loan details
            loan_details = LoanDetails(loan_simulation=loan_simulation)
            loan_details.calculate_details()

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

                    # Set the token in an HTTP-only cookie
                    response = JsonResponse({"success": True, "message": "Login successful"})
                    response.set_cookie(
                        'jwt_token',
                        token,
                        max_age=datetime.timedelta(days=1),
                        httponly=True, # Cannot be accessed via JavaScript
                        secure=True, # Use only over HTTPS
                        samesite='Strict' # Protects against CSRF attacks
                    )
                    return response
                else:
                    return JsonResponse({"error": "Face not recognized"}, status=401)
            else:
                return JsonResponse({"error": "No matching face found"}, status=401)

        except Exception as e:
            print(f"Error during Rekognition process: {str(e)}")
            return JsonResponse({"error": f"Rekognition error: {str(e)}"}, status=500)

    def get_user_by_face_id(self, face_id):
        """
        Retrieves user by face_id.
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
        
class LoanApplicationViewSet(viewsets.ModelViewSet):
    queryset = LoanApplication.objects.all()
    serializer_class = LoanApplicationSerializer
    http_method_names = ['get', 'post', 'delete']

    def create(self, request, *args, **kwargs):
        customer = self.auth_user_is(request, "customer")

        # Extract data from the request
        try:
            data = request.data.copy()
            monthly_income = int(data["monthly_income"])
            monthly_expenses = int(data["monthly_expenses"])
            amount = int(data["amount"])
            duration = int(data["duration"])
        except Exception as e:
            raise ValidationError(detail=f"Wrong data in one of (monthly_income, monthly_expenses, amount, duration). Must be valid integers.")

        # Calculate the credit score and classify the application
        credit_score = self.calculate_credit_score(monthly_income, monthly_expenses, amount, duration)
        application_status = self.classify_application(credit_score)
        data['credit_score'] = credit_score
        data['application_status'] = application_status
        data['username'] = customer['username']

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        self.auth_user_is(request, "officer") # TODO: customer should be able to list his own applications
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        self.auth_user_is(request, "officer") # TODO: customer should be able to retrieve his own applications
        return super().retrieve(request, *args, **kwargs)

    # eliminarrrr -------------------
    # substituir pelo workflow
    def calculate_credit_score(self, monthly_income, monthly_expenses, amount, duration):
        """
        Simplified formula for credit score calculation.
        """
        score = 100
        expense_ratio = (monthly_expenses / monthly_income) * 100
        score -= expense_ratio

        risk = amount / (monthly_income * duration) * 100
        score -= risk

        return max(0, min(int(score), 100))

    # substituir pelo workflow
    def classify_application(self, credit_score):
        """
        Classify loan application based on the credit score.
        """
        if credit_score >= 70:
            return "accept"
        elif credit_score >= 40:
            return "interview"
        else:
            return "reject"

    def auth_user_is(self, request, user_type):
        """
        Retrieves the authenticated user from session and returns the user data if user_type matches.
        If session not authenticated or user is not of user_type, returns None.
        """
        try:
            user_data = get_jwt_decoded(request)
            username = user_data.get("username")

            # Verify if user in session is a customer in our system
            user = get_user_from_dynamodb(username)
            if (user and user['user_type'] == user_type):
                return user
        except Exception as e:
            logger.error(f"Error occurred retrieving authentication data: {e}", exc_info=True)
    
        raise AuthenticationFailed(detail=f"Session is not authenticated by one {user_type}.")

class LoanEvaluationViewSet(viewsets.ModelViewSet):
    queryset = LoanEvaluation.objects.all()
    serializer_class = LoanEvaluationSerializer