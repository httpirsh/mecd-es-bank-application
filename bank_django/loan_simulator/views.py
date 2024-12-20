from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .models import LoanSimulation, LoanDetails, User
from django.contrib.auth import login
from django.conf import settings
import base64
import os
import boto3
import json

# Initialize Rekognition and DynamoDB clients
rekognition_client = boto3.client('rekognition', region_name=os.environ.get("AWS_DEFAULT_REGION"))
dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
print(f"DynamoDB client initialized: {dynamodb}")

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
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return JsonResponse({"error": "Error decoding image"}, status=400)

        try:
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
                    login(request, user)
                    return JsonResponse({"success": True, "message": "Login successful"})
                else:
                    return JsonResponse({"error": "Face not recognized"}, status=401)
            else:
                return JsonResponse({"error": "No matching face found"}, status=401)

        except Exception as e:
            return JsonResponse({"error": f"Rekognition error: {str(e)}"}, status=500)
        
    def get_user_by_face_id(self, face_id):
        """
        Recovers the Django dynamoDB user based on face_id. 
        """
        try:
            dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
            table = dynamodb.Table(settings.AWS_DYNAMO_TABLE_NAME)
            print(f"Table initialized: {table}")

            response = table.get_item(Key={'face_id': face_id})
            print(f"Response from DynamoDB: {response}")

            if 'Item' in response:
                print(f"User found: {response['Item']}")
                user_data = response['Item']
                return user_data 
            else:
                print("User not found in DynamoDB.")
                return None
        except Exception as e:
            print(f"Error retrieving user from DynamoDB: {e}")
            return None
            
def index(request):
    return render(request, "login.html")
