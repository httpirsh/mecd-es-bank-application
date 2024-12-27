import boto3
from django.core.management.base import BaseCommand

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Reference the 'users' table
table = dynamodb.Table('Users')

class Command(BaseCommand):
    help = 'Adds test users (customers and bank employees) to DynamoDB'

    def handle(self, *args, **kwargs):
        # Add a customer
        add_user_to_dynamodb(
            username='iris',
            email='iris@example.com',
            phone='1234567890',
            user_type='customer',
        )

        # Add a bank employee
        add_user_to_dynamodb(
            username='helder',
            email='helder@bank.com',
            phone='0987654321',
            user_type='employee',
        )

def add_user_to_dynamodb(username, email, phone, user_type, face_id = None):
    """
    Add a customer or employee to the DynamoDB table.
    """
    try:
        # Add the user to the DynamoDB table
        response = table.put_item(
            Item={
                'username': username,
                'email': email,
                'phone': phone,
                'user_type': user_type,  # 'customer' or 'employee'
                'face_id': face_id,
            }
        )
        print(f"{username} added: {response}")
    except Exception as e:
        print(f"Failed to add {username}: {e}")
