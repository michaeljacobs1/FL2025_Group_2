from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import SignupForm  # make sure this import exists


class SignUpView(CreateView):
    form_class = SignupForm      # <- use our form with the email field
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"
