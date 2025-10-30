import json
import logging
import os
from decimal import Decimal
from typing import Dict, Any, Optional

import openai
from django.conf import settings

logger = logging.getLogger(__name__)

# Set the API key globally for the older openai library
openai.api_key = os.getenv('OPENAI_API_KEY')


class AICostEstimationService:
    """Service for generating cost estimates using OpenAI API"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        # Allow overriding the model via env; default stays widely-available
        # Examples: gpt-3.5-turbo, gpt-4o, gpt-4.1, gpt-4.5 (if account has access)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    def generate_cost_estimate(
        self, 
        location: str, 
        number_of_children: int, 
        house_size_sqft: int,
        house_type: str = "single_family"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive cost estimates for housing and family planning
        
        Args:
            location: Desired location (e.g., "Austin, Texas, USA")
            number_of_children: Desired number of children
            house_size_sqft: Desired house size in square feet
            house_type: Type of house (single_family, condo, townhouse, multi_family)
        
        Returns:
            Dictionary containing all cost estimates and metadata
        """
        
        prompt = self._build_prompt(location, number_of_children, house_size_sqft, house_type)
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial planning expert specializing in real estate and family cost analysis. Provide accurate, data-driven cost estimates based on current market conditions and reliable sources."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent, factual responses
                max_tokens=2000
            )
            
            ai_response = response.choices[0].message.content
            cost_data = self._parse_ai_response(ai_response)
            
            return {
                "success": True,
                "cost_data": cost_data,
                "ai_response_raw": ai_response,
                "model_used": self.model,
                "confidence_score": self._calculate_confidence_score(cost_data)
            }
            
        except Exception as e:
            logger.error(f"Error generating AI cost estimate: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "cost_data": {},
                "ai_response_raw": "",
                "model_used": self.model,
                "confidence_score": 0.0
            }
    
    def _build_prompt(self, location: str, number_of_children: int, house_size_sqft: int, house_type: str) -> str:
        """Build the prompt for OpenAI API"""
        
        house_type_descriptions = {
            "single_family": "single-family detached home",
            "condo": "condominium or apartment",
            "townhouse": "townhouse",
            "multi_family": "multi-family home"
        }
        
        house_desc = house_type_descriptions.get(house_type, "single-family home")
        
        return f"""
Please provide detailed cost estimates for the following scenario. Use current market data and reliable sources. Format your response as a JSON object with the exact field names specified.

Location: {location}
Number of children desired: {number_of_children}
House size: {house_size_sqft} square feet
House type: {house_desc}

Please provide estimates for the following costs in USD (use current market rates):

HOUSING COSTS:
- estimated_home_price: Average home price for a {house_size_sqft} sqft {house_desc} in {location}
- estimated_monthly_mortgage: Monthly mortgage payment (assume 20% down, 30-year fixed at current rates)
- estimated_property_tax_annual: Annual property taxes
- estimated_insurance_annual: Annual homeowners insurance
- estimated_utilities_monthly: Monthly utilities (electric, gas, water, internet)
- estimated_maintenance_annual: Annual maintenance and repairs (1-2% of home value)

CHILD-RELATED COSTS (per child):
- estimated_childcare_annual: Annual childcare costs (daycare, after-school care)
- estimated_education_annual: Annual education costs (private school, tutoring, supplies)
- estimated_child_healthcare_annual: Annual healthcare costs for child
- estimated_child_food_annual: Annual food costs for child
- estimated_child_clothing_annual: Annual clothing costs for child

LOCATION-BASED LIFESTYLE COSTS (for family):
- estimated_transportation_annual: Annual transportation costs (car payments, insurance, gas, public transit)
- estimated_healthcare_annual: Annual healthcare costs for adults
- estimated_groceries_annual: Annual grocery costs for family

IMPORTANT:
1. Use current market data and recent statistics
2. Consider the specific location's cost of living
3. Account for inflation and current economic conditions
4. Provide realistic estimates based on actual market conditions
5. Return ONLY a valid JSON object with the exact field names above
6. All monetary values should be numbers (no currency symbols or commas)
7. If you cannot find specific data for a field, provide a reasonable estimate based on similar locations

Example format:
{{
    "estimated_home_price": 450000,
    "estimated_monthly_mortgage": 2400,
    "estimated_property_tax_annual": 9000,
    ...
}}
"""
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response and extract cost data"""
        try:
            # Try to find JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                cost_data = json.loads(json_str)
                
                # Convert all numeric values to Decimal for database storage
                for key, value in cost_data.items():
                    if isinstance(value, (int, float)):
                        cost_data[key] = Decimal(str(value))
                
                return cost_data
            else:
                logger.warning("No JSON found in AI response")
                return {}
                
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response JSON: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error processing AI response: {str(e)}")
            return {}
    
    def _calculate_confidence_score(self, cost_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on data completeness and reasonableness"""
        if not cost_data:
            return 0.0
        
        # Check if all required fields are present
        required_fields = [
            'estimated_home_price', 'estimated_monthly_mortgage', 'estimated_property_tax_annual',
            'estimated_insurance_annual', 'estimated_utilities_monthly', 'estimated_maintenance_annual',
            'estimated_childcare_annual', 'estimated_education_annual', 'estimated_child_healthcare_annual',
            'estimated_child_food_annual', 'estimated_child_clothing_annual',
            'estimated_transportation_annual', 'estimated_healthcare_annual', 'estimated_groceries_annual'
        ]
        
        present_fields = sum(1 for field in required_fields if field in cost_data and cost_data[field] is not None)
        completeness_score = present_fields / len(required_fields)
        
        # Check for reasonable values (basic sanity checks)
        reasonableness_score = 1.0
        
        if 'estimated_home_price' in cost_data:
            home_price = float(cost_data['estimated_home_price'])
            if home_price < 50000 or home_price > 10000000:  # Unreasonable home prices
                reasonableness_score *= 0.5
        
        if 'estimated_monthly_mortgage' in cost_data:
            mortgage = float(cost_data['estimated_monthly_mortgage'])
            if mortgage < 500 or mortgage > 50000:  # Unreasonable mortgage payments
                reasonableness_score *= 0.5
        
        # Final confidence score
        confidence = (completeness_score * 0.7 + reasonableness_score * 0.3)
        return min(confidence, 1.0)
    
    def validate_cost_data(self, cost_data: Dict[str, Any]) -> bool:
        """Validate that cost data contains reasonable values"""
        if not cost_data:
            return False
        
        # Check for required fields
        required_fields = ['estimated_home_price', 'estimated_monthly_mortgage']
        if not all(field in cost_data for field in required_fields):
            return False
        
        # Check for reasonable values
        try:
            home_price = float(cost_data.get('estimated_home_price', 0))
            mortgage = float(cost_data.get('estimated_monthly_mortgage', 0))
            
            if home_price <= 0 or mortgage <= 0:
                return False
                
            # Basic sanity check: mortgage should be roughly 0.4-0.8% of home price monthly
            expected_mortgage_range = (home_price * 0.004, home_price * 0.008)
            if not (expected_mortgage_range[0] <= mortgage <= expected_mortgage_range[1]):
                logger.warning(f"Mortgage payment {mortgage} seems unreasonable for home price {home_price}")
                # Don't fail validation for this, just log warning
            
            return True
            
        except (ValueError, TypeError):
            return False
    
    def generate_contextual_cost_estimate(
        self,
        location: str,
        income: float,
        housing_spending: str,
        travel_spending: str,
        food_spending: str,
        leisure_spending: str,
        previous_cost: float = None,
        year: int = None
    ) -> Dict[str, Any]:
        """
        Generate contextual cost estimates based on income and spending preferences.
        Costs are scaled based on income level and spending preferences.
        For the same location, costs should not change more than 2% per year.
        """
        
        prompt = self._build_contextual_prompt(
            location, income, housing_spending, travel_spending,
            food_spending, leisure_spending
        )
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial planning expert. Generate realistic annual living costs based on location, income level, and spending preferences. Costs should be contextual to the person's income - a moderate spender making $1M will have different costs than a moderate spender making $100K. Always provide a total annual cost that never exceeds the given income."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content
            cost_data = self._parse_contextual_response(ai_response)
            
            # Apply 2% stability constraint for same location
            total_cost = cost_data.get("total_annual_cost", 0)
            if previous_cost is not None and previous_cost > 0:
                # Calculate max allowed change (2% increase or decrease)
                max_increase = previous_cost * 1.02
                max_decrease = previous_cost * 0.98
                
                if total_cost > max_increase:
                    total_cost = max_increase
                    logger.info(f"Cost capped at 2% increase: {total_cost}")
                elif total_cost < max_decrease:
                    total_cost = max_decrease
                    logger.info(f"Cost capped at 2% decrease: {total_cost}")
            
            # Update the cost data with the adjusted total
            cost_data["total_annual_cost"] = total_cost
            
            return {
                "success": True,
                "total_annual_cost": total_cost,
                "cost_breakdown": cost_data,
                "ai_response_raw": ai_response,
                "model_used": self.model,
            }
            
        except Exception as e:
            # If a configured model isn't available (e.g., gpt-4.5), fall back gracefully
            err_msg = str(e)
            logger.error(f"Error generating contextual cost estimate with model {self.model}: {err_msg}")
            if self.model != 'gpt-3.5-turbo':
                try:
                    fallback_model = 'gpt-3.5-turbo'
                    logger.info(f"Falling back to {fallback_model}")
                    response = openai.ChatCompletion.create(
                        model=fallback_model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a financial planning expert. Generate realistic annual living costs based on location, income level, and spending preferences. Costs should be contextual to the person's income - a moderate spender making $1M will have different costs than a moderate spender making $100K. Always provide a total annual cost that never exceeds the given income."
                            },
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        max_tokens=1000
                    )
                    ai_response = response.choices[0].message.content
                    cost_data = self._parse_contextual_response(ai_response)
                    return {
                        "success": True,
                        "total_annual_cost": cost_data.get("total_annual_cost", 0),
                        "cost_breakdown": cost_data,
                        "ai_response_raw": ai_response,
                        "model_used": fallback_model,
                    }
                except Exception as inner_e:
                    logger.error(f"Fallback to gpt-3.5-turbo failed: {inner_e}")
            return {"success": False, "error": f"Failed to generate cost estimate: {err_msg}"}
    
    def _build_contextual_prompt(
        self, 
        location: str, 
        income: float, 
        housing_spending: str, 
        travel_spending: str, 
        food_spending: str, 
        leisure_spending: str
    ) -> str:
        """Build the prompt for contextual cost estimation"""
        
        spending_descriptions = {
            "very_little": "very frugal, minimal spending",
            "less_than_average": "below average spending habits", 
            "average": "average spending habits",
            "above_average": "above average spending habits",
            "very_high": "very high spending, luxury lifestyle"
        }
        
        housing_desc = spending_descriptions.get(housing_spending, "average")
        travel_desc = spending_descriptions.get(travel_spending, "average")
        food_desc = spending_descriptions.get(food_spending, "average")
        leisure_desc = spending_descriptions.get(leisure_spending, "average")
        
        return f"""
Please provide realistic annual living costs for someone living in {location} with an annual income of ${income:,.2f}.

IMPORTANT: Consider the significant cost differences between locations. {location} may have very different living costs compared to other cities. For example:
- High-cost areas (NYC, San Francisco, London): Expect 30-50% higher costs
- Medium-cost areas (Chicago, Austin, Seattle): Moderate costs
- Lower-cost areas (Phoenix, Dallas, Atlanta): 20-30% lower costs
- International locations: Consider currency, local economy, and cost of living

Spending preferences:
- Housing: {housing_desc} (consider local housing market prices)
- Travel: {travel_desc} (factor in local transportation costs and travel opportunities)
- Food & Groceries: {food_desc} (account for local food prices and dining culture)
- Leisure: {leisure_desc} (consider local entertainment costs and lifestyle)

Generate costs that are:
1. Appropriate for this income level and spending preferences
2. Realistic for the specific location's cost of living
3. Contextual - a person making ${income:,.2f} should have different costs than someone making $50,000 or $500,000
4. Location-specific - emphasize how {location} affects each cost category

Return a JSON object with these fields:
- total_annual_cost: Total annual living costs (must be less than income)
- housing_cost: Annual housing costs (consider local rent/mortgage rates)
- transportation_cost: Annual transportation costs (local transit, car costs, gas prices)
- food_cost: Annual food and grocery costs (local food prices and dining culture)
- leisure_cost: Annual leisure and entertainment costs (local entertainment options and pricing)
- other_costs: Annual other miscellaneous costs (utilities, insurance, etc. - location-specific)

Ensure the total_annual_cost is realistic for the income level, location-specific, and never exceeds the given income.
"""
    
    def _parse_contextual_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse the AI response for contextual cost estimation"""
        try:
            # Try to extract JSON from the response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = ai_response[start_idx:end_idx]
                cost_data = json.loads(json_str)
                
                # Convert to Decimal for consistency
                for key, value in cost_data.items():
                    if isinstance(value, (int, float)):
                        cost_data[key] = Decimal(str(value))
                
                return cost_data
            else:
                # Fallback: try to extract numbers from text
                import re
                numbers = re.findall(r'\$?([\d,]+\.?\d*)', ai_response)
                if numbers:
                    total_cost = float(numbers[0].replace(',', ''))
                    return {
                        "total_annual_cost": Decimal(str(total_cost)),
                        "housing_cost": Decimal(str(total_cost * 0.4)),
                        "transportation_cost": Decimal(str(total_cost * 0.15)),
                        "food_cost": Decimal(str(total_cost * 0.2)),
                        "leisure_cost": Decimal(str(total_cost * 0.15)),
                        "other_costs": Decimal(str(total_cost * 0.1))
                    }
                else:
                    return {"total_annual_cost": Decimal('0')}
                    
        except (json.JSONDecodeError, ValueError, IndexError) as e:
            logger.error(f"Error parsing contextual AI response: {str(e)}")
            return {"total_annual_cost": Decimal('0')}
