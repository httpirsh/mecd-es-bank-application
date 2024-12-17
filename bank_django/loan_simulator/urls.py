from django.urls import path

from . import views

urlpatterns = [
    path("simulator/", views.index, name="Loan simulator"),
]