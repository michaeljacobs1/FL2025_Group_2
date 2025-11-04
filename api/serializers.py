# api/serializers.py
from rest_framework import serializers

from .models import (
    AICostEstimate,
    FinancialProfile,
    IncomeEntry,
    MonteCarloIteration,
    MonteCarloSimulation,
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
        read_only_fields = ["user", "created_at", "updated_at"]


class ProjectionScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectionScenario
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]


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
        read_only_fields = ["user", "created_at"]


class IncomeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeEntry
        fields = "__all__"
        read_only_fields = ["user", "created_at"]


class PersonalInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInformation
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]


class AICostEstimateSerializer(serializers.ModelSerializer):
    total_housing_costs_annual = serializers.ReadOnlyField()
    total_child_costs_annual = serializers.ReadOnlyField()
    total_lifestyle_costs_annual = serializers.ReadOnlyField()

    class Meta:
        model = AICostEstimate
        fields = "__all__"
        read_only_fields = [
            "user",
            "created_at",
            "updated_at",
            "ai_response_raw",
            "ai_model_used",
            "confidence_score",
        ]


class MonteCarloIterationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonteCarloIteration
        fields = "__all__"


class MonteCarloSimulationSerializer(serializers.ModelSerializer):
    scenario = ProjectionScenarioSerializer(read_only=True)
    iterations = MonteCarloIterationSerializer(many=True, read_only=True)

    class Meta:
        model = MonteCarloSimulation
        fields = "__all__"
        read_only_fields = [
            "user",
            "created_at",
            "updated_at",
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
        ]
