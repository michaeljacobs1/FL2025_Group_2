"""
Advanced Financial Projection Service
Provides comprehensive financial projection calculations with multiple scenarios
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from .models import (
    FinancialProfile,
    IncomeEntry,
    ProjectionResult,
    ProjectionScenario,
    ProjectionYearlyData,
)


class ProjectionCalculator:
    """Advanced financial projection calculator with multiple scenarios"""

    def __init__(self, user):
        self.user = user
        self.financial_profile = None
        self.income_entries = None
        self._load_user_data()

    def _load_user_data(self):
        """Load user's financial data"""
        try:
            self.financial_profile = FinancialProfile.objects.get(user=self.user)
        except FinancialProfile.DoesNotExist:
            self.financial_profile = None

        self.income_entries = IncomeEntry.objects.filter(user=self.user).order_by(
            "year"
        )

    def create_default_scenarios(self):
        """Create default projection scenarios for the user"""
        scenarios = [
            {
                "name": "Conservative Growth",
                "scenario_type": "conservative",
                "annual_return_rate": 4.0,
                "inflation_rate": 2.5,
                "risk_tolerance": "low",
            },
            {
                "name": "Moderate Growth",
                "scenario_type": "moderate",
                "annual_return_rate": 7.0,
                "inflation_rate": 3.0,
                "risk_tolerance": "medium",
            },
            {
                "name": "Aggressive Growth",
                "scenario_type": "aggressive",
                "annual_return_rate": 10.0,
                "inflation_rate": 3.5,
                "risk_tolerance": "high",
            },
        ]

        created_scenarios = []
        for scenario_data in scenarios:
            scenario, created = ProjectionScenario.objects.get_or_create(
                user=self.user, name=scenario_data["name"], defaults=scenario_data
            )
            if created:
                created_scenarios.append(scenario)

        return created_scenarios

    def calculate_projection(
        self, scenario_id: int, projected_years: int
    ) -> ProjectionResult:
        """Calculate comprehensive financial projection"""
        try:
            scenario = ProjectionScenario.objects.get(id=scenario_id, user=self.user)
        except ProjectionScenario.DoesNotExist:
            raise ValueError("Invalid scenario ID")

        if not self.financial_profile:
            raise ValueError("Financial profile not found")

        # Calculate monthly savings
        monthly_income = self.financial_profile.monthly_income or Decimal("0")
        monthly_expenses = self.financial_profile.monthly_expenses or Decimal("0")
        monthly_savings = monthly_income - monthly_expenses

        # Calculate annual savings
        annual_savings = monthly_savings * 12

        # Get current savings
        current_savings = self.financial_profile.current_savings or Decimal("0")

        # Calculate projection
        yearly_data = self._calculate_yearly_projection(
            current_savings,
            annual_savings,
            projected_years,
            scenario.annual_return_rate,
            scenario.inflation_rate,
        )

        # Calculate totals
        total_contributions = current_savings + (annual_savings * projected_years)
        projected_valuation = yearly_data[-1]["ending_balance"]
        total_gains = projected_valuation - total_contributions

        # Calculate asset allocation ratios (simplified)
        ratios = self._calculate_asset_allocation_ratios(scenario.scenario_type)

        # Create projection result
        projection = ProjectionResult.objects.create(
            user=self.user,
            scenario=scenario,
            total_invested=total_contributions,
            projected_years=projected_years,
            projected_valuation=projected_valuation,
            annual_return_rate=scenario.annual_return_rate,
            inflation_rate=scenario.inflation_rate,
            income_ratio=ratios["income_ratio"],
            investment_ratio=ratios["investment_ratio"],
            property_ratio=ratios["property_ratio"],
            real_estate_ratio=ratios["real_estate_ratio"],
            liabilities_ratio=ratios["liabilities_ratio"],
            net_worth=projected_valuation,
            monthly_contribution=monthly_savings,
            total_contributions=total_contributions,
            total_gains=total_gains,
        )

        # Create yearly data
        for year_data in yearly_data:
            ProjectionYearlyData.objects.create(
                projection=projection,
                year=year_data["year"],
                beginning_balance=year_data["beginning_balance"],
                contributions=year_data["contributions"],
                gains=year_data["gains"],
                ending_balance=year_data["ending_balance"],
                inflation_adjusted_balance=year_data["inflation_adjusted_balance"],
            )

        return projection

    def _calculate_yearly_projection(
        self,
        initial_balance: Decimal,
        annual_contribution: Decimal,
        years: int,
        return_rate: Decimal,
        inflation_rate: Decimal,
    ) -> List[Dict]:
        """Calculate year-by-year projection"""
        yearly_data = []
        current_balance = initial_balance
        current_year = datetime.now().year

        for year in range(1, years + 1):
            beginning_balance = current_balance

            # Add annual contribution
            contributions = annual_contribution
            current_balance += contributions

            # Calculate gains on the balance (including new contributions)
            gains = current_balance * (return_rate / 100)
            current_balance += gains

            # Calculate inflation-adjusted balance
            inflation_factor = (1 + inflation_rate / 100) ** year
            inflation_adjusted_balance = current_balance / Decimal(
                str(inflation_factor)
            )

            yearly_data.append(
                {
                    "year": current_year + year,
                    "beginning_balance": beginning_balance,
                    "contributions": contributions,
                    "gains": gains,
                    "ending_balance": current_balance,
                    "inflation_adjusted_balance": inflation_adjusted_balance,
                }
            )

        return yearly_data

    def _calculate_asset_allocation_ratios(
        self, scenario_type: str
    ) -> Dict[str, Decimal]:
        """Calculate asset allocation ratios based on scenario type"""
        if scenario_type == "conservative":
            return {
                "income_ratio": Decimal("100.0"),
                "investment_ratio": Decimal("40.0"),
                "property_ratio": Decimal("30.0"),
                "real_estate_ratio": Decimal("20.0"),
                "liabilities_ratio": Decimal("10.0"),
            }
        elif scenario_type == "aggressive":
            return {
                "income_ratio": Decimal("100.0"),
                "investment_ratio": Decimal("80.0"),
                "property_ratio": Decimal("10.0"),
                "real_estate_ratio": Decimal("5.0"),
                "liabilities_ratio": Decimal("5.0"),
            }
        else:  # moderate
            return {
                "income_ratio": Decimal("100.0"),
                "investment_ratio": Decimal("60.0"),
                "property_ratio": Decimal("20.0"),
                "real_estate_ratio": Decimal("15.0"),
                "liabilities_ratio": Decimal("5.0"),
            }

    def get_projection_summary(self, projection_id: int) -> Dict:
        """Get comprehensive projection summary"""
        try:
            projection = ProjectionResult.objects.get(id=projection_id, user=self.user)
        except ProjectionResult.DoesNotExist:
            raise ValueError("Projection not found")

        yearly_data = projection.yearly_data.all()

        return {
            "projection": projection,
            "yearly_data": yearly_data,
            "summary": {
                "total_contributions": projection.total_contributions,
                "total_gains": projection.total_gains,
                "projected_valuation": projection.projected_valuation,
                "return_on_investment": projection.return_on_investment,
                "monthly_contribution": projection.monthly_contribution,
                "annual_return_rate": projection.annual_return_rate,
                "inflation_rate": projection.inflation_rate,
            },
        }

    def compare_scenarios(
        self, scenario_ids: List[int], projected_years: int
    ) -> List[Dict]:
        """Compare multiple projection scenarios"""
        comparisons = []

        for scenario_id in scenario_ids:
            try:
                projection = self.calculate_projection(scenario_id, projected_years)
                summary = self.get_projection_summary(projection.id)
                comparisons.append(
                    {
                        "scenario": projection.scenario,
                        "projection": projection,
                        "summary": summary["summary"],
                    }
                )
            except ValueError as e:
                print(f"Error calculating projection for scenario {scenario_id}: {e}")

        return comparisons


