# api/serializers.py
from rest_framework import serializers

from .models import (
    FinancialProfile,
    IncomeEntry,
    PersonalInformation,
    Post,
    ProjectionResult,
    ProjectionScenario,
    ProjectionYearlyData,
)


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"


class FinancialProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialProfile
        fields = "__all__"
        read_only_fields = ['user', 'created_at', 'updated_at']


class ProjectionScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectionScenario
        fields = "__all__"
        read_only_fields = ['user', 'created_at', 'updated_at']


class ProjectionYearlyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectionYearlyData
        fields = "__all__"


class ProjectionResultSerializer(serializers.ModelSerializer):
    scenario = ProjectionScenarioSerializer(read_only=True)
    yearly_data = ProjectionYearlyDataSerializer(many=True, read_only=True)
    return_on_investment = serializers.ReadOnlyField()
    
    class Meta:
        model = ProjectionResult
        fields = "__all__"
        read_only_fields = ['user', 'created_at']


class IncomeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeEntry
        fields = "__all__"
        read_only_fields = ['user', 'created_at']


class PersonalInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInformation
        fields = "__all__"
        read_only_fields = ['user', 'created_at', 'updated_at']
