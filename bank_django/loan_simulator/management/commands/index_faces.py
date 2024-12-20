import boto3
import os
from django.core.management.base import BaseCommand
from loan_simulator.models import User  # Importe o modelo User

class Command(BaseCommand):
    help = 'Indexes images from S3 into AWS Rekognition collection.'

    def handle(self, *args, **options):
        # Fetch AWS credentials and region from the environment
        bucketname = os.environ['AWS_BUCKET_NAME']
        collection_name = os.environ['AWS_COLLECTION_NAME']

        # Initialize S3 and Rekognition clients
        region = os.environ['AWS_DEFAULT_REGION']
        s3 = boto3.resource('s3', region_name=region)
        rekognition_client = boto3.client('rekognition', region_name=region)

        # Create or verify Rekognition collection
        try:
            response = rekognition_client.create_collection(CollectionId=collection_name)
            self.stdout.write(self.style.SUCCESS(f'Collection {collection_name} created: {response}'))
        except rekognition_client.exceptions.ResourceAlreadyExistsException:
            self.stdout.write(self.style.WARNING(f'Collection {collection_name} already exists.'))

        # Index faces in the bucket
        my_bucket = s3.Bucket(bucketname)
        for my_bucket_object in my_bucket.objects.filter(Prefix="toindex/", Delimiter="/"):
            filename = my_bucket_object.key.split('/')[-1]
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    # Call Rekognition to index the face
                    response = rekognition_client.index_faces(
                        CollectionId=collection_name,
                        Image={
                            'S3Object': {
                                'Bucket': my_bucket_object.bucket_name,
                                'Name': my_bucket_object.key
                            }
                        },
                        ExternalImageId=filename,  # Use the filename as an ID or other identifier
                        DetectionAttributes=['ALL']
                    )

                    # Print the indexed face information
                    self.stdout.write(self.style.SUCCESS(f"Indexed: {my_bucket_object.key}, Response: {response}"))
                    
                    # Retrieve the face ID from the response
                    for face_record in response['FaceRecords']:
                        face_id = face_record['Face']['FaceId']
                        self.stdout.write(self.style.SUCCESS(f"Filename: {filename}, Face ID: {face_id}"))

                        # Optionally, you can print or log the face_id for further processing
                        
                        # Assuming the filename corresponds to the user's name)
                        username = filename.split('.')[0]  # Remove file extension
                        
                        # Find the user by name (username)
                        try:
                            self.stdout.write(self.style.NOTICE(f"Searching for user {username} in dynamo..."))
                            user = User.get(username)
                            user.face_id = face_id  # Assign the Rekognition face_id to the user
                            user.save()  # Save the user object with the updated face_id
                            self.stdout.write(self.style.SUCCESS(f"Updated user {user.username} with face_id {face_id}"))
                        except User.DoesNotExist:
                            self.stdout.write(self.style.ERROR(f"User with name {username} not found"))
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to index {my_bucket_object.key}: {e}"))
