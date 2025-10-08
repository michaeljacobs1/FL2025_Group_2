from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FinancialDashboardView,
    FinancialInformationView,
    FinancialProfileViewSet,
    IncomeEntryViewSet,
    IncomeTimelineView,
    PersonalInformationView,
    PersonalInformationViewSet,
    PostViewSet,
    ProjectionDetailView,
    ProjectionResultViewSet,
    ProjectionScenarioViewSet,
    ResultsView,
    ScenarioComparisonView,
    SignUpView,
)

router = DefaultRouter()
router.register("posts", PostViewSet)
router.register("financial-profiles", FinancialProfileViewSet)
router.register("projection-scenarios", ProjectionScenarioViewSet)
router.register("projection-results", ProjectionResultViewSet)
router.register("income-entries", IncomeEntryViewSet)
router.register("personal-information", PersonalInformationViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("signup/", SignUpView.as_view(), name="signup"),
    # Financial Planning URLs
    path("financial/", FinancialDashboardView.as_view(), name="financial_dashboard"),
    path("personal-info/", PersonalInformationView.as_view(), name="personal_info"),
    path("financial-info/", FinancialInformationView.as_view(), name="financial_info"),
    path("income-timeline/", IncomeTimelineView.as_view(), name="income_timeline"),
    path("results/", ResultsView.as_view(), name="results"),
    path(
        "projection/<int:projection_id>/",
        ProjectionDetailView.as_view(),
        name="projection_detail",
    ),
    path(
        "scenario-comparison/",
        ScenarioComparisonView.as_view(),
        name="scenario_comparison",
    ),
]
