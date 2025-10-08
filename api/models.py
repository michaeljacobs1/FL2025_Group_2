from django.contrib.auth.models import User
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=120)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class PersonalInformation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ], blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class IncomeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.IntegerField()
    income_amount = models.DecimalField(max_digits=12, decimal_places=2)
    income_source = models.CharField(max_length=100, default="Salary")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'year']
        ordering = ['year']

    def __str__(self):
        return f"{self.user.username} - {self.year}: ${self.income_amount}"


class FinancialProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_savings_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage", blank=True, null=True)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    monthly_expenses = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    current_savings = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    investment_goals = models.TextField(blank=True)
    retirement_goals = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Financial Profile"


class ProjectionScenario(models.Model):
    SCENARIO_TYPES = [
        ('conservative', 'Conservative'),
        ('moderate', 'Moderate'),
        ('aggressive', 'Aggressive'),
        ('custom', 'Custom'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    scenario_type = models.CharField(max_length=20, choices=SCENARIO_TYPES, default='moderate')
    annual_return_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Expected annual return percentage")
    inflation_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Expected inflation rate percentage")
    risk_tolerance = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.scenario_type})"


class ProjectionResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scenario = models.ForeignKey(ProjectionScenario, on_delete=models.CASCADE, null=True, blank=True)
    total_invested = models.DecimalField(max_digits=12, decimal_places=2)
    projected_years = models.IntegerField()
    projected_valuation = models.DecimalField(max_digits=12, decimal_places=2)
    annual_return_rate = models.DecimalField(max_digits=5, decimal_places=2)
    inflation_rate = models.DecimalField(max_digits=5, decimal_places=2)
    income_ratio = models.DecimalField(max_digits=5, decimal_places=2)
    investment_ratio = models.DecimalField(max_digits=5, decimal_places=2)
    property_ratio = models.DecimalField(max_digits=5, decimal_places=2)
    real_estate_ratio = models.DecimalField(max_digits=5, decimal_places=2)
    liabilities_ratio = models.DecimalField(max_digits=5, decimal_places=2)
    net_worth = models.DecimalField(max_digits=12, decimal_places=2)
    monthly_contribution = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_contributions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_gains = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Projection for {self.projected_years} years"

    @property
    def return_on_investment(self):
        if self.total_contributions > 0:
            return ((self.projected_valuation - self.total_contributions) / self.total_contributions) * 100
        return 0


class ProjectionYearlyData(models.Model):
    projection = models.ForeignKey(ProjectionResult, on_delete=models.CASCADE, related_name='yearly_data')
    year = models.IntegerField()
    beginning_balance = models.DecimalField(max_digits=12, decimal_places=2)
    contributions = models.DecimalField(max_digits=12, decimal_places=2)
    gains = models.DecimalField(max_digits=12, decimal_places=2)
    ending_balance = models.DecimalField(max_digits=12, decimal_places=2)
    inflation_adjusted_balance = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ['year']
        unique_together = ['projection', 'year']

    def __str__(self):
        return f"{self.projection.user.username} - Year {self.year}: ${self.ending_balance}"
