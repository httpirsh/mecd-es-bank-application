from django.urls import path, include
from rest_framework import routers
from .views import LoginView, LoanSimulationView, LoanApplicationView, LoanApplicationViewSet
from . import views

# define the router path and viewset to be used
router = routers.DefaultRouter()
router.register(r'', LoanApplicationViewSet)

urlpatterns = [
    path('simulator/', LoanSimulationView.as_view(), name="Loan simulator"),
    path('login/', LoginView.as_view(), name="login"),
    path('loan-application/', LoanApplicationView.as_view(), name="Loan Application"),
    path('applications/', include(router.urls))
]