from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
import base64
import os
import boto3
import json

# Initialize AWS Rekognition and DynamoDB clients
rekognition_client = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')

#@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        image_data = data.get('image')
        if not image_data:
            return JsonResponse({"error": "Image file is required"}, status=400)

        # Decode the Base64 image data
        image_bytes = base64.b64decode(image_data)

        try:
            response = rekognition_client.search_faces_by_image(
                CollectionId=os.getenv('AWS_COLLECTION_NAME'),
                Image={'Bytes': image_bytes},
                MaxFaces=1
            )
        except Exception as e:
            return JsonResponse({"error": f"Rekognition error: {str(e)}"}, status=500)

        if not response['FaceMatches']:
            return JsonResponse({"error": "Face not recognized"}, status=401)

        face_id = response['FaceMatches'][0]['Face']['FaceId']
        return JsonResponse({"success": True, "face_id": face_id}, status=200)
    
# Create your views here.

def index(request):
    return render(request, "login.html")