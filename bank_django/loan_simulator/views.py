from .models import LoanSimulation, LoanDetails, User
from boto3.dynamodb.conditions import Attr
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.views import View
from utils import generate_jwt_token, verify_jwt_token, decode_jwt_token, get_user_from_dynamodb, save_loan_application
import datetime
import base64
import os
import boto3
import json

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

    def get(self, request, *args, **kwargs):
        return render(request, "login.html")

def index(request):
    print("Rendering login.html")
    return render(request, "login.html")

class ProtectedResourceView(View):
    def get(self, request, *args, **kwargs):
        # Verify the JWT token
        payload = verify_jwt_token(request)
        
        # If the token is invalid, the function will return a JsonResponse with error
        if isinstance(payload, JsonResponse):
            return payload

        return JsonResponse({"message": "Protected resource accessed", "user": payload['username']})
    
    
class LoanApplicationView(View):
    def post(self, request):
        try:
            # Retrieve the JWT token from cookies
            token = request.COOKIES.get('jwt_token')
            if not token:
                return JsonResponse({"error": "Token is missing"}, status=400)

            # Decode the JWT token and extract the username
            try:
                user_data = decode_jwt_token(token)
                username = user_data.get("username")
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=401)

            # Fetch the user from DynamoDB using the username
            user = get_user_from_dynamodb(username)
            if not user:
                return JsonResponse({"error": "User not found"}, status=404)

            # Parse the JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))

            # Extract data from the parsed JSON
            monthly_income = int(data.get("monthly_income"))
            monthly_expenses = int(data.get("monthly_expenses"))
            loan_amount = int(data.get("loan_amount"))
            loan_duration = int(data.get("loan_duration"))

            # Calculate the credit score and classify the application
            credit_score = self.calculate_credit_score(monthly_income, monthly_expenses, loan_amount, loan_duration)
            application_status = self.classify_application(credit_score)

            # Save the loan application linked to the user
            loan_application = save_loan_application(
                user=user,
                monthly_income=monthly_income,
                monthly_expenses=monthly_expenses,
                loan_amount=loan_amount,
                loan_duration=loan_duration,
                credit_score=credit_score,
                application_status=application_status
            )

            # Return a JsonResponse with the results
            return JsonResponse({
                "credit_score": credit_score,
                "application_status": application_status,
                "loan_application_id": loan_application.id
            })

        except Exception as e:
            # Return an error message if parsing fails
            return JsonResponse({"error": str(e)}, status=400)

    # eliminarrrr -------------------
    # substituir pelo workflow
    def calculate_credit_score(self, monthly_income, monthly_expenses, loan_amount, loan_duration):
        """
        Simplified formula for credit score calculation.
        """
        score = 100
        expense_ratio = (monthly_expenses / monthly_income) * 100
        score -= expense_ratio

        loan_risk = loan_amount / (monthly_income * loan_duration) * 100
        score -= loan_risk

        return max(0, min(int(score), 100))

    # substituir pelo workflow
    def classify_application(self, credit_score):
        """
        Classify loan application based on the credit score.
        """
        if credit_score >= 70:
            return "Accepted"
        elif credit_score >= 40:
            return "Interview"
        else:
            return "Rejected"