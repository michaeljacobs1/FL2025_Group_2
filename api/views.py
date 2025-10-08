from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from django.views import View
from rest_framework import permissions, viewsets
from decimal import Decimal
import json

from .models import Post, PersonalInformation, IncomeEntry, FinancialProfile, ProjectionResult
from .serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]


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
        context['personal_info'] = personal_info
        
        
        financial_profile, created = FinancialProfile.objects.get_or_create(user=user)
        context['financial_profile'] = financial_profile
        
       
        context['recent_projections'] = ProjectionResult.objects.filter(user=user).order_by('-created_at')[:3]
        
        return context


class PersonalInformationView(LoginRequiredMixin, View):
    template_name = "financial/personal_info.html"
    
    def get(self, request):
        personal_info, created = PersonalInformation.objects.get_or_create(user=request.user)
        return render(request, self.template_name, {'personal_info': personal_info})
    
    def post(self, request):
        personal_info, created = PersonalInformation.objects.get_or_create(user=request.user)
        
        personal_info.name = request.POST.get('name', '') or None
        personal_info.address = request.POST.get('address', '') or None
        personal_info.phone = request.POST.get('phone', '') or None
        personal_info.email = request.POST.get('email', '') or None
        
        date_of_birth = request.POST.get('date_of_birth', '')
        personal_info.date_of_birth = date_of_birth if date_of_birth else None
        
        gender = request.POST.get('gender', '')
        personal_info.gender = gender if gender else None
        
        personal_info.save()
        
        messages.success(request, 'Personal information updated successfully!')
        return redirect('personal_info')


class FinancialInformationView(LoginRequiredMixin, View):
    template_name = "financial/financial_info.html"
    
    def get(self, request):
        financial_profile, created = FinancialProfile.objects.get_or_create(user=request.user)
        return render(request, self.template_name, {'financial_profile': financial_profile})
    
    def post(self, request):
        financial_profile, created = FinancialProfile.objects.get_or_create(user=request.user)
        
        savings_rate = request.POST.get('savings_rate', '')
        financial_profile.current_savings_rate = Decimal(savings_rate) if savings_rate else None
        
        monthly_income = request.POST.get('monthly_income', '')
        financial_profile.monthly_income = Decimal(monthly_income) if monthly_income else None
        
        monthly_expenses = request.POST.get('monthly_expenses', '')
        financial_profile.monthly_expenses = Decimal(monthly_expenses) if monthly_expenses else None
        
        current_savings = request.POST.get('current_savings', '')
        financial_profile.current_savings = Decimal(current_savings) if current_savings else None
        
        financial_profile.investment_goals = request.POST.get('investment_goals', '')
        financial_profile.retirement_goals = request.POST.get('retirement_goals', '')
        financial_profile.save()
        
        messages.success(request, 'Financial information updated successfully!')
        return redirect('financial_info')


class IncomeTimelineView(LoginRequiredMixin, View):
    template_name = "financial/income_timeline.html"
    
    def get(self, request):
        income_entries = IncomeEntry.objects.filter(user=request.user).order_by('year')
        return render(request, self.template_name, {'income_entries': income_entries})
    
    def post(self, request):
        
        year = request.POST.get('year')
        income_amount = request.POST.get('income_amount')
        income_source = request.POST.get('income_source', 'Salary')
        
        if year and income_amount:
            IncomeEntry.objects.update_or_create(
                user=request.user,
                year=int(year),
                defaults={
                    'income_amount': Decimal(income_amount),
                    'income_source': income_source
                }
            )
            messages.success(request, f'Income data for {year} saved successfully!')
        
        return redirect('income_timeline')


class ResultsView(LoginRequiredMixin, View):
    template_name = "financial/results.html"
    
    def get(self, request):
        user = request.user
        
        
        try:
            financial_profile = FinancialProfile.objects.get(user=user)
        except FinancialProfile.DoesNotExist:
            messages.warning(request, 'Please complete your financial information first.')
            return redirect('financial_info')
        
        
        projections = ProjectionResult.objects.filter(user=user).order_by('-created_at')
        
        return render(request, self.template_name, {
            'financial_profile': financial_profile,
            'projections': projections
        })
    
    def post(self, request):
       
        user = request.user
        projected_years = int(request.POST.get('projected_years', 10))
        
        try:
            financial_profile = FinancialProfile.objects.get(user=user)
        except FinancialProfile.DoesNotExist:
            messages.warning(request, 'Please complete your financial information first.')
            return redirect('financial_info')
        
    
        monthly_savings = financial_profile.monthly_income - financial_profile.monthly_expenses
        annual_savings = monthly_savings * 12
        total_invested = financial_profile.current_savings + (annual_savings * projected_years)
        
       
        projected_valuation = total_invested * (1.07 ** projected_years)
        
      
        income_ratio = 100.0
        investment_ratio = 60.0
        property_ratio = 20.0
        real_estate_ratio = 15.0
        liabilities_ratio = 5.0
        
        net_worth = projected_valuation
        
        
        projection = ProjectionResult.objects.create(
            user=user,
            total_invested=total_invested,
            projected_years=projected_years,
            projected_valuation=projected_valuation,
            income_ratio=income_ratio,
            investment_ratio=investment_ratio,
            property_ratio=property_ratio,
            real_estate_ratio=real_estate_ratio,
            liabilities_ratio=liabilities_ratio,
            net_worth=net_worth
        )
        
        messages.success(request, f'Projection calculated for {projected_years} years!')
        return redirect('results')
