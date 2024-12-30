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

from django.utils import timezone
from datetime import timedelta

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
    timeslot = forms.DateTimeField(required=False, widget=forms.SelectDateWidget)  # Timeslot só se for 'interview'

class LoanEvaluationView(LoginRequiredMixin, DetailView, FormView):
    model = LoanApplication
    template_name = 'loanEvaluation.html'
    context_object_name = 'loan'
    form_class = LoanEvaluationForm

    def get_object(self):
        return get_object_or_404(LoanApplication, id=self.kwargs['loan_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Gerar 5 timeslots de exemplo
        timeslots = self._get_available_timeslots()
        context['available_timeslots'] = timeslots

        return context

    def form_valid(self, form):
        loan = self.get_object()
        status = form.cleaned_data['status']
        timeslot = form.cleaned_data.get('timeslot')

        # Criar ou obter a avaliação associada ao empréstimo
        evaluation, created = LoanEvaluation.objects.get_or_create(application=loan, officer=self.request.user.username)
        evaluation.status = status
        
        # Se o status for 'interview', associamos um timeslot
        if status == 'interview' and timeslot:
            evaluation.timeslot = timeslot

        evaluation.save()

        # Se o status for 'interview', redireciona para a página de empréstimos aguardando entrevista
        if status == 'interview':
            return redirect('loan_waiting_interview')
        return redirect('loan_evaluated')

    def _get_available_timeslots(self):
        # Simula slots de tempo disponíveis para entrevistas
        now = timezone.now()
        return [now + timedelta(hours=i) for i in range(1, 6)]

class LoanEvaluatedView(LoginRequiredMixin, ListView):
    model = LoanEvaluation
    template_name = 'loanEvaluated.html'
    context_object_name = 'evaluated_loans'

    def get_queryset(self):
        return LoanEvaluation.objects.filter()

class LoanWaitingInterviewView(LoginRequiredMixin, ListView):
    model = LoanEvaluation
    template_name = 'loanWaitingInterview.html'
    context_object_name = 'waiting_loans'

    def get_queryset(self):
        return LoanEvaluation.objects.filter(status='interview')
