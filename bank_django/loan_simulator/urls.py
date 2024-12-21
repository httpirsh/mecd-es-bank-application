from django.urls import path
from .views import LoginView, LoanSimulationView
from . import views

urlpatterns = [
    path("simulator/", LoanSimulationView.as_view(), name="Loan simulator"),
    path('login/', LoginView.as_view(), name='login'), 
]