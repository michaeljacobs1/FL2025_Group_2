from django.urls import path

from .views import DashboardView, SignUpView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup1"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
