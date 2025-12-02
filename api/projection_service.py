"""
Advanced Financial Projection Service
Provides comprehensive financial projection calculations with multiple scenarios
"""

import math
import random
import statistics
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from .historical_data import HistoricalData
from .models import (
    FinancialProfile,
    IncomeEntry,
    MonteCarloIteration,
    MonteCarloSimulation,
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


class MonteCarloService:
    """Monte Carlo simulation service for investment projections"""

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

        # Load year-by-year income entries
        self.income_entries = IncomeEntry.objects.filter(user=self.user).order_by(
            "year"
        )

    def _get_default_std_dev(
        self, return_rate: Decimal, risk_tolerance: str
    ) -> Decimal:
        """Get default standard deviation based on return rate and risk tolerance"""
        # Base volatility: higher returns typically have higher volatility
        # Conservative: ~8-12% std dev, Moderate: ~12-16%, Aggressive: ~16-20%
        base_volatility_map = {
            "low": Decimal("10.0"),
            "medium": Decimal("14.0"),
            "high": Decimal("18.0"),
        }

        # Scale based on return rate (higher returns = higher volatility)
        base_vol = base_volatility_map.get(risk_tolerance, Decimal("14.0"))
        return base_vol

    def run_simulation(
        self,
        scenario_id: Optional[int] = None,
        projected_years: int = 30,
        number_of_iterations: int = 1000,
        base_return_rate: Optional[Decimal] = None,
        return_rate_std_dev: Optional[Decimal] = None,
        base_inflation_rate: Optional[Decimal] = None,
        inflation_rate_std_dev: Optional[Decimal] = None,
        target_goal: Optional[Decimal] = None,
        store_iterations: bool = False,
        use_bootstrap: bool = True,
        use_recent_data: bool = True,
        recent_data_years: int = 50,
    ) -> MonteCarloSimulation:
        """
        Run Monte Carlo simulation with random variations in returns and inflation.
        Uses historical data bootstrap by default for more realistic projections.

        Args:
            scenario_id: Optional scenario ID to use as base parameters
            projected_years: Number of years to project
            number_of_iterations: Number of Monte Carlo iterations (1000-10000 recommended)
            base_return_rate: Expected annual return rate (overrides scenario)
            return_rate_std_dev: Standard deviation of returns (overrides scenario-based default)
            base_inflation_rate: Expected inflation rate (overrides scenario)
            inflation_rate_std_dev: Standard deviation of inflation (default: 1.0)
            target_goal: Optional target goal amount for success rate calculation
            store_iterations: Whether to store individual iteration results (can be large)
            use_bootstrap: If True, use historical data bootstrap; if False, use normal distribution
            use_recent_data: If True (and use_bootstrap=True), use only recent historical data
            recent_data_years: Number of recent years to use for bootstrap (default: 50)

        Returns:
            MonteCarloSimulation instance with statistical results
        """
        if not self.financial_profile:
            raise ValueError("Financial profile not found")

        # Get base parameters from scenario or use provided values
        scenario = None
        if scenario_id:
            try:
                scenario = ProjectionScenario.objects.get(
                    id=scenario_id, user=self.user
                )
                if base_return_rate is None:
                    base_return_rate = scenario.annual_return_rate
                if base_inflation_rate is None:
                    base_inflation_rate = scenario.inflation_rate
                if return_rate_std_dev is None:
                    return_rate_std_dev = self._get_default_std_dev(
                        base_return_rate, scenario.risk_tolerance
                    )
            except ProjectionScenario.DoesNotExist:
                raise ValueError("Invalid scenario ID")

        if base_return_rate is None:
            raise ValueError(
                "base_return_rate must be provided or scenario must be specified"
            )
        if base_inflation_rate is None:
            base_inflation_rate = Decimal("3.0")  # Default 3% inflation
        if return_rate_std_dev is None:
            return_rate_std_dev = Decimal("14.0")  # Default 14% std dev
        if inflation_rate_std_dev is None:
            inflation_rate_std_dev = Decimal("1.0")  # Default 1% std dev for inflation

        # Get starting savings
        current_savings = self.financial_profile.current_savings or Decimal("0")

        # Calculate year-by-year contributions from IncomeEntry if available
        # Otherwise fall back to FinancialProfile monthly data
        # Returns tuple of (contributions list, base_year for inflation adjustments)
        yearly_contributions, base_year_for_inflation = self._get_yearly_contributions(
            projected_years
        )

        # Run Monte Carlo iterations
        final_values = []
        iterations_data = []  # Store if needed

        for iteration_num in range(1, number_of_iterations + 1):
            # Generate random return and inflation rates for each year
            if use_bootstrap:
                # Use empirical bootstrap from historical data
                # Sample returns from historical stock market data
                historical_returns = HistoricalData.bootstrap_sample_return(
                    n=projected_years,
                    use_recent=use_recent_data,
                    recent_years=recent_data_years,
                )

                # Adjust historical returns to match target mean if specified
                if base_return_rate is not None:
                    target_mean = float(base_return_rate)
                    historical_returns = HistoricalData.adjust_returns_for_risk(
                        historical_returns, target_mean
                    )

                yearly_returns = [Decimal(str(r)) for r in historical_returns]

                # Sample inflation from historical data
                historical_inflation = HistoricalData.bootstrap_sample_inflation(
                    n=projected_years,
                    use_recent=use_recent_data,
                    recent_years=recent_data_years,
                )

                # Adjust historical inflation to match target mean if specified
                if base_inflation_rate is not None:
                    target_inf_mean = float(base_inflation_rate)
                    historical_mean = HistoricalData.get_mean_inflation(
                        use_recent=use_recent_data, recent_years=recent_data_years
                    )
                    shift = target_inf_mean - historical_mean
                    historical_inflation = [inf + shift for inf in historical_inflation]

                yearly_inflation = [Decimal(str(i)) for i in historical_inflation]
            else:
                # Use normal distribution (original method)
                yearly_returns = []
                yearly_inflation = []

                for year in range(projected_years):
                    # Generate normally distributed return rate
                    return_rate = self._generate_normal_random(
                        float(base_return_rate), float(return_rate_std_dev)
                    )
                    # Clamp to reasonable bounds (-50% to +50%)
                    return_rate = max(-50.0, min(50.0, return_rate))
                    yearly_returns.append(Decimal(str(return_rate)))

                    # Generate normally distributed inflation rate
                    inflation_rate = self._generate_normal_random(
                        float(base_inflation_rate), float(inflation_rate_std_dev)
                    )
                    # Clamp to reasonable bounds (0% to 15%)
                    inflation_rate = max(0.0, min(15.0, inflation_rate))
                    yearly_inflation.append(Decimal(str(inflation_rate)))

            # Run projection with these random rates
            final_value, total_contributions, avg_return, avg_inflation = (
                self._run_single_iteration(
                    current_savings,
                    yearly_contributions,
                    projected_years,
                    yearly_returns,
                    yearly_inflation,
                    base_year_for_inflation,
                )
            )

            final_values.append(float(final_value))

            if store_iterations:
                iterations_data.append(
                    {
                        "iteration_number": iteration_num,
                        "final_value": final_value,
                        "total_contributions": total_contributions,
                        "total_gains": final_value - total_contributions,
                        "avg_return_rate": avg_return,
                        "avg_inflation_rate": avg_inflation,
                    }
                )

        # Calculate statistics from actual bootstrap results
        # All percentiles and statistics come from actual final_values (real bootstrap results)
        # Calculate statistics from actual bootstrap results
        # All percentiles and statistics come from actual final_values (real bootstrap results)
        final_values_sorted = sorted(final_values)
        mean_value = Decimal(str(statistics.mean(final_values)))
        median_value = Decimal(str(statistics.median(final_values)))
        std_dev_value = Decimal(
            str(statistics.stdev(final_values) if len(final_values) > 1 else 0)
        )
        min_value = Decimal(str(min(final_values)))
        max_value = Decimal(str(max(final_values)))

        # Calculate percentiles
        percentile_5 = Decimal(
            str(final_values_sorted[int(len(final_values_sorted) * 0.05)])
        )
        percentile_25 = Decimal(
            str(final_values_sorted[int(len(final_values_sorted) * 0.25)])
        )
        percentile_75 = Decimal(
            str(final_values_sorted[int(len(final_values_sorted) * 0.75)])
        )
        percentile_95 = Decimal(
            str(final_values_sorted[int(len(final_values_sorted) * 0.95)])
        )

        # Calculate success rate if target goal provided
        success_rate = None
        if target_goal:
            successes = sum(1 for v in final_values if v >= float(target_goal))
            success_rate = Decimal(str((successes / len(final_values)) * 100))

        # Create simulation record
        simulation = MonteCarloSimulation.objects.create(
            user=self.user,
            scenario=scenario,
            number_of_iterations=number_of_iterations,
            projected_years=projected_years,
            base_return_rate=base_return_rate,
            return_rate_std_dev=return_rate_std_dev,
            base_inflation_rate=base_inflation_rate,
            inflation_rate_std_dev=inflation_rate_std_dev,
            mean_final_value=mean_value,
            median_final_value=median_value,
            std_dev_final_value=std_dev_value,
            min_final_value=min_value,
            max_final_value=max_value,
            percentile_5=percentile_5,
            percentile_25=percentile_25,
            percentile_75=percentile_75,
            percentile_95=percentile_95,
            success_rate=success_rate,
            target_goal=target_goal,
        )

        # Store individual iterations
        # For bootstrap simulations, ALWAYS store final values for accurate visualization
        # This ensures the histogram shows actual bootstrap results
        max_iterations_to_store = 10000  # Reasonable limit to avoid database bloat

        if store_iterations:
            # Store full iteration data if requested
            for iter_data in iterations_data:
                if iter_data["iteration_number"] <= max_iterations_to_store:
                    MonteCarloIteration.objects.create(
                        simulation=simulation,
                        iteration_number=iter_data["iteration_number"],
                        final_value=iter_data["final_value"],
                        total_contributions=iter_data["total_contributions"],
                        total_gains=iter_data["total_gains"],
                        avg_return_rate=iter_data["avg_return_rate"],
                        avg_inflation_rate=iter_data["avg_inflation_rate"],
                    )
        elif use_bootstrap and number_of_iterations <= max_iterations_to_store:
            # For bootstrap simulations, automatically store final values (not full iteration data)
            # This enables accurate histogram visualization based on actual bootstrap results
            for idx, final_val in enumerate(final_values):
                if idx < max_iterations_to_store:
                    MonteCarloIteration.objects.create(
                        simulation=simulation,
                        iteration_number=idx + 1,
                        final_value=Decimal(str(final_val)),
                        total_contributions=Decimal(
                            "0"
                        ),  # Minimal data, just final values
                        total_gains=Decimal("0"),
                        avg_return_rate=Decimal("0"),
                        avg_inflation_rate=Decimal("0"),
                    )

        return simulation

    def _generate_normal_random(self, mean: float, std_dev: float) -> float:
        """Generate a random number from normal distribution using Box-Muller transform"""
        # Box-Muller transform for normal distribution
        u1 = random.random()
        u2 = random.random()
        # Avoid log(0)
        while u1 == 0.0:
            u1 = random.random()
        z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        return mean + std_dev * z0

    def _get_yearly_contributions(self, projected_years: int) -> tuple:
        """
        Get year-by-year contribution amounts based on IncomeEntry data or FinancialProfile.

        Returns:
            Tuple of (contributions list, base_year_for_inflation)
            - contributions: list of annual contributions for each projected year
            - base_year_for_inflation: the year index from which to start applying inflation adjustments
        """
        from datetime import datetime

        current_year = datetime.now().year
        contributions = []
        base_year_for_inflation = None

        # Check if we have IncomeEntry data
        if self.income_entries.exists():
            # Create a dictionary of year -> income entry for quick lookup
            entries_dict = {entry.year: entry for entry in self.income_entries}

            # Get the range of years we have data for
            entry_years = sorted([entry.year for entry in self.income_entries])
            if entry_years:
                min_year = min(entry_years)
                max_year = max(entry_years)

                # Calculate contributions for each projected year
                for year_offset in range(projected_years):
                    projection_year = current_year + year_offset

                    # Try to find exact match first
                    if projection_year in entries_dict:
                        entry = entries_dict[projection_year]
                        # Use after_tax_income if available, otherwise income_amount
                        income = (
                            entry.after_tax_income
                            or entry.income_amount
                            or Decimal("0")
                        )
                        costs = entry.costs or Decimal("0")
                        contribution = income - costs
                        contributions.append(contribution)
                        # Track the last year offset where we have actual IncomeEntry data
                        if (
                            base_year_for_inflation is None
                            or year_offset > base_year_for_inflation
                        ):
                            base_year_for_inflation = year_offset

                    # If year is before our data, use first year's data
                    elif projection_year < min_year:
                        entry = entries_dict[min_year]
                        income = (
                            entry.after_tax_income
                            or entry.income_amount
                            or Decimal("0")
                        )
                        costs = entry.costs or Decimal("0")
                        contribution = income - costs
                        contributions.append(contribution)

                    # If year is after our data, use last year's data
                    # (will be adjusted for inflation in the iteration loop)
                    else:  # projection_year > max_year
                        entry = entries_dict[max_year]
                        income = (
                            entry.after_tax_income
                            or entry.income_amount
                            or Decimal("0")
                        )
                        costs = entry.costs or Decimal("0")
                        contribution = income - costs
                        contributions.append(contribution)
                        # Set base year for inflation if not set (this is the last year with actual data)
                        if base_year_for_inflation is None:
                            # Find the year offset for max_year
                            base_year_for_inflation = max_year - current_year
                # If we have actual data, use the last actual data year as base for inflation
                if base_year_for_inflation is None:
                    base_year_for_inflation = 0
            else:
                # No entry years, use monthly data
                monthly_income = self.financial_profile.monthly_income or Decimal("0")
                monthly_expenses = self.financial_profile.monthly_expenses or Decimal(
                    "0"
                )
                monthly_savings = monthly_income - monthly_expenses
                annual_savings = monthly_savings * 12
                contributions = [annual_savings] * projected_years
                base_year_for_inflation = 0
        else:
            # No IncomeEntry data, use FinancialProfile monthly data
            monthly_income = self.financial_profile.monthly_income or Decimal("0")
            monthly_expenses = self.financial_profile.monthly_expenses or Decimal("0")
            monthly_savings = monthly_income - monthly_expenses
            annual_savings = monthly_savings * 12
            contributions = [annual_savings] * projected_years
            base_year_for_inflation = 0

        return contributions, base_year_for_inflation

    def _run_single_iteration(
        self,
        initial_balance: Decimal,
        yearly_contributions: List[Decimal],
        years: int,
        yearly_returns: List[Decimal],
        yearly_inflation: List[Decimal],
        base_year_for_inflation: int = 0,
    ) -> tuple:
        """
        Run a single iteration of the projection with specific return rates and year-by-year contributions.

        Inflation affects contributions: for years beyond the base_year_for_inflation (which has actual data),
        contributions are adjusted for inflation to maintain real purchasing power.

        Args:
            initial_balance: Starting portfolio balance
            yearly_contributions: List of annual contribution amounts for each year
            years: Number of years to project
            yearly_returns: List of return rates for each year
            yearly_inflation: List of inflation rates for each year
            base_year_for_inflation: Year index from which to start applying inflation adjustments

        Returns:
            Tuple of (final_value, total_contributions, avg_return_rate, avg_inflation_rate)
        """
        current_balance = initial_balance
        total_contributions = initial_balance

        # Calculate average rates for this iteration
        avg_return = sum(yearly_returns) / len(yearly_returns)
        avg_inflation = sum(yearly_inflation) / len(yearly_inflation)

        for year_idx in range(years):
            # Get the base contribution for this year
            base_contribution = (
                yearly_contributions[year_idx]
                if year_idx < len(yearly_contributions)
                else yearly_contributions[-1]
                if yearly_contributions
                else Decimal("0")
            )

            # Only apply inflation adjustment for years beyond the base year (which has actual IncomeEntry data)
            if year_idx > base_year_for_inflation:
                # Calculate cumulative inflation from base year to this year
                cumulative_inflation = Decimal("1")
                for prev_year_idx in range(base_year_for_inflation, year_idx):
                    inflation_rate = (
                        yearly_inflation[prev_year_idx]
                        if prev_year_idx < len(yearly_inflation)
                        else yearly_inflation[-1]
                    )
                    cumulative_inflation *= Decimal("1") + inflation_rate / Decimal(
                        "100"
                    )

                adjusted_contribution = base_contribution * cumulative_inflation
            else:
                # Use contribution as-is (it's already in nominal dollars for that year from IncomeEntry)
                adjusted_contribution = base_contribution

            # Add annual contribution
            current_balance += adjusted_contribution
            total_contributions += adjusted_contribution

            # Apply return for this year (nominal return)
            return_rate = (
                yearly_returns[year_idx]
                if year_idx < len(yearly_returns)
                else yearly_returns[-1]
            )
            gains = current_balance * (return_rate / 100)
            current_balance += gains

        return current_balance, total_contributions, avg_return, avg_inflation
