from django.shortcuts import render
from django.http import HttpResponse
from api.models import LoanApplication, LoanEvaluation

# /office/applications/
# List of submitted applications. No evaluation record yet.
def submitted_applications(request):
    applications_to_evaluate = LoanApplication.objects.filter(loanevaluation__isnull=True).order_by("created")
    output = ", ".join([app.__str__() for app in applications_to_evaluate])
    return HttpResponse(output)

# /office/evaluations/<application_id>/
# Create or update an evaluation for <application_id>
def evaluate(request, application_id):
    officer = _auth_officer(request)
    evaluation = _get_or_create_evaluation(application_id, officer)
    return HttpResponse("You're looking at application %s." % evaluation)

#/office/evaluations
def in_evaluation(request):
    evaluations = LoanEvaluation.objects.filter(status__in=["unevaluated", "interview"])
    output = ", ".join([e.__str__() for e in evaluations])
    return HttpResponse(output)

# Private methods to abstract the view from the models usage
# TODO: Move these methods to the model classes to improve cohesion
def _get_or_create_evaluation(application_id, officer):
    """
    Get the current evaluation for a given application.
    If the evaluation doesn't exist yet, creates a new one.
    """
    try:
        # Ensure the LoanApplication exists
        application = LoanApplication.objects.get(id=application_id)
    except LoanApplication.DoesNotExist:
        raise ValueError(f"LoanApplication with ID {application_id} does not exist.")
    
    # Use get_or_create for the evaluation
    evaluation, created = LoanEvaluation.objects.get_or_create(
        application=application,
        defaults={
            "officer": officer,
        }
    )
    
    if created:
        print(f"Created new LoanEvaluation for LoanApplication {application_id}.")
    else:
        print(f"LoanEvaluation for LoanApplication {application_id} already exists.")
    
    return evaluation

def _auth_officer(request):
    """
    Verify token and retrieve officer username
    TODO: implement using the token utils from api module.
    TODO: move this method to the utils module for better cohesion and reuse.
    """
    return "iris-officer"