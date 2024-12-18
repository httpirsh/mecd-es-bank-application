import boto3
import os
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Indexes images from S3 into AWS Rekognition collection.'

    def handle(self, *args, **options):
        # Fetch AWS credentials and region from the environment
        bucketname = os.environ['AWS_BUCKET_NAME']
        collection_name = os.environ['AWS_COLLECTION_NAME']

        # Initialize S3 and Rekognition clients
        s3 = boto3.resource('s3', region_name=os.environ['AWS_DEFAULT_REGION'])
        client = boto3.client('rekognition', region_name=os.environ['AWS_DEFAULT_REGION'])

        # Create or verify collection
        try:
            response = client.create_collection(CollectionId=collection_name)
            self.stdout.write(self.style.SUCCESS(f'Collection {collection_name} created: {response}'))
        except client.exceptions.ResourceAlreadyExistsException:
            self.stdout.write(self.style.WARNING(f'Collection {collection_name} already exists.'))

        # Index faces in the bucket
        my_bucket = s3.Bucket(bucketname)
        for my_bucket_object in my_bucket.objects.filter(Prefix="toindex/", Delimiter="/"):
            filename = my_bucket_object.key.split('/')[-1]
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    response = client.index_faces(CollectionId=collection_name,
                                                Image={
                                                    'S3Object': {
                                                        'Bucket': my_bucket_object.bucket_name,
                                                        'Name': my_bucket_object.key
                                                    }
                                                })
                    print(f"Indexed: {my_bucket_object.key}, Response: {response}")
                except Exception as e:
                    print(f"Failed to index {my_bucket_object.key}: {e}")