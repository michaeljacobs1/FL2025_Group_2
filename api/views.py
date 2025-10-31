from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView
from rest_framework import permissions, viewsets

from .models import (
    AICostEstimate,
    FinancialProfile,
    IncomeEntry,
    LocationPreference,
    PersonalInformation,
    Post,
    ProjectionResult,
    ProjectionScenario,
    ProjectionYearlyData,
    SpendingPreference,
)
from .projection_service import ProjectionCalculator
from .serializers import (
    AICostEstimateSerializer,
    FinancialProfileSerializer,
    IncomeEntrySerializer,
    PersonalInformationSerializer,
    PostSerializer,
    ProjectionResultSerializer,
    ProjectionScenarioSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]


class FinancialProfileViewSet(viewsets.ModelViewSet):
    queryset = FinancialProfile.objects.all()
    serializer_class = FinancialProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FinancialProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProjectionScenarioViewSet(viewsets.ModelViewSet):
    queryset = ProjectionScenario.objects.all()
    serializer_class = ProjectionScenarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProjectionScenario.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProjectionResultViewSet(viewsets.ModelViewSet):
    queryset = ProjectionResult.objects.all()
    serializer_class = ProjectionResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProjectionResult.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IncomeEntryViewSet(viewsets.ModelViewSet):
    queryset = IncomeEntry.objects.all()
    serializer_class = IncomeEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return IncomeEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PersonalInformationViewSet(viewsets.ModelViewSet):
    queryset = PersonalInformation.objects.all()
    serializer_class = PersonalInformationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PersonalInformation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")


class FinancialDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "financial/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        personal_info, created = PersonalInformation.objects.get_or_create(user=user)
        context["personal_info"] = personal_info

        financial_profile, created = FinancialProfile.objects.get_or_create(user=user)
        context["financial_profile"] = financial_profile

        try:
            context["recent_projections"] = (
                ProjectionResult.objects.filter(user=user)
                .only(
                    "id",
                    "total_invested",
                    "projected_years",
                    "projected_valuation",
                    "income_ratio",
                    "investment_ratio",
                    "property_ratio",
                    "real_estate_ratio",
                    "liabilities_ratio",
                    "net_worth",
                    "created_at",
                )
                .order_by("-created_at")[:3]
            )
        except Exception as e:
            print(f"Error loading projections: {e}")
            context["recent_projections"] = []

        try:
            context["scenarios"] = ProjectionScenario.objects.filter(user=user)
        except Exception:
            context["scenarios"] = []

        try:
            context["income_entries"] = IncomeEntry.objects.filter(user=user).order_by(
                "-year"
            )[:5]
        except Exception:
            context["income_entries"] = []

        return context


class PersonalInformationView(LoginRequiredMixin, View):
    template_name = "financial/personal_info.html"

    def get(self, request):
        personal_info, created = PersonalInformation.objects.get_or_create(
            user=request.user
        )
        return render(request, self.template_name, {"personal_info": personal_info})

    def post(self, request):
        personal_info, created = PersonalInformation.objects.get_or_create(
            user=request.user
        )

        personal_info.name = request.POST.get("name", "") or None
        personal_info.address = request.POST.get("address", "") or None
        personal_info.phone = request.POST.get("phone", "") or None
        personal_info.email = request.POST.get("email", "") or None

        date_of_birth = request.POST.get("date_of_birth", "")
        personal_info.date_of_birth = date_of_birth if date_of_birth else None

        gender = request.POST.get("gender", "")
        personal_info.gender = gender if gender else None

        personal_info.save()

        messages.success(request, "Personal information updated successfully!")
        return redirect("personal_info")


