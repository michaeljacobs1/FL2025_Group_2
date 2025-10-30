from django import forms

from .models import AICostEstimate


class AICostEstimateForm(forms.ModelForm):
    """Form for AI cost estimation input"""

    class Meta:
        model = AICostEstimate
        fields = [
            "desired_location",
            "number_of_children",
            "house_size_sqft",
            "house_type",
        ]
        widgets = {
            "desired_location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Austin, Texas, USA",
                    "required": True,
                }
            ),
            "number_of_children": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "10",
                    "required": True,
                }
            ),
            "house_size_sqft": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "500",
                    "max": "10000",
                    "required": True,
                }
            ),
            "house_type": forms.Select(
                attrs={"class": "form-control", "required": True}
            ),
        }
        labels = {
            "desired_location": "Desired Location",
            "number_of_children": "Number of Children",
            "house_size_sqft": "House Size (sq ft)",
            "house_type": "House Type",
        }
        help_texts = {
            "desired_location": "Enter the city, state, and country where you want to live",
            "number_of_children": "How many children do you plan to have?",
            "house_size_sqft": "What size house are you looking for?",
            "house_type": "What type of housing are you interested in?",
        }

    def clean_desired_location(self):
        location = self.cleaned_data.get("desired_location")
        if location and len(location.strip()) < 3:
            raise forms.ValidationError(
                "Please enter a more specific location (e.g., 'Austin, Texas, USA')"
            )
        return location.strip()

    def clean_number_of_children(self):
        children = self.cleaned_data.get("number_of_children")
        if children is not None and children < 0:
            raise forms.ValidationError("Number of children cannot be negative")
        if children is not None and children > 10:
            raise forms.ValidationError(
                "Please enter a reasonable number of children (max 10)"
            )
        return children

    def clean_house_size_sqft(self):
        size = self.cleaned_data.get("house_size_sqft")
        if size is not None and size < 500:
            raise forms.ValidationError("House size should be at least 500 square feet")
        if size is not None and size > 10000:
            raise forms.ValidationError(
                "House size seems unreasonably large (max 10,000 sq ft)"
            )
        return size
