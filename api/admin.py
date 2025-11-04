# Register your models here.

from django.contrib import admin

from .models import (
    FinancialProfile,
    IncomeEntry,
    MonteCarloIteration,
    MonteCarloSimulation,
    PersonalInformation,
    ProjectionResult,
    ProjectionScenario,
)


@admin.register(MonteCarloSimulation)
class MonteCarloSimulationAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "scenario",
        "number_of_iterations",
        "projected_years",
        "mean_final_value",
        "median_final_value",
        "created_at",
    ]
    list_filter = ["created_at", "scenario"]
    search_fields = ["user__username", "scenario__name"]
    readonly_fields = [
        "mean_final_value",
        "median_final_value",
        "std_dev_final_value",
        "min_final_value",
        "max_final_value",
        "percentile_5",
        "percentile_25",
        "percentile_75",
        "percentile_95",
        "success_rate",
        "created_at",
        "updated_at",
    ]


@admin.register(MonteCarloIteration)
class MonteCarloIterationAdmin(admin.ModelAdmin):
    list_display = [
        "simulation",
        "iteration_number",
        "final_value",
        "total_contributions",
        "total_gains",
    ]
    list_filter = ["simulation"]
    search_fields = ["simulation__user__username"]


# Register other models if not already registered
if not admin.site.is_registered(ProjectionScenario):
    admin.site.register(ProjectionScenario)
if not admin.site.is_registered(ProjectionResult):
    admin.site.register(ProjectionResult)
if not admin.site.is_registered(FinancialProfile):
    admin.site.register(FinancialProfile)
if not admin.site.is_registered(IncomeEntry):
    admin.site.register(IncomeEntry)
if not admin.site.is_registered(PersonalInformation):
    admin.site.register(PersonalInformation)
