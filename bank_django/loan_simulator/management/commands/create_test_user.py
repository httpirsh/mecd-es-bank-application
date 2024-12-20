import boto3
from django.core.management.base import BaseCommand

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Reference the 'users' table
table = dynamodb.Table('Users')

def add_user_to_dynamodb(face_id, name, email, phone, user_type):
    """
    Add a customer or employee to the DynamoDB table.
    """
    try:
        # Add the user to the DynamoDB table
        response = table.put_item(
            Item={
                'face_id': face_id,
                'name': name,
                'email': email,
                'phone': phone,
                'user_type': user_type  # 'customer' or 'employee'
            }
        )
        print(f"{user_type.capitalize()} added: {response}")
    except Exception as e:
        print(f"Failed to add {user_type}: {e}")


class Command(BaseCommand):
    help = 'Adds test users (customers and bank employees) to DynamoDB'

    def handle(self, *args, **kwargs):
        # Add a customer
        add_user_to_dynamodb(
            face_id='52137f89-0220-4eca-b36f-69def37f8c10',  # Face ID for the 'iris.jpg' image
            name='iris',
            email='iris@example.com',
            phone='1234567890',
            user_type='customer'
        )

        # Add a bank employee
        add_user_to_dynamodb(
            face_id='ea0e4b24-06d0-4803-8551-09cd4b97a473',  # Face ID for the 'helder.jpeg' image
            name='helder',
            email='helder@bank.com',
            phone='0987654321',
            user_type='employee'
        )
