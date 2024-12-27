from django.test import TestCase
from django.utils import timezone
from api.models import LoanApplication, LoanEvaluation

class LoanApplicationTestCase(TestCase):
	def setUp(self):
		self.application = LoanApplication.objects.create(
			username = "test_user",
			amount = 10000, 
			duration = 36,
    		desired_monthly_payment = None,
			monthly_income = 2000, 
			monthly_expenses = 1000, 

			credit_score = 10,
			application_status = "accept",
		)

		LoanEvaluation.objects.create(
			application = self.application,
			notes = "Test annotation.",
		    officer = "test officer",
		)

	def test_auto_fields_are_set(self):
		application = LoanApplication.objects.get(id=self.application.id)
		evaluation = LoanEvaluation.objects.get(application=application)
		self.assertEqual(evaluation.status, "unevaluated")
		self.assertLessEqual(evaluation.created, timezone.now())
		self.assertLessEqual(evaluation.updated, timezone.now())
