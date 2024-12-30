from django.urls import path
from .views import welcome_page, manager_login, home_page, LoanRequestsListView, LoanEvaluationView, LoanEvaluatedView, LoanWaitingInterviewView

urlpatterns = [
    path('', welcome_page, name='welcome_page'),  # Página inicial de boas-vindas
    path('login/', manager_login, name='login'),  # Página de login
    path('home/', home_page, name='home'),  # Página inicial após o login
    path('loan-requests-list/', LoanRequestsListView.as_view(), name='loan_requests_list'),  # Lista de empréstimos
    path('loan-evaluation/<int:loan_id>/', LoanEvaluationView.as_view(), name='loan_evaluation'),  # Avaliação do empréstimo
    path('loan-evaluated/', LoanEvaluatedView.as_view(), name='loan_evaluated'),  # Empréstimos avaliados
    path('loan-waiting-interview/', LoanWaitingInterviewView.as_view(), name='loan_waiting_interview'),  # Empréstimos aguardando entrevista
]
