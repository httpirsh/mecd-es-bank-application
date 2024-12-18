from django.urls import path
from .views import LoginView
from . import views

urlpatterns = [
    path("simulator/", views.index, name="Loan simulator"),
    path('login/', LoginView.as_view(), name='login'), 
]