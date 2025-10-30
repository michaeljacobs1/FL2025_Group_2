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
    gender = models.CharField(
        max_length=10,
        choices=[
            ("M", "Male"),
            ("F", "Female"),
            ("O", "Other"),
        ],
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class IncomeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.IntegerField()
    income_amount = models.DecimalField(max_digits=12, decimal_places=2)
    income_source = models.CharField(max_length=100, default="Salary")
    costs = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Annual costs/expenses",
    )
    location = models.CharField(
        max_length=200, blank=True, null=True, help_text="Location for this year"
    )
    savings_rate = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "year"]
        ordering = ["year"]

    def __str__(self):
        return f"{self.user.username} - {self.year}: ${self.income_amount}"


class FinancialProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_savings_rate = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Percentage", blank=True, null=True
    )
    monthly_income = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    monthly_expenses = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    current_savings = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    investment_goals = models.TextField(blank=True)
    retirement_goals = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Financial Profile"


class ProjectionScenario(models.Model):
    SCENARIO_TYPES = [
        ("conservative", "Conservative"),
        ("moderate", "Moderate"),
        ("aggressive", "Aggressive"),
        ("custom", "Custom"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    scenario_type = models.CharField(
        max_length=20, choices=SCENARIO_TYPES, default="moderate"
    )
    annual_return_rate = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Expected annual return percentage"
    )
    inflation_rate = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Expected inflation rate percentage"
    )
    risk_tolerance = models.CharField(
        max_length=20,
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
        ],
        default="medium",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.scenario_type})"


class ProjectionResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scenario = models.ForeignKey(
        ProjectionScenario, on_delete=models.CASCADE, null=True, blank=True
    )
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
    monthly_contribution = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    total_contributions = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    total_gains = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Projection for {self.projected_years} years"

    @property
    def return_on_investment(self):
        if self.total_contributions > 0:
            return (
                (self.projected_valuation - self.total_contributions)
                / self.total_contributions
            ) * 100
        return 0


class ProjectionYearlyData(models.Model):
    projection = models.ForeignKey(
        ProjectionResult, on_delete=models.CASCADE, related_name="yearly_data"
    )
    year = models.IntegerField()
    beginning_balance = models.DecimalField(max_digits=12, decimal_places=2)
    contributions = models.DecimalField(max_digits=12, decimal_places=2)
    gains = models.DecimalField(max_digits=12, decimal_places=2)
    ending_balance = models.DecimalField(max_digits=12, decimal_places=2)
    inflation_adjusted_balance = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["year"]
        unique_together = ["projection", "year"]

    def __str__(self):
        return f"{self.projection.user.username} - Year {self.year}: ${self.ending_balance}"


class LocationPreference(models.Model):
    """User's location preferences with year ranges"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=200, help_text="City, State, Country")
    start_year = models.IntegerField(help_text="Starting year for this location")
    end_year = models.IntegerField(help_text="Ending year for this location")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_year"]

    def __str__(self):
        return f"{self.user.username} - {self.location} ({self.start_year}-{self.end_year})"


class SpendingPreference(models.Model):
    """User's spending preferences for different categories"""

    SPENDING_CHOICES = [
        ("very_little", "Very Little"),
        ("less_than_average", "Less Than Average"),
        ("average", "Average"),
        ("above_average", "Above Average"),
        ("very_high", "Very High"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    housing_spending = models.CharField(
        max_length=20, choices=SPENDING_CHOICES, default="average"
    )
    travel_spending = models.CharField(
        max_length=20, choices=SPENDING_CHOICES, default="average"
    )
    food_spending = models.CharField(
        max_length=20, choices=SPENDING_CHOICES, default="average"
    )
    leisure_spending = models.CharField(
        max_length=20, choices=SPENDING_CHOICES, default="average"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username} - Spending Preferences"


class AICostEstimate(models.Model):
    """AI-generated cost estimates for housing and family planning"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # User preferences
    desired_location = models.CharField(
        max_length=200, help_text="City, State, Country"
    )
    number_of_children = models.IntegerField(help_text="Desired number of children")
    house_size_sqft = models.IntegerField(help_text="Desired house size in square feet")
    house_type = models.CharField(
        max_length=50,
        choices=[
            ("single_family", "Single Family Home"),
            ("condo", "Condo/Apartment"),
            ("townhouse", "Townhouse"),
            ("multi_family", "Multi-Family Home"),
        ],
        default="single_family",
    )

    # AI-generated cost estimates
    estimated_home_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    estimated_monthly_mortgage = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    estimated_property_tax_annual = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    estimated_insurance_annual = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    estimated_utilities_monthly = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    estimated_maintenance_annual = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    # Child-related costs
    estimated_childcare_annual = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    estimated_education_annual = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    estimated_child_healthcare_annual = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    estimated_child_food_annual = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    estimated_child_clothing_annual = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    # Additional location-based costs
    estimated_transportation_annual = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    estimated_healthcare_annual = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    estimated_groceries_annual = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    # AI response metadata
    ai_response_raw = models.TextField(
        blank=True, help_text="Raw AI response for debugging"
    )
    ai_model_used = models.CharField(max_length=100, default="gpt-4")
    confidence_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="AI confidence score 0-1",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.desired_location} ({self.number_of_children} kids, {self.house_size_sqft} sqft)"

    @property
    def total_housing_costs_annual(self):
        """Calculate total annual housing costs"""
        if not all(
            [
                self.estimated_monthly_mortgage,
                self.estimated_property_tax_annual,
                self.estimated_insurance_annual,
                self.estimated_utilities_monthly,
                self.estimated_maintenance_annual,
            ]
        ):
            return None
        return (
            self.estimated_monthly_mortgage * 12
            + self.estimated_property_tax_annual
            + self.estimated_insurance_annual
            + self.estimated_utilities_monthly * 12
            + self.estimated_maintenance_annual
        )

    @property
    def total_child_costs_annual(self):
        """Calculate total annual child-related costs"""
        if not all(
            [
                self.estimated_childcare_annual,
                self.estimated_education_annual,
                self.estimated_child_healthcare_annual,
                self.estimated_child_food_annual,
                self.estimated_child_clothing_annual,
            ]
        ):
            return None
        return (
            self.estimated_childcare_annual
            + self.estimated_education_annual
            + self.estimated_child_healthcare_annual
            + self.estimated_child_food_annual
            + self.estimated_child_clothing_annual
        ) * self.number_of_children

    @property
    def total_lifestyle_costs_annual(self):
        """Calculate total annual lifestyle costs"""
        if not all(
            [
                self.estimated_transportation_annual,
                self.estimated_healthcare_annual,
                self.estimated_groceries_annual,
            ]
        ):
            return None
        return (
            self.estimated_transportation_annual
            + self.estimated_healthcare_annual
            + self.estimated_groceries_annual
        )
