from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from api.models import LoanApplication, LoanEvaluation
from django.views import View
from django.views.generic import ListView
from datetime import datetime

class SubmittedApplicationsView(ListView):
    model = LoanApplication
    template_name = "appplications.html"  # Defina um template apropriado
    context_object_name = "applications"

    def get_queryset(self):
        queryset = LoanApplication.objects.filter(loanevaluation__isnull=True).order_by("created")
        return queryset



class EvaluateApplicationView(View):
    def get(self, request, application_id):
        # Verificar se o oficial está autenticado
        officer = self._auth_officer(request)
        
        # Obter ou criar uma avaliação para a aplicação
        evaluation = self._get_or_create_evaluation(application_id, officer)

        # Gerar uma lista de slots de tempo disponíveis
        available_timeslots = self._get_available_timeslots()
        
        # Passar para o contexto da página
        context = {
            'evaluation': evaluation,
            'available_timeslots': available_timeslots,
        }
        return render(request, 'evaluate.html', context)

    def post(self, request, application_id):
        officer = self._auth_officer(request)
        evaluation = self._get_or_create_evaluation(application_id, officer)

        # Processar o formulário de avaliação
        evaluation.status = request.POST.get('status')
        evaluation.notes = request.POST.get('notes')

        # Se o status for 'interview' ou 'pending', permitir selecionar um timeslot
        if evaluation.status in ['interview', 'pending']:
            timeslot = request.POST.get('timeslot')
            if timeslot:
                evaluation.timeslot = datetime.strptime(timeslot, '%Y-%m-%d %H:%M:%S')
        
        evaluation.save()

        # Redirecionar para a lista de aplicações
        return redirect('applications')

    def _auth_officer(self, request):
        # Placeholder para autenticação do oficial
        return "iris-officer"

    def _get_or_create_evaluation(self, application_id, officer):
        try:
            application = LoanApplication.objects.get(id=application_id)
        except LoanApplication.DoesNotExist:
            raise ValueError(f"LoanApplication with ID {application_id} does not exist.")
        
        evaluation, created = LoanEvaluation.objects.get_or_create(
            application=application,
            defaults={"officer": officer}
        )
        return evaluation

    def _get_available_timeslots(self):
        # Simula slots de tempo disponíveis para entrevistas
        from datetime import datetime, timedelta
        now = datetime.now()
        return [now + timedelta(hours=i) for i in range(1, 6)]

    
class InEvaluationListView(ListView):
    model = LoanEvaluation
    template_name = "in_evalutation.html"  # Defina um template apropriado
    context_object_name = "in_evaluation"

    def get_queryset(self):
        return LoanEvaluation.objects.filter(status__in=["unevaluated", "interview"])

