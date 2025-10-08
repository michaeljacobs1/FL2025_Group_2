from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    PostViewSet, SignUpView, FinancialDashboardView, 
    PersonalInformationView, FinancialInformationView, 
    IncomeTimelineView, ResultsView
)

router = DefaultRouter()
router.register("posts", PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("signup/", SignUpView.as_view(), name="signup"),
    # Financial Planning URLs
    path("financial/", FinancialDashboardView.as_view(), name="financial_dashboard"),
    path("personal-info/", PersonalInformationView.as_view(), name="personal_info"),
    path("financial-info/", FinancialInformationView.as_view(), name="financial_info"),
    path("income-timeline/", IncomeTimelineView.as_view(), name="income_timeline"),
    path("results/", ResultsView.as_view(), name="results"),
]