class DataGenerator:
    """Generate sample data for testing and demonstration"""

    @staticmethod
    def generate_sample_financial_profile(user, profile_data=None):
        """Generate sample financial profile data"""
        if not profile_data:
            profile_data = {
                "current_savings_rate": Decimal("15.0"),
                "monthly_income": Decimal("5000.00"),
                "monthly_expenses": Decimal("3500.00"),
                "current_savings": Decimal("25000.00"),
                "investment_goals": "Build emergency fund and invest for retirement",
                "retirement_goals": "Retire at 65 with $1M+ in savings",
            }

        profile, created = FinancialProfile.objects.get_or_create(
            user=user, defaults=profile_data
        )

        if not created:
            for key, value in profile_data.items():
                setattr(profile, key, value)
            profile.save()

        return profile

    @staticmethod
    def generate_sample_income_entries(user, years_back=5):
        """Generate sample income timeline data"""
        current_year = datetime.now().year

        for i in range(years_back):
            year = current_year - years_back + i + 1
            base_income = Decimal("45000.00") + (Decimal("5000.00") * i)

            IncomeEntry.objects.get_or_create(
                user=user,
                year=year,
                defaults={"income_amount": base_income, "income_source": "Salary"},
            )

    @staticmethod
    def generate_sample_projections(user):
        """Generate sample projection scenarios and results"""
        calculator = ProjectionCalculator(user)

        # Create default scenarios
        scenarios = calculator.create_default_scenarios()

        # Generate projections for each scenario
        projections = []
        for scenario in scenarios:
            try:
                projection = calculator.calculate_projection(scenario.id, 10)
                projections.append(projection)
            except Exception as e:
                print(f"Error generating projection for {scenario.name}: {e}")

        return projections
