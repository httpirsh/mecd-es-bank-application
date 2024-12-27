from django.test import TestCase
from django.core.exceptions import ValidationError

from api.models import LoanSimulation

class LoanSimulationTests(TestCase):

    def test_desired_monthly_payment(self):
        """
        Loan with 'amount' and 'desired_monthly_payment'.
        """
        monthly_loan = LoanSimulation(
            amount=10000,
            desired_monthly_payment=10,
        )
        monthly_loan.full_clean()

    def test_duration(self):
        """
        Loan with 'amount' and 'duration'.
        """
        duration_loan = LoanSimulation(
            amount=10000,
            duration=36,
        )
        duration_loan.full_clean()

    def test_cannot_set_monthly_and_duration(self):
        """
        Loan can only set 'duration' or 'desired_monthly_payment', not both.
        """
        loan = LoanSimulation(
            amount=10000,
            duration=36, 
            desired_monthly_payment=10,
        )
        with self.assertRaises(ValidationError) :
            loan.full_clean()

    def test_must_set_monthly_or_duration(self):
        """
        Loan cannot have 'duration' and 'desired_monthly_payment' empty.
        """
        loan = LoanSimulation(
            amount=1000,
        )
        with self.assertRaises(ValidationError):
            loan.full_clean()