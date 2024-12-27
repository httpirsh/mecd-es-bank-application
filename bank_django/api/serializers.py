from rest_framework import serializers
from django.core.exceptions import ValidationError

from .models import LoanApplication, LoanEvaluation

class LoanApplicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LoanApplication
        fields = ('id','username','monthly_income','monthly_expenses','amount','duration','desired_monthly_payment','credit_score','application_status','created')

    def validate(self, data):
        # Apply the model's clean method to ensure all validations and calculations are performed
        loan_application = LoanApplication(**data)  # Create an instance without saving it
        try:
            loan_application.clean()  # Calls the model's clean method
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)  # Raise the validation error if any

        # If clean() passes, return the validated data
        return data
    
class LoanEvaluationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LoanEvaluation
        fields = ('application', 'notes', 'status', 'officer', 'created', 'updated')