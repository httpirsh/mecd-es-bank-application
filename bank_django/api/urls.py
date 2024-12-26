from django.urls import path
from .views import LoginView, LoanSimulationView, LoanApplicationView
from . import views

urlpatterns = [
    path('simulator/', LoanSimulationView.as_view(), name="Loan simulator"),
    path('login/', LoginView.as_view(), name='login'),
    #path('facialLogin/', views.index, name="Facial login form")
    path('loan-application/', LoanApplicationView.as_view(), name="Loan Application")
]