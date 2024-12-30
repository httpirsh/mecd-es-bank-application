from django.urls import path
from .views import SubmittedApplicationsView, EvaluateApplicationView, InEvaluationListView

urlpatterns = [
    path('applications/', SubmittedApplicationsView.as_view(), name='applications'),
    path('evaluations/<int:application_id>/', EvaluateApplicationView.as_view(), name='evaluations'),
    path('in_evaluation/', InEvaluationListView.as_view(), name='in_evaluation'),
]