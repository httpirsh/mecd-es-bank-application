from datetime import datetime
from django.contrib import admin
from django.utils.html import format_html
from .models import LoanApplication, LoanEvaluation

admin.site.register(LoanApplication)
admin.site.register(LoanEvaluation)