from rest_framework import serializers

from .models import LoanApplication

class LoanApplicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LoanApplication
        fields = ('id','username','monthly_income','monthly_expenses','amount','duration','desired_monthly_payment','credit_score','application_status','created')