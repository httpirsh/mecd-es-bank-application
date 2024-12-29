from django.urls import path

from . import views

urlpatterns = [
    path("applications/", views.submitted_applications, name="Index for applications."),
    path("evaluations/<int:application_id>/", views.evaluate, name="Evaluate application."),
    path("evaluations/", views.in_evaluation, name="Index of applications to schedule interview.")
]