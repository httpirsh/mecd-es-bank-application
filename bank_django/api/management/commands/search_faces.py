from django.core.management.base import BaseCommand
import boto3
import os

class Command(BaseCommand):
    help = 'Searches faces in AWS Rekognition collection using images from S3.'

    def handle(self, *args, **options):
        # Fetch AWS credentials and region from the environment
        bucketname = os.environ['AWS_BUCKET_NAME']
        collection_name = os.environ['AWS_COLLECTION_NAME']

        # Initialize S3 and Rekognition clients
        s3 = boto3.resource('s3', region_name=os.environ['AWS_DEFAULT_REGION'])
        client = boto3.client('rekognition', region_name=os.environ['AWS_DEFAULT_REGION'])

        # Search faces in the bucket
        my_bucket = s3.Bucket(bucketname)
        for obj in my_bucket.objects.filter(Prefix="toselect/"):
            if obj.key.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    response = client.search_faces_by_image(
                        CollectionId=collection_name,
                        Image={'S3Object': {'Bucket': bucketname, 'Name': obj.key}}
                    )
                    # Process the response as needed
                    self.stdout.write(self.style.SUCCESS(f"Processed image: {obj.key}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing image {obj.key}: {e}"))
