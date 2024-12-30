from django.urls import path, include
from rest_framework import routers
from .views import LoginView, LoanSimulationView, LoanApplicationViewSet, LoanEvaluationViewSet
from . import views

# define the router path and viewset to be used
router = routers.DefaultRouter()
router.register(r'', LoanApplicationViewSet)

other = routers.DefaultRouter()
other.register(r'', LoanEvaluationViewSet)


urlpatterns = [
    path('simulator/', LoanSimulationView.as_view(), name="Loan simulator"),
    path('login/', LoginView.as_view(), name="login"),
    path('applications/', include(router.urls), name="Loan applications rest api"),
    path('evaluations/', include(other.urls), name="Loan applications rest api")

]