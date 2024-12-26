from datetime import datetime
from django.contrib import admin
from django.utils.html import format_html
from .models import LoanSimulation, LoanApplication, LoanDetails

admin.site.register(LoanSimulation)

class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'loan_amount', 'loan_duration', 'credit_score', 'application_status', 'interview_date', 'loan_officer')
    list_filter = ('application_status', 'loan_officer')
    search_fields = ('username',)
    
    fields = ('username', 'monthly_income', 'monthly_expenses', 'loan_amount', 'loan_duration', 'credit_score', 'application_status', 'interview_date', 'loan_officer')

    # Adding action for updating status
    actions = ['set_interview_date', 'assign_loan_officer', 'approve_loan', 'reject_loan']

    def set_interview_date(self, request, queryset):
        """Custom action to set interview date for selected loans"""
        for loan in queryset:
            loan.application_status = 'interview'
            loan.interview_date = datetime.now()  # For example, set to current date
            loan.save()
        self.message_user(request, "Interview date set successfully!")
    
    def assign_loan_officer(self, request, queryset):
        """Custom action to assign loan officer to selected loans"""
        for loan in queryset:
            loan.loan_officer = 'Loan Officer Name'  # Replace with actual loan officer name
            loan.save()
        self.message_user(request, "Loan officer assigned successfully!")

    def approve_loan(self, request, queryset):
        """Approve selected loans"""
        queryset.update(application_status='accept')
        self.message_user(request, "Selected loans have been approved!")

    def reject_loan(self, request, queryset):
        """Reject selected loans"""
        queryset.update(application_status='reject')
        self.message_user(request, "Selected loans have been rejected!")

    # You can add a custom link in the list view for viewing loan application details
    def view_details(self, obj):
        """Add a link to view loan details"""
        return format_html('<a href="/admin/loan_simulator/loanapplication/{}/change/">View</a>', obj.pk)

    view_details.short_description = 'View Details'

# Register the LoanApplication model
#admin.site.register(LoanApplication, LoanApplicationAdmin)

class LoanSimulationAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'duration', 'desired_monthly_payment')
    search_fields = ('amount',)

class LoanDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'interest_rate', 'total_repayment', 'monthly_payment', 'loan_simulation')
    search_fields = ('loan_simulation__amount',)

# Register models to the admin interface
#admin.site.register(LoanApplication, LoanApplicationAdmin)
#admin.site.register(LoanSimulation, LoanSimulationAdmin)
#admin.site.register(LoanDetails, LoanDetailsAdmin)