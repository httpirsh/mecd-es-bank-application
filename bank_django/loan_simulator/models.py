import boto3
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class LoanSimulation(models.Model):
    amount = models.IntegerField("Amount (€)", default=1000) 
    duration = models.IntegerField("Duration (months)", null=True, blank=True, default=12)
    desired_monthly_payment = models.IntegerField("Desired monthly payment (€)", null=True, blank=True, default=100)

    def clean(self):
        super().clean()
        if self.duration and self.desired_monthly_payment:
            raise ValidationError("You can only set 'duration' or 'desired_monthly_payment', not both.")
        if not self.duration and not self.desired_monthly_payment:
            raise ValidationError("You must set either 'duration' or 'desired_monthly_payment'.")

    def get_interest_rate(self, loan_amount, loan_duration):
        """
        Calculate the interest rate based on loan amount and duration.
        """
        if loan_amount <= 10000:
            return 5.0 if loan_duration <= 12 else 5.5
        elif loan_amount <= 20000:
            return 4.5 if loan_duration <= 12 else 5.0
        else:
            return 4.0

    def calculate_loan_details(self, loan_amount, loan_duration):
        """
        Calculate total repayment and monthly installment for the loan.
        """
        interest_rate = self.get_interest_rate(loan_amount, loan_duration)
        total_repayment = loan_amount * (1 + (interest_rate / 100) * (loan_duration / 12))
        monthly_installment = total_repayment / loan_duration

        return {
            "interest_rate": interest_rate,
            "total_repayment": round(total_repayment, 2),
            "monthly_installment": round(monthly_installment, 2),
        }

class LoanDetails(models.Model):
    loan_simulation = models.ForeignKey(LoanSimulation, on_delete=models.CASCADE, default=1)
    interest_rate = models.FloatField("Interest rate (%)", default=5.0)
    total_repayment = models.FloatField("Total repayment", default=0.0)
    monthly_payment = models.IntegerField("Monthly payment (€)", default=0)

    def calculate_and_save_details(self):
        # Use the LoanSimulation instance to calculate the details
        loan_simulation = self.loan_simulation
        result = loan_simulation.calculate_loan_details(loan_simulation.amount, loan_simulation.duration)
        
        self.interest_rate = result["interest_rate"]
        self.total_repayment = result["total_repayment"]
        self.monthly_payment = result["monthly_installment"]
        
        self.save()

    def __str__(self):
        return f"LoanDetails for {self.loan_simulation.amount}€"

class LoanApplication(models.Model):
    loan_simulation = models.ForeignKey(LoanSimulation, on_delete=models.CASCADE, default=1)
    loan_details = models.ForeignKey(LoanDetails, on_delete=models.CASCADE, null=True, blank=True)

    monthly_income = models.IntegerField("Monthly income (€)", default=2000)
    monthly_expenses = models.IntegerField("Monthly expenses (€)", default=500)
    application_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Loan Application for {self.loan_simulation.amount}€"
    

class User(models.Model):
    face_id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    class Meta:
        db_table = 'User'

    def __str__(self):
        return f"User {self.name} ({self.face_id})"




