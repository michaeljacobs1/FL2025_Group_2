from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView
from rest_framework import permissions, viewsets

from .models import (
    FinancialProfile,
    IncomeEntry,
    PersonalInformation,
    Post,
    ProjectionResult,
    ProjectionScenario,
    ProjectionYearlyData,
)
from .projection_service import ProjectionCalculator
from .serializers import (
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
    template_name = "financial/financial_info.html"

    def get(self, request):
        financial_profile, created = FinancialProfile.objects.get_or_create(
            user=request.user
        )
        income_entries = IncomeEntry.objects.filter(user=request.user).order_by("year")
        return render(
            request,
            self.template_name,
            {"financial_profile": financial_profile, "income_entries": income_entries},
        )

    def post(self, request):
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
        income_entries = list(income_entries_qs.values("year", "income_amount"))
        income_years = [e["year"] for e in income_entries]

        # Align yearly projection series to the number of income years (labels come from income_years)
        net_worth_series = []
        if yearly:
            for idx in range(len(income_years)):
                if idx < len(yearly):
                    net_worth_series.append(float(yearly[idx]["ending_balance"]))
                else:
                    break

        context = {
            "projections": latest_by_scenario,
            "active_result": active,
            "yearly": yearly,
            "scenarios": scenarios,
            "income_entries": income_entries,
            "income_years": income_years,
            "net_worth_series": net_worth_series,
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