class FinancialInformationView(LoginRequiredMixin, View):
    template_name = "financial/financial_info_new.html"

    def get(self, request):
        financial_profile, created = FinancialProfile.objects.get_or_create(
            user=request.user
        )
        income_entries = IncomeEntry.objects.filter(user=request.user).order_by("year")

        # Load existing location and spending preferences if they exist
        location_preferences = LocationPreference.objects.filter(
            user=request.user
        ).order_by("start_year")

        spending_preference = SpendingPreference.objects.filter(
            user=request.user
        ).first()

        # Determine if user has any saved data
        has_saved_data = income_entries.exists() or location_preferences.exists()

        # Extract income parameters from existing entries if they exist
        income_data = None
        if income_entries.exists():
            entries_list = list(income_entries)
            if len(entries_list) > 0:
                start_year = entries_list[0].year
                end_year = entries_list[-1].year
                total_years = end_year - start_year + 1
                starting_income = float(entries_list[0].income_amount)

                # Calculate growth rate by comparing first and last year
                if len(entries_list) > 1:
                    ending_income = float(entries_list[-1].income_amount)
                    # Calculate CAGR (Compound Annual Growth Rate)
                    if starting_income > 0 and total_years > 1:
                        growth_rate = (
                            (ending_income / starting_income)
                            ** (1.0 / (total_years - 1))
                            - 1
                        ) * 100
                    else:
                        growth_rate = 0.0
                else:
                    growth_rate = 0.0

                income_data = {
                    "startYear": start_year,
                    "totalYears": total_years,
                    "startingIncome": starting_income,
                    "growthRate": growth_rate,
                }

        # Prepare location data for template
        saved_locations = []
        if location_preferences.exists():
            for loc in location_preferences:
                # Parse state and area level from location label format "State (area level)"
                location_label = loc.location
                if " (" in location_label and location_label.endswith(")"):
                    state = location_label.split(" (")[0]
                    area_level = location_label.split(" (")[1].rstrip(")")
                    saved_locations.append(
                        {
                            "state": state,
                            "areaLevel": area_level.replace(" ", "_"),
                            "startYear": loc.start_year,
                            "endYear": loc.end_year,
                        }
                    )
                else:
                    # Fallback if format is different
                    saved_locations.append(
                        {
                            "state": location_label,
                            "areaLevel": "average",
                            "startYear": loc.start_year,
                            "endYear": loc.end_year,
                        }
                    )

        return render(
            request,
            self.template_name,
            {
                "financial_profile": financial_profile,
                "income_entries": income_entries,
                "income_data": income_data,
                "location_preferences": saved_locations,
                "spending_preference": spending_preference,
                "has_saved_data": has_saved_data,
            },
        )

    def post(self, request):
        # Check if this is a generate results request
        if request.POST.get("generate_results") == "1":
            return self._handle_generate_results(request)

        # Check if this is an update entries request
        if request.POST.get("update_entries") == "1":
            return self._handle_update_entries(request)

        # Check if this is a save projection request
        if request.POST.get("save_projection") == "1":
            return self._handle_save_projection(request)

        # Check if this is an AI cost generation request
        if request.POST.get("generate_ai_costs") == "1":
            return self._handle_ai_cost_generation(request)

        mode = request.POST.get("income_mode", "")

        if mode == "by_year":
            years = request.POST.getlist("year[]")
            incomes = request.POST.getlist("income[]")
            rates = request.POST.getlist("savings_rate_year[]")
            keep_years = []

            const_flag = request.POST.get("use_constant_rate", "")
            const_rate_val = request.POST.get("constant_rate_value", "")

            for i in range(len(years)):
                y = years[i].strip() if i < len(years) else ""
                inc = incomes[i].strip() if i < len(incomes) else ""
                rate = rates[i].strip() if i < len(rates) else ""
                if not y or not inc:
                    continue
                year_i = int(y)
                keep_years.append(year_i)

                final_rate = None
                if const_flag and const_rate_val:
                    final_rate = Decimal(const_rate_val)
                elif rate:
                    final_rate = Decimal(rate)

                IncomeEntry.objects.update_or_create(
                    user=request.user,
                    year=year_i,
                    defaults={
                        "income_amount": Decimal(inc),
                        "income_source": "Salary",
                        "savings_rate": final_rate,
                    },
                )

            if keep_years:
                (
                    IncomeEntry.objects.filter(user=request.user)
                    .exclude(year__in=keep_years)
                    .delete()
                )

            calculator = ProjectionCalculator(request.user)
            if not ProjectionScenario.objects.filter(user=request.user).exists():
                calculator.create_default_scenarios()
            default_scenario = ProjectionScenario.objects.filter(
                user=request.user
            ).first()
            if default_scenario:
                try:
                    calculator.calculate_projection(
                        default_scenario.id,
                        projected_years=len(keep_years) if keep_years else 1,
                    )
                except Exception:
                    pass

            return redirect("results")

        financial_profile, created = FinancialProfile.objects.get_or_create(
            user=request.user
        )

        savings_rate = request.POST.get("savings_rate", "")
        financial_profile.current_savings_rate = (
            Decimal(savings_rate) if savings_rate else None
        )

        monthly_income = request.POST.get("monthly_income", "")
        financial_profile.monthly_income = (
            Decimal(monthly_income) if monthly_income else None
        )

        monthly_expenses = request.POST.get("monthly_expenses", "")
        financial_profile.monthly_expenses = (
            Decimal(monthly_expenses) if monthly_expenses else None
        )

        current_savings = request.POST.get("current_savings", "")
        financial_profile.current_savings = (
            Decimal(current_savings) if current_savings else None
        )

        financial_profile.investment_goals = request.POST.get("investment_goals", "")
        financial_profile.retirement_goals = request.POST.get("retirement_goals", "")
        financial_profile.save()

        calculator = ProjectionCalculator(request.user)
        if not ProjectionScenario.objects.filter(user=request.user).exists():
            calculator.create_default_scenarios()
        default_scenario = ProjectionScenario.objects.filter(user=request.user).first()
        if default_scenario:
            try:
                years_from_income = IncomeEntry.objects.filter(
                    user=request.user
                ).count()
                calculator.calculate_projection(
                    default_scenario.id, projected_years=years_from_income or 10
                )
            except Exception:
                pass

        return redirect("results")

    def _handle_ai_cost_generation(self, request):
        """Handle AI cost generation for income timeline"""
        # Check if OpenAI API key is configured
        import os

        from .ai_cost_service import AICostEstimationService
        from .models import LocationPreference, SpendingPreference

        if not os.getenv("OPENAI_API_KEY"):
            return JsonResponse(
                {"success": False, "error": "AI cost generation is not configured."}
            )

        try:
            # Get form data
            years = request.POST.getlist("year[]")
            incomes = request.POST.getlist("income[]")
            locations = request.POST.getlist("locations[]")
            start_years = request.POST.getlist("start_years[]")
            end_years = request.POST.getlist("end_years[]")

            housing_spending = request.POST.get("housing_spending", "average")
            travel_spending = request.POST.get("travel_spending", "average")
            food_spending = request.POST.get("food_spending", "average")
            leisure_spending = request.POST.get("leisure_spending", "average")

            # Validate required data
            if not years or not incomes or not locations:
                return JsonResponse(
                    {"success": False, "error": "Please fill in all required fields."}
                )

            # Save location preferences
            LocationPreference.objects.filter(user=request.user).delete()
            for i, location in enumerate(locations):
                if location.strip():
                    LocationPreference.objects.create(
                        user=request.user,
                        location=location.strip(),
                        start_year=int(start_years[i])
                        if i < len(start_years)
                        else int(years[0]),
                        end_year=int(end_years[i])
                        if i < len(end_years)
                        else int(years[-1]),
                    )

            # Save spending preferences
            SpendingPreference.objects.filter(user=request.user).delete()
            SpendingPreference.objects.create(
                user=request.user,
                housing_spending=housing_spending,
                travel_spending=travel_spending,
                food_spending=food_spending,
                leisure_spending=leisure_spending,
            )

            # Generate costs for each year
            ai_service = AICostEstimationService()
            generated_costs = []

            for i, (year, income) in enumerate(zip(years, incomes)):
                if not income or float(income) <= 0:
                    generated_costs.append(0)
                    continue

                # Find location for this year
                location_pref = LocationPreference.objects.filter(
                    user=request.user,
                    start_year__lte=int(year),
                    end_year__gte=int(year),
                ).first()

                if not location_pref:
                    generated_costs.append(0)
                    continue

                # Generate cost estimate
                result = ai_service.generate_contextual_cost_estimate(
                    location=location_pref.location,
                    income=float(income),
                    housing_spending=housing_spending,
                    travel_spending=travel_spending,
                    food_spending=food_spending,
                    leisure_spending=leisure_spending,
                )

                if result["success"]:
                    # Ensure costs don't exceed income
                    total_cost = result["total_annual_cost"]
                    max_cost = float(income) * 0.95  # Max 95% of income
                    final_cost = min(total_cost, max_cost)
                    generated_costs.append(final_cost)
                else:
                    generated_costs.append(0)

            return JsonResponse(
                {
                    "success": True,
                    "costs": generated_costs,
                    "message": f"Generated costs for {len(generated_costs)} years",
                }
            )

        except Exception as e:
            return JsonResponse(
                {"success": False, "error": f"An error occurred: {str(e)}"}
            )

    def _handle_generate_results(self, request):
        """Handle generating results and saving to database"""
        try:
            import json

            from .coli_data import (
                AREA_LEVEL_MULTIPLIER,
                BASE_US_AVG,
                COLI_BY_STATE_2024,
                SPENDING_MULTIPLIER,
                SPENDING_WEIGHTS,
            )
            from .models import LocationPreference, SpendingPreference
            from .tax_data import calculate_total_tax

            # Get the data
            income_data = json.loads(request.POST.get("income_data", "[]"))
            location_data = json.loads(request.POST.get("location_data", "[]"))
            spending_data = json.loads(request.POST.get("spending_data", "{}"))

            if not income_data:
                return JsonResponse(
                    {"success": False, "error": "No income data provided"}
                )

            # Save location preferences
            LocationPreference.objects.filter(user=request.user).delete()
            for loc in location_data:
                state = loc.get("state")
                area_level = loc.get("areaLevel", "average")
                label = f"{state} ({area_level.replace('_', ' ')})"
                LocationPreference.objects.create(
                    user=request.user,
                    location=label,
                    start_year=loc["startYear"],
                    end_year=loc["endYear"],
                )

            # Save spending preferences
            SpendingPreference.objects.filter(user=request.user).delete()
            SpendingPreference.objects.create(
                user=request.user,
                housing_spending=spending_data.get("housing", "average"),
                travel_spending=spending_data.get("travel", "average"),
                food_spending=spending_data.get("food", "average"),
                leisure_spending=spending_data.get("leisure", "average"),
            )

            # Generate costs deterministically using COLI
            # Costs increase by 3% annually (inflation)
            updated_income_data = []
            current_label = None
            base_year = None  # Track the first year to calculate annual 3% increases

            for year_data in income_data:
                # Set base year to first year in the data
                if base_year is None:
                    base_year = year_data["year"]
                # Find location for this year
                location_pref = LocationPreference.objects.filter(
                    user=request.user,
                    start_year__lte=year_data["year"],
                    end_year__gte=year_data["year"],
                ).first()

                if location_pref:
                    # Parse state and area level from label "State (area level)"
                    label = location_pref.location
                    if current_label != label:
                        current_label = label
                    try:
                        state = label.split(" (")[0]
                        area_level = label[
                            label.find("(") + 1 : label.find(")")
                        ].replace(" ", "_")
                    except Exception:
                        state = label
                        area_level = "average"

                    state_index = (
                        COLI_BY_STATE_2024.get(
                            state, COLI_BY_STATE_2024.get("United States", 100.0)
                        )
                        / 100.0
                    )
                    area_mult = AREA_LEVEL_MULTIPLIER.get(area_level, 1.0)

                    base_cost = BASE_US_AVG * state_index * area_mult

                    # Spending preferences weighted multiplier
                    h = SPENDING_MULTIPLIER.get(
                        spending_data.get("housing", "average"), 1.0
                    )
                    t = SPENDING_MULTIPLIER.get(
                        spending_data.get("travel", "average"), 1.0
                    )
                    f = SPENDING_MULTIPLIER.get(
                        spending_data.get("food", "average"), 1.0
                    )
                    leisure_mult = SPENDING_MULTIPLIER.get(
                        spending_data.get("leisure", "average"), 1.0
                    )

                    weighted_mult = (
                        h * SPENDING_WEIGHTS["housing"]
                        + t * SPENDING_WEIGHTS["travel"]
                        + f * SPENDING_WEIGHTS["food"]
                        + leisure_mult * SPENDING_WEIGHTS["leisure"]
                    )

                    final_cost = float(base_cost * weighted_mult)
                else:
                    # If no location found, use national average with average area level
                    state_index = COLI_BY_STATE_2024.get("United States", 100.0) / 100.0
                    final_cost = float(BASE_US_AVG * state_index)

                # Apply 3% annual inflation to costs
                # Calculate years since base year (0-indexed)
                years_since_base = year_data["year"] - base_year
                # Apply compound 3% increase: cost * (1.03 ^ years_since_base)
                inflation_multiplier = Decimal("1.03") ** years_since_base
                final_cost = float(Decimal(str(final_cost)) * inflation_multiplier)

                updated_income_data.append(
                    {
                        "year": year_data["year"],
                        "income": year_data["income"],
                        "costs": final_cost,
                        "location": location_pref.location
                        if location_pref
                        else "Unknown",
                    }
                )

            # Save to database with tax calculations
            # IMPORTANT: Taxes are calculated ONLY on gross income, NOT on costs
            # Formula: Gross Income → Apply Marginal Tax Rates (Federal + State) → After-Tax Income
            #         After-Tax Income - Costs = Net Savings
            IncomeEntry.objects.filter(user=request.user).delete()
            for year_data in updated_income_data:
                # Extract state name from location for tax calculation
                location_str = year_data["location"]
                state_name = (
                    location_str.split(" (")[0]
                    if " (" in location_str
                    else location_str
                )

                # Calculate taxes based on GROSS INCOME and state location
                # Uses progressive marginal tax brackets for federal and state taxes
                income_float = float(year_data["income"])  # Gross income before taxes
                tax_info = calculate_total_tax(income_float, state_name)

                # Costs are NOT taxed - they are separate expenses
                IncomeEntry.objects.create(
                    user=request.user,
                    year=year_data["year"],
                    income_amount=year_data["income"],  # Gross income
                    costs=year_data["costs"],  # Costs (not taxed)
                    location=year_data["location"],
                    federal_tax=Decimal(str(tax_info["federal_tax"])),
                    state_tax=Decimal(str(tax_info["state_tax"])),
                    total_tax=Decimal(str(tax_info["total_tax"])),
                    after_tax_income=Decimal(
                        str(tax_info["after_tax_income"])
                    ),  # Income after taxes
                    savings_rate=0,  # Will be calculated later
                )

            # Return the calculated data for display in editable table
            entries_data = []
            for entry in IncomeEntry.objects.filter(user=request.user).order_by("year"):
                entries_data.append(
                    {
                        "year": entry.year,
                        "income": float(entry.income_amount),
                        "federal_tax": float(entry.federal_tax)
                        if entry.federal_tax
                        else 0,
                        "state_tax": float(entry.state_tax) if entry.state_tax else 0,
                        "total_tax": float(entry.total_tax) if entry.total_tax else 0,
                        "after_tax_income": float(entry.after_tax_income)
                        if entry.after_tax_income
                        else float(entry.income_amount),
                        "costs": float(entry.costs) if entry.costs else 0,
                        "location": entry.location or "Unknown",
                    }
                )

            return JsonResponse(
                {
                    "success": True,
                    "message": "Results generated and saved successfully",
                    "entries": entries_data,
                }
            )

        except Exception as e:
            return JsonResponse(
                {"success": False, "error": f"Error generating results: {str(e)}"}
            )

    def _handle_update_entries(self, request):
        """Handle updating edited income and costs values"""
        try:
            import json

            from .tax_data import calculate_total_tax

            updates = json.loads(request.POST.get("updates", "[]"))

            if not updates:
                return JsonResponse({"success": False, "error": "No updates provided"})

            for update in updates:
                year = update.get("year")
                income = update.get("income")
                costs = update.get("costs")

                if not year or income is None or costs is None:
                    continue

                # Get existing entry to find location/state
                entry = IncomeEntry.objects.filter(user=request.user, year=year).first()

                if entry:
                    # Extract state from location for tax calculation
                    location_str = entry.location or "Unknown"
                    state_name = (
                        location_str.split(" (")[0]
                        if " (" in location_str
                        else location_str
                    )

                    # Recalculate taxes based on new income
                    income_float = float(income)
                    tax_info = calculate_total_tax(income_float, state_name)

                    # Update entry
                    entry.income_amount = Decimal(str(income))
                    entry.costs = Decimal(str(costs))
                    entry.federal_tax = Decimal(str(tax_info["federal_tax"]))
                    entry.state_tax = Decimal(str(tax_info["state_tax"]))
                    entry.total_tax = Decimal(str(tax_info["total_tax"]))
                    entry.after_tax_income = Decimal(str(tax_info["after_tax_income"]))

                    # Recalculate savings rate
                    net_savings = entry.after_tax_income - entry.costs
                    if entry.after_tax_income > 0:
                        entry.savings_rate = (
                            net_savings / entry.after_tax_income
                        ) * 100
                    else:
                        entry.savings_rate = 0

                    entry.save()

            # Return updated entries for table refresh
            entries_data = []
            for entry in IncomeEntry.objects.filter(user=request.user).order_by("year"):
                entries_data.append(
                    {
                        "year": entry.year,
                        "income": float(entry.income_amount),
                        "federal_tax": float(entry.federal_tax)
                        if entry.federal_tax
                        else 0,
                        "state_tax": float(entry.state_tax) if entry.state_tax else 0,
                        "total_tax": float(entry.total_tax) if entry.total_tax else 0,
                        "after_tax_income": float(entry.after_tax_income)
                        if entry.after_tax_income
                        else float(entry.income_amount),
                        "costs": float(entry.costs) if entry.costs else 0,
                        "location": entry.location or "Unknown",
                    }
                )

            return JsonResponse(
                {
                    "success": True,
                    "message": "Entries updated successfully",
                    "entries": entries_data,
                }
            )

        except Exception as e:
            return JsonResponse(
                {"success": False, "error": f"Error updating entries: {str(e)}"}
            )

    def _handle_save_projection(self, request):
        """Handle saving the complete financial projection"""
        try:
            import json

            # Get the projection data
            years = json.loads(request.POST.get("years", "[]"))
            incomes = json.loads(request.POST.get("incomes", "[]"))
            costs = json.loads(request.POST.get("costs", "[]"))

            if not years or not incomes or not costs:
                return JsonResponse(
                    {"success": False, "error": "No projection data provided"}
                )

            # Clear existing income entries for this user
            IncomeEntry.objects.filter(user=request.user).delete()

            # Create new income entries
            for i, (year, income, cost) in enumerate(zip(years, incomes, costs)):
                IncomeEntry.objects.create(
                    user=request.user,
                    year=int(year),
                    income_amount=float(income) if income else 0,
                    costs=float(cost) if cost else 0,
                    savings_rate=0,  # Will be calculated later
                )

            return JsonResponse(
                {
                    "success": True,
                    "message": f"Projection saved with {len(years)} years of data",
                }
            )

        except Exception as e:
            return JsonResponse(
                {"success": False, "error": f"Error saving projection: {str(e)}"}
            )

    def _handle_ai_cost_estimation(self, request):
        """Handle AI cost estimation form submission"""
        # Check if OpenAI API key is configured
        import os

        from .ai_cost_service import AICostEstimationService

        if not os.getenv("OPENAI_API_KEY"):
            messages.error(
                request, "AI cost estimation is not configured. Please contact support."
            )
            return redirect("financial_info")

        # Get form data
        desired_location = request.POST.get("desired_location", "").strip()
        house_type = request.POST.get("house_type", "")
        house_size_sqft = request.POST.get("house_size_sqft", "")
        number_of_children = request.POST.get("number_of_children", "")

        # Validate required fields
        if not all([desired_location, house_type, house_size_sqft, number_of_children]):
            messages.error(
                request, "Please fill in all required fields for AI cost estimation."
            )
            return redirect("financial_info")

        try:
            # Convert to appropriate types
            house_size_sqft = int(house_size_sqft)
            number_of_children = int(number_of_children)

            # Generate AI cost estimate
            ai_service = AICostEstimationService()
            result = ai_service.generate_cost_estimate(
                location=desired_location,
                number_of_children=number_of_children,
                house_size_sqft=house_size_sqft,
                house_type=house_type,
            )

            if result["success"]:
                # Create and save the cost estimate
                cost_estimate = AICostEstimate.objects.create(
                    user=request.user,
                    desired_location=desired_location,
                    number_of_children=number_of_children,
                    house_size_sqft=house_size_sqft,
                    house_type=house_type,
                    ai_response_raw=result["ai_response_raw"],
                    ai_model_used=result["model_used"],
                    confidence_score=result["confidence_score"],
                )

                # Populate AI-generated data
                cost_data = result["cost_data"]
                for field, value in cost_data.items():
                    if hasattr(cost_estimate, field) and value is not None:
                        setattr(cost_estimate, field, value)
                cost_estimate.save()

                messages.success(
                    request,
                    f"AI cost estimate generated successfully! Confidence: {result['confidence_score']:.1%}",
                )
                return redirect("results")
            else:
                error_msg = result.get("error", "Unknown error")
                # Show the actual API error for debugging
                messages.error(request, f"API Error: {error_msg}")
                if "quota" in error_msg.lower() or "billing" in error_msg.lower():
                    messages.error(
                        request,
                        "This appears to be a quota/billing issue. Please check your OpenAI billing settings.",
                    )

        except ValueError as e:
            messages.error(request, f"Invalid input: {str(e)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect("financial_info")


class IncomeTimelineView(LoginRequiredMixin, View):
    template_name = "financial/income_timeline.html"

    def get(self, request):
        income_entries = IncomeEntry.objects.filter(user=request.user).order_by("year")
        return render(request, self.template_name, {"income_entries": income_entries})

    def post(self, request):
        year = request.POST.get("year")
        income_amount = request.POST.get("income_amount")
        income_source = request.POST.get("income_source", "Salary")

        if year and income_amount:
            IncomeEntry.objects.update_or_create(
                user=request.user,
                year=int(year),
                defaults={
                    "income_amount": Decimal(income_amount),
                    "income_source": income_source,
                },
            )
            messages.success(request, f"Income data for {year} saved successfully!")

        return redirect("income_timeline")


class ResultsView(LoginRequiredMixin, View):
    def get(self, request):
        scenarios = ProjectionScenario.objects.filter(user=request.user).order_by("id")

        latest_by_scenario = []
        for sc in scenarios:
            latest = (
                ProjectionResult.objects.filter(user=request.user, scenario=sc)
                .order_by("-created_at")
                .first()
            )
            if latest:
                latest_by_scenario.append(latest)

        active = None
        if latest_by_scenario:
            target_sid = request.GET.get("scenario")
            active = (
                next(
                    (r for r in latest_by_scenario if str(r.scenario_id) == target_sid),
                    latest_by_scenario[0],
                )
                if target_sid
                else latest_by_scenario[0]
            )

        yearly = []
        if active:
            yearly = list(
                ProjectionYearlyData.objects.filter(projection=active)
                .order_by("year")
                .values(
                    "year",
                    "ending_balance",
                    "contributions",
                    "gains",
                    "inflation_adjusted_balance",
                )
            )

        income_entries_qs = IncomeEntry.objects.filter(user=request.user).order_by(
            "year"
        )
        income_entries = []
        for entry in income_entries_qs:
            # Use after-tax income for calculations
            # Formula: Gross Income → Taxes (Marginal Rates) → After-Tax Income → Costs → Net Savings
            # Costs are NOT taxed - they are separate expenses deducted from after-tax income
            income_for_calc = (
                float(entry.after_tax_income)
                if entry.after_tax_income
                else float(entry.income_amount)
            )

            # Calculate net savings: After-Tax Income - Costs (costs are not taxed)
            net_savings_after_tax = (
                income_for_calc - float(entry.costs) if entry.costs else income_for_calc
            )

            savings_rate_after_tax = (
                (net_savings_after_tax / income_for_calc * 100)
                if income_for_calc > 0
                else 0
            )

            income_entries.append(
                {
                    "year": entry.year,
                    "income": entry.income_amount,  # Gross income
                    "federal_tax": entry.federal_tax or 0,
                    "state_tax": entry.state_tax or 0,
                    "total_tax": entry.total_tax or 0,
                    "after_tax_income": entry.after_tax_income or entry.income_amount,
                    "costs": entry.costs,
                    "location": entry.location or "Unknown",
                    "net_savings": net_savings_after_tax,
                    "savings_rate": savings_rate_after_tax,
                }
            )
        income_years = [e["year"] for e in income_entries]

        # Align yearly projection series to the number of income years (labels come from income_years)
        net_worth_series = []
        if yearly:
            for idx in range(len(income_years)):
                if idx < len(yearly):
                    net_worth_series.append(float(yearly[idx]["ending_balance"]))
                else:
                    break

        # Get AI cost estimates for the user
        ai_cost_estimates = AICostEstimate.objects.filter(user=request.user).order_by(
            "-created_at"
        )[:3]

        context = {
            "projections": latest_by_scenario,
            "active_result": active,
            "yearly": yearly,
            "scenarios": scenarios,
            "income_entries": income_entries,
            "income_years": income_years,
            "net_worth_series": net_worth_series,
            "ai_cost_estimates": ai_cost_estimates,
        }
        return render(request, "financial/results.html", context)

    def post(self, request):
        user = self.request.user
        scenario_id = request.POST.get("scenario_id")

        if not scenario_id:
            messages.error(request, "Please select a scenario.")
            return redirect("results")

        years_from_income = IncomeEntry.objects.filter(user=user).count()
        if years_from_income <= 0:
            messages.error(
                request, "Add income years on the Financial Info page first."
            )
            return redirect("financial_info")

        try:
            calculator = ProjectionCalculator(user)
            calculator.calculate_projection(
                int(scenario_id), projected_years=years_from_income
            )
            messages.success(request, "Projection calculated from your entered years.")
        except Exception as e:
            messages.error(request, f"Error calculating projection: {str(e)}")

        return redirect("results")


class ProjectionDetailView(LoginRequiredMixin, View):
    template_name = "financial/projection_detail.html"

    def get(self, request, projection_id):
        user = request.user

        try:
            projection = ProjectionResult.objects.get(id=projection_id, user=user)
        except ProjectionResult.DoesNotExist:
            messages.error(request, "Projection not found.")
            return redirect("results")

        calculator = ProjectionCalculator(user)
        summary = calculator.get_projection_summary(projection.id)

        return render(
            request,
            self.template_name,
            {
                "projection": projection,
                "summary": summary["summary"],
                "yearly_data": summary["yearly_data"],
            },
        )


class ScenarioComparisonView(LoginRequiredMixin, View):
    template_name = "financial/scenario_comparison.html"

    def get(self, request):
        user = request.user
        scenarios = ProjectionScenario.objects.filter(user=user)

        return render(request, self.template_name, {"scenarios": scenarios})

    def post(self, request):
        user = request.user
        scenario_ids = request.POST.getlist("scenario_ids")

        if len(scenario_ids) < 2:
            messages.error(request, "Please select at least 2 scenarios to compare.")
            return redirect("scenario_comparison")

        years_from_income = IncomeEntry.objects.filter(user=user).count()
        if years_from_income <= 0:
            messages.error(
                request, "Add income years on the Financial Info page first."
            )
            return redirect("financial_info")

        try:
            calculator = ProjectionCalculator(user)
            comparisons = calculator.compare_scenarios(
                [int(sid) for sid in scenario_ids], years_from_income
            )
            return render(
                request,
                self.template_name,
                {"comparisons": comparisons, "projected_years": years_from_income},
            )
        except Exception as e:
            messages.error(request, f"Error comparing scenarios: {str(e)}")
            return redirect("scenario_comparison")


class AICostEstimateViewSet(viewsets.ModelViewSet):
    queryset = AICostEstimate.objects.all()
    serializer_class = AICostEstimateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AICostEstimate.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
