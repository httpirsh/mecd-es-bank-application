from django.db import models
from django.core.exceptions import ValidationError

class LoanSimulation(models.Model):
    amount = models.IntegerField("Amount (€)")
    duration = models.IntegerField("Duration (months)", null=True, blank=True)
    desired_monthly_payment = models.IntegerField("Desired monthly payment (€)", null=True, blank=True)

    def clean(self):
        super().clean()
        if self.duration and self.desired_monthly_payment:
            raise ValidationError("You can only set 'duration' or 'desired_monthly_payment', not both.")
        if not self.duration and not self.desired_monthly_payment:
            raise ValidationError("You must set either 'duration' or 'desired_monthly_payment'.")
           
class LoanDetails(models.Model):
    #loan_simulation = models.ForeignKey(LoanSimulation)
    interest_rate = models.FloatField("Interest rate (%)")
    total_repayment = models.FloatField("Total repayment")
    monthly_payment = models.IntegerField("Monthly payment (€)")

class LoanApplication(models.Model):
    monthly_income = models.IntegerField("Monthly income (€)")
    monthly_expenses = models.IntegerField("Monthly expenses (€)")
