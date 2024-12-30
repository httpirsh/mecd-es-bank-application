from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth.models import User
from django.utils import timezone
from django import forms
from datetime import timedelta
from api.models import LoanApplication, LoanEvaluation
from django.contrib.auth.mixins import LoginRequiredMixin
import boto3
from django.conf import settings
from datetime import datetime

# Página de boas-vindas (sem login necessário)
def welcome_page(request):
    return render(request, 'welcomePage.html')

# Função de login simulada
def manager_login(request):
    if request.method == 'POST':
        # Obter nome de usuário e senha do formulário
        username = request.POST['username']
        password = request.POST['password']
        
        # Cria um usuário fictício ou recupera o existente
        user, created = User.objects.get_or_create(username=username)
        
        # Simula a configuração da senha (não será verificada, apenas para fins de navegação)
        if created:
            user.set_password(password)  # Apenas configura a senha para garantir
            user.save()

        # Realiza o login fictício
        auth_login(request, user)

        # Redireciona para a página inicial (home)
        return redirect('home')  # Substitua 'home' pelo nome correto da URL para a homePage
        
    return render(request, 'login.html')

# Página inicial após login
@login_required
def home_page(request):
    return render(request, 'homePage.html')


class LoanRequestsListView(LoginRequiredMixin, ListView):
    model = LoanApplication
    template_name = 'loanRequestsList.html'
    context_object_name = 'loans'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_date = timezone.now()

        # Filtrar empréstimos atuais
        current_loans = LoanApplication.objects.filter(
            created__gte=current_date - timedelta(days=2),
            loanevaluation__isnull=True
        ).order_by('created')

        # Filtrar empréstimos passados
        past_loans = LoanApplication.objects.filter(
            created__lt=current_date - timedelta(days=2),
            loanevaluation__isnull=True
        ).order_by('created')

        # Adicionar as listas de empréstimos atuais e passados ao contexto
        context['current_loans'] = current_loans
        context['past_loans'] = past_loans

        return context


class LoanEvaluationForm(forms.Form):
    STATUS_CHOICES = [
        ('accept', 'Accepted'),
        ('reject', 'Rejected'),
        ('interview', 'Interview'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES)
    timeslots = forms.CharField(required=False, widget=forms.HiddenInput)  # Vamos armazenar os timeslots selecionados aqui

class LoanEvaluationView(LoginRequiredMixin, DetailView, FormView):
    model = LoanApplication
    template_name = 'loanEvaluation.html'
    context_object_name = 'loan'
    form_class = LoanEvaluationForm

    def get_object(self):
        return get_object_or_404(LoanApplication, id=self.kwargs['loan_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        timeslots = self._get_available_timeslots()
        context['available_timeslots'] = timeslots
        return context

    def form_valid(self, form):
        loan = self.get_object()
        status = form.cleaned_data['status']
        timeslot_values = self.request.POST.getlist('timeslots')  # Obtém os timeslots selecionados

        # Criar ou obter a avaliação associada ao empréstimo
        evaluation, created = LoanEvaluation.objects.get_or_create(application=loan, officer=self.request.user.username)
        evaluation.status = status

        # Se o status for 'interview', associamos os timeslots selecionados
        if status == 'interview' and timeslot_values:
            evaluation.timeslots = '/ '.join(timeslot_values)  # Guarda os timeslots como uma string separada por vírgulas
        evaluation.save()


        # Se o status for 'interview', redireciona para a página de empréstimos aguardando entrevista
        if status == 'interview':
            return redirect('loan_waiting_interview')
        else: 
            self.send_sns_notification(loan)
            return redirect('loan_evaluated')

    def send_sns_notification(self, loan):
        sns = boto3.client('sns')
        # ARN do tópico SNS
        topic_arn = 'arn:aws:sns:us-east-1:211125598817:Notification'

        # Corpo da mensagem
        message = f"Olá {loan.username}, sua solicitação de empréstimo foi avaliada com o status: {loan.application_status}."

        # Enviar a mensagem SNS
        response = sns.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject="Avaliação de Empréstimo Concluída"
        )

    def _get_available_timeslots(self):
        # Simula slots de tempo disponíveis para entrevistas
        now = timezone.now()
        timeslots = [now + timedelta(hours=i) for i in range(1, 6)]
        return [{"formatted": slot.strftime('%Y-%m-%d %H:%M:%S'), "display": slot.strftime('%a, %b %d, %Y %H:%M')} for slot in timeslots]

class LoanEvaluatedView(LoginRequiredMixin, ListView):
    model = LoanEvaluation
    template_name = 'loanEvaluated.html'
    context_object_name = 'loan_evaluated'

    def get_queryset(self):
        return  LoanEvaluation.objects.exclude(status='interview')

        

class LoanWaitingInterviewView(LoginRequiredMixin, ListView):
    model = LoanEvaluation
    template_name = 'loanWaitingInterview.html'
    context_object_name = 'loan_waiting_interview'

    def get_queryset(self):
        return LoanEvaluation.objects.filter(status='interview')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        for loan in context['loan_waiting_interview']:
            if loan.timeslots:
                # Divide os timeslots em uma lista de strings
                timeslot_str_list = loan.timeslots.split("/ ")
                
                # Converte as strings para objetos datetime
                loan.timeslot_list = [
                    datetime.strptime(timeslot_str, "%Y-%m-%d %H:%M:%S") 
                    for timeslot_str in timeslot_str_list
                ]
            else:
                loan.timeslot_list = []

        return context 
        

    def post(self, request, *args, **kwargs):
        # Verifique se o usuário tem permissão para alterar o status
        if not request.user.is_authenticated:
            return ValueError("You are not allowed to do this.")
        
        loan_id = request.POST.get('loan_id')
        action = request.POST.get('action')

        if not loan_id or action not in ['accept', 'reject']:
            return ValueError("Invalid action.")

        # Obtenha o empréstimo com base no ID
        loan_evaluation = get_object_or_404(LoanEvaluation, pk=loan_id)

        # Verifique se o empréstimo está no status 'interview'
        if loan_evaluation.status != 'interview':
            return ValueError("Loan is not in interview status.")

        # Atualize o status de acordo com o botão pressionado
        loan_evaluation.status = action
        loan_evaluation.save()
        self.send_sns_notification_eval(loan_evaluation)
        
        # Redirecione de volta para a página de empréstimos aguardando entrevista
        return redirect('loan_waiting_interview')  # Certifique-se de que a URL esteja correta
    
    def send_sns_notification_eval(self, loan_evaluation):
        sns = boto3.client('sns')
        # ARN do tópico SNS
        topic_arn = 'arn:aws:sns:us-east-1:211125598817:Notification'

        # Obtendo informações necessárias do empréstimo
        loan = loan_evaluation.application
        message = f"Olá {loan.username}, sua solicitação de empréstimo foi avaliada com o status: {loan_evaluation.status}."

        # Enviar a mensagem SNS
        sns.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject="Avaliação de Empréstimo Concluída"
        )
        

  
    
