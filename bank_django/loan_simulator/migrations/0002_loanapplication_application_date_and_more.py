# Generated by Django 4.2.17 on 2024-12-19 13:30

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("loan_simulator", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="loanapplication",
            name="application_date",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="loanapplication",
            name="loan_details",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="loan_simulator.loandetails",
            ),
        ),
        migrations.AddField(
            model_name="loanapplication",
            name="loan_simulation",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="loan_simulator.loansimulation",
            ),
        ),
        migrations.AddField(
            model_name="loanapplication",
            name="monthly_expenses",
            field=models.IntegerField(default=500, verbose_name="Monthly expenses (€)"),
        ),
        migrations.AddField(
            model_name="loandetails",
            name="loan_simulation",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="loan_simulator.loansimulation",
            ),
        ),
        migrations.AlterField(
            model_name="loanapplication",
            name="monthly_income",
            field=models.IntegerField(default=2000, verbose_name="Monthly income (€)"),
        ),
        migrations.AlterField(
            model_name="loandetails",
            name="interest_rate",
            field=models.FloatField(default=5.0, verbose_name="Interest rate (%)"),
        ),
        migrations.AlterField(
            model_name="loandetails",
            name="monthly_payment",
            field=models.IntegerField(default=0, verbose_name="Monthly payment (€)"),
        ),
        migrations.AlterField(
            model_name="loandetails",
            name="total_repayment",
            field=models.FloatField(default=0.0, verbose_name="Total repayment"),
        ),
        migrations.AlterField(
            model_name="loansimulation",
            name="amount",
            field=models.IntegerField(default=1000, verbose_name="Amount (€)"),
        ),
        migrations.AlterField(
            model_name="loansimulation",
            name="desired_monthly_payment",
            field=models.IntegerField(
                blank=True,
                default=100,
                null=True,
                verbose_name="Desired monthly payment (€)",
            ),
        ),
        migrations.AlterField(
            model_name="loansimulation",
            name="duration",
            field=models.IntegerField(
                blank=True, default=12, null=True, verbose_name="Duration (months)"
            ),
        ),
    ]
