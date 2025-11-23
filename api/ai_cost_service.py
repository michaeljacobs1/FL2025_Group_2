import json
import logging
import os
import re
from decimal import Decimal
from typing import Any, Dict

import openai

logger = logging.getLogger(__name__)

# Set the API key globally for the older openai library
openai.api_key = os.getenv("OPENAI_API_KEY")


class AICostEstimationService:
    """Service for generating cost estimates using OpenAI API"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        # Allow overriding the model via env; default stays widely-available
        # Examples: gpt-3.5-turbo, gpt-4o, gpt-4.1, gpt-4.5 (if account has access)
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    def generate_cost_estimate(
        self,
        location: str,
        number_of_children: int,
        house_size_sqft: int,
        house_type: str = "single_family",
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

        prompt = self._build_prompt(
            location, number_of_children, house_size_sqft, house_type
        )

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial planning expert specializing in real estate and family cost analysis. Provide accurate, data-driven cost estimates based on current market conditions and reliable sources.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Lower temperature for more consistent, factual responses
                max_tokens=2000,
            )

            ai_response = response.choices[0].message.content
            cost_data = self._parse_ai_response(ai_response)

            return {
                "success": True,
                "cost_data": cost_data,
                "ai_response_raw": ai_response,
                "model_used": self.model,
                "confidence_score": self._calculate_confidence_score(cost_data),
            }

        except Exception as e:
            logger.error(f"Error generating AI cost estimate: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "cost_data": {},
                "ai_response_raw": "",
                "model_used": self.model,
                "confidence_score": 0.0,
            }

    def _build_prompt(
        self,
        location: str,
        number_of_children: int,
        house_size_sqft: int,
        house_type: str,
    ) -> str:
        """Build the prompt for OpenAI API"""

        house_type_descriptions = {
            "single_family": "single-family detached home",
            "condo": "condominium or apartment",
            "townhouse": "townhouse",
            "multi_family": "multi-family home",
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
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1

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
            "estimated_home_price",
            "estimated_monthly_mortgage",
            "estimated_property_tax_annual",
            "estimated_insurance_annual",
            "estimated_utilities_monthly",
            "estimated_maintenance_annual",
            "estimated_childcare_annual",
            "estimated_education_annual",
            "estimated_child_healthcare_annual",
            "estimated_child_food_annual",
            "estimated_child_clothing_annual",
            "estimated_transportation_annual",
            "estimated_healthcare_annual",
            "estimated_groceries_annual",
        ]

        present_fields = sum(
            1
            for field in required_fields
            if field in cost_data and cost_data[field] is not None
        )
        completeness_score = present_fields / len(required_fields)

        # Check for reasonable values (basic sanity checks)
        reasonableness_score = 1.0

        if "estimated_home_price" in cost_data:
            home_price = float(cost_data["estimated_home_price"])
            if home_price < 50000 or home_price > 10000000:  # Unreasonable home prices
                reasonableness_score *= 0.5

        if "estimated_monthly_mortgage" in cost_data:
            mortgage = float(cost_data["estimated_monthly_mortgage"])
            if mortgage < 500 or mortgage > 50000:  # Unreasonable mortgage payments
                reasonableness_score *= 0.5

        # Final confidence score
        confidence = completeness_score * 0.7 + reasonableness_score * 0.3
        return min(confidence, 1.0)

    def validate_cost_data(self, cost_data: Dict[str, Any]) -> bool:
        """Validate that cost data contains reasonable values"""
        if not cost_data:
            return False

        # Check for required fields
        required_fields = ["estimated_home_price", "estimated_monthly_mortgage"]
        if not all(field in cost_data for field in required_fields):
            return False

        # Check for reasonable values
        try:
            home_price = float(cost_data.get("estimated_home_price", 0))
            mortgage = float(cost_data.get("estimated_monthly_mortgage", 0))

            if home_price <= 0 or mortgage <= 0:
                return False

            # Basic sanity check: mortgage should be roughly 0.4-0.8% of home price monthly
            expected_mortgage_range = (home_price * 0.004, home_price * 0.008)
            if not (
                expected_mortgage_range[0] <= mortgage <= expected_mortgage_range[1]
            ):
                logger.warning(
                    f"Mortgage payment {mortgage} seems unreasonable for home price {home_price}"
                )
                # Don't fail validation for this, just log warning

            return True

        except (ValueError, TypeError):
            return False

    def generate_contextual_cost_estimate(
        self,
        location: str,
        income: float,
        housing_spending,
        travel_spending,
        food_spending,
        leisure_spending,
        previous_cost: float = None,
        year: int = None,
    ) -> Dict[str, Any]:
        """
        Generate contextual cost estimates based on income and spending preferences.
        Costs are scaled based on income level and spending preferences.
        For the same location, costs should not change more than 2% per year.
        """

        prompt = self._build_contextual_prompt(
            location,
            income,
            housing_spending,
            travel_spending,
            food_spending,
            leisure_spending,
        )

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial planning expert. Generate realistic annual living costs based on location, income level, and spending preferences. Costs should be contextual to the person's income - a moderate spender making $1M will have different costs than a moderate spender making $100K. Always provide a total annual cost that never exceeds the given income.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1000,
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
            logger.error(
                f"Error generating contextual cost estimate with model {self.model}: {err_msg}"
            )
            if self.model != "gpt-3.5-turbo":
                try:
                    fallback_model = "gpt-3.5-turbo"
                    logger.info(f"Falling back to {fallback_model}")
                    response = openai.ChatCompletion.create(
                        model=fallback_model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a financial planning expert. Generate realistic annual living costs based on location, income level, and spending preferences. Costs should be contextual to the person's income - a moderate spender making $1M will have different costs than a moderate spender making $100K. Always provide a total annual cost that never exceeds the given income.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.3,
                        max_tokens=1000,
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
            return {
                "success": False,
                "error": f"Failed to generate cost estimate: {err_msg}",
            }

    def _build_contextual_prompt(
        self,
        location: str,
        income: float,
        housing_spending,
        travel_spending,
        food_spending,
        leisure_spending,
    ) -> str:
        """Build the prompt for contextual cost estimation"""

        # Convert percentages to descriptive text
        def percentage_to_description(pct):
            """Convert percentage (float) to descriptive text"""
            if isinstance(pct, str):
                # Handle legacy string values
                spending_descriptions = {
                    "very_little": "very frugal, minimal spending",
                    "less_than_average": "below average spending habits",
                    "average": "average spending habits",
                    "above_average": "above average spending habits",
                    "very_high": "very high spending, luxury lifestyle",
                }
                return spending_descriptions.get(pct, "average spending habits")

            # Convert percentage to description
            pct_float = float(pct)
            if pct_float < 10:
                return "very frugal, minimal spending"
            elif pct_float < 20:
                return "below average spending habits"
            elif pct_float < 35:
                return "average spending habits"
            elif pct_float < 50:
                return "above average spending habits"
            else:
                return "very high spending, luxury lifestyle"

        housing_desc = percentage_to_description(housing_spending)
        travel_desc = percentage_to_description(travel_spending)
        food_desc = percentage_to_description(food_spending)
        leisure_desc = percentage_to_description(leisure_spending)

        # Also include the actual percentages in the prompt
        housing_pct = (
            float(housing_spending) if not isinstance(housing_spending, str) else "N/A"
        )
        travel_pct = (
            float(travel_spending) if not isinstance(travel_spending, str) else "N/A"
        )
        food_pct = float(food_spending) if not isinstance(food_spending, str) else "N/A"
        leisure_pct = (
            float(leisure_spending) if not isinstance(leisure_spending, str) else "N/A"
        )

        return f"""
Please provide realistic annual living costs for someone living in {location} with an annual income of ${income:,.2f}.

IMPORTANT: Consider the significant cost differences between locations. {location} may have very different living costs compared to other cities. For example:
- High-cost areas (NYC, San Francisco, London): Expect 30-50% higher costs
- Medium-cost areas (Chicago, Austin, Seattle): Moderate costs
- Lower-cost areas (Phoenix, Dallas, Atlanta): 20-30% lower costs
- International locations: Consider currency, local economy, and cost of living

Spending preferences (as percentage of income):
- Housing: {housing_desc} ({housing_pct}% of income - consider local housing market prices)
- Travel: {travel_desc} ({travel_pct}% of income - factor in local transportation costs and travel opportunities)
- Food & Groceries: {food_desc} ({food_pct}% of income - account for local food prices and dining culture)
- Leisure: {leisure_desc} ({leisure_pct}% of income - consider local entertainment costs and lifestyle)

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
            start_idx = ai_response.find("{")
            end_idx = ai_response.rfind("}") + 1

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

                numbers = re.findall(r"\$?([\d,]+\.?\d*)", ai_response)
                if numbers:
                    total_cost = float(numbers[0].replace(",", ""))
                    return {
                        "total_annual_cost": Decimal(str(total_cost)),
                        "housing_cost": Decimal(str(total_cost * 0.4)),
                        "transportation_cost": Decimal(str(total_cost * 0.15)),
                        "food_cost": Decimal(str(total_cost * 0.2)),
                        "leisure_cost": Decimal(str(total_cost * 0.15)),
                        "other_costs": Decimal(str(total_cost * 0.1)),
                    }
                else:
                    return {"total_annual_cost": Decimal("0")}

        except (json.JSONDecodeError, ValueError, IndexError) as e:
            logger.error(f"Error parsing contextual AI response: {str(e)}")
            return {"total_annual_cost": Decimal("0")}

    def generate_income_cost_analysis(
        self,
        income_entries: list,
        spending_mode: str = "percentage_based",
        income_context: str = "",
    ) -> Dict[str, Any]:
        """
        Generate AI analysis of income and costs over time

        Args:
            income_entries: List of dictionaries containing year, income, costs, location, etc.
            spending_mode: Either "location_based" or "percentage_based"
            income_context: Optional user-provided context about their job/career/income situation

        Returns:
            Dictionary containing AI analysis and metadata
        """
        try:
            prompt = self._build_income_cost_prompt(
                income_entries, spending_mode, income_context=income_context
            )

            if not prompt or prompt == "No income data provided.":
                return {
                    "success": False,
                    "error": "No income data available for analysis.",
                    "analysis": "",
                    "model_used": self.model,
                }

            # Build request parameters
            request_params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a financial planning expert specializing in income and expense analysis. Provide insightful, actionable analysis of financial projections over time. Focus on trends, potential concerns, and recommendations. Be concise but comprehensive.",
                    },
                    {"role": "user", "content": prompt},
                ],
            }

            # Set token limit based on model type
            if "gpt-5-nano" in self.model.lower():
                request_params["max_completion_tokens"] = 4000
            else:
                request_params["max_tokens"] = 2000
                request_params["temperature"] = 0.7

            response = openai.ChatCompletion.create(**request_params)

            # Extract response content
            ai_response = None
            if hasattr(response, "choices") and response.choices:
                if hasattr(response.choices[0], "message"):
                    if hasattr(response.choices[0].message, "content"):
                        ai_response = response.choices[0].message.content

            if ai_response is None or not str(ai_response).strip():
                return {
                    "success": False,
                    "error": "AI returned an empty response. Please try again.",
                    "analysis": "",
                    "model_used": self.model,
                }

            return {
                "success": True,
                "analysis": str(ai_response).strip(),
                "model_used": self.model,
            }

        except Exception as e:
            logger.error(f"Error generating AI income/cost analysis: {str(e)}")
            import traceback

            logger.error(traceback.format_exc())

            error_msg = str(e)
            if "AuthenticationError" in str(type(e)) or "Invalid API key" in error_msg:
                error_msg = "OpenAI API key is not configured or invalid. Please contact support."
            elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
                error_msg = "OpenAI API quota exceeded. Please check your OpenAI account billing."
            elif "rate limit" in error_msg.lower():
                error_msg = (
                    "OpenAI API rate limit exceeded. Please try again in a moment."
                )

            return {
                "success": False,
                "error": error_msg,
                "analysis": "",
                "model_used": self.model,
            }

    def _build_income_cost_prompt(
        self,
        income_entries: list,
        spending_mode: str,
        income_context: str = "",
    ) -> str:
        """Build the prompt for income and cost analysis"""

        total_years = len(income_entries)
        if total_years == 0:
            return "No income data provided."

        first_year = income_entries[0]
        last_year = income_entries[-1]

        initial_income = float(
            first_year.get("after_tax_income", first_year.get("income", 0)) or 0
        )
        final_income = float(
            last_year.get("after_tax_income", last_year.get("income", 0)) or 0
        )
        income_growth = (
            ((final_income - initial_income) / initial_income * 100)
            if initial_income > 0
            else 0
        )

        initial_costs = float(first_year.get("costs", 0) or 0)
        final_costs = float(last_year.get("costs", 0) or 0)
        cost_growth = (
            ((final_costs - initial_costs) / initial_costs * 100)
            if initial_costs > 0
            else 0
        )

        avg_savings_rate = (
            sum(entry.get("savings_rate", 0) for entry in income_entries) / total_years
            if total_years > 0
            else 0
        )

        locations = set()
        for entry in income_entries:
            loc = entry.get("location", "Unknown")
            if loc and loc != "N/A" and loc != "Unknown":
                locations.add(loc)

        # Build detailed year-by-year data with annual changes
        mode_name = (
            "Location-Based"
            if spending_mode == "location_based"
            else "Percentage-Based"
        )

        data_summary = "\nYear-by-Year Financial Data:\n"
        data_summary += "=" * 100 + "\n"

        previous_income = None
        previous_costs = None
        previous_savings = None

        for entry in income_entries:
            year = entry.get("year", "N/A")
            income = float(entry.get("after_tax_income", entry.get("income", 0)) or 0)
            costs = float(entry.get("costs", 0) or 0)
            net_savings = float(entry.get("net_savings", income - costs) or 0)
            savings_rate = float(entry.get("savings_rate", 0) or 0)
            location = entry.get("location", "N/A")

            income_change = None
            income_change_pct = None
            costs_change = None
            costs_change_pct = None
            savings_change = None
            savings_change_pct = None

            if previous_income is not None:
                income_change = income - previous_income
                income_change_pct = (
                    (income_change / previous_income * 100)
                    if previous_income > 0
                    else 0
                )
                costs_change = costs - previous_costs
                costs_change_pct = (
                    (costs_change / previous_costs * 100) if previous_costs > 0 else 0
                )
                savings_change = net_savings - previous_savings
                savings_change_pct = (
                    (savings_change / previous_savings * 100)
                    if previous_savings != 0
                    else 0
                )

            data_summary += f"\nYear {year}:\n"
            data_summary += f"  After-Tax Income: ${income:,.0f}"
            if income_change is not None:
                change_indicator = (
                    "↑" if income_change > 0 else "↓" if income_change < 0 else "→"
                )
                data_summary += f" ({change_indicator} ${abs(income_change):,.0f}, {income_change_pct:+.1f}% from previous year)\n"
            else:
                data_summary += " (baseline year)\n"

            data_summary += f"  Costs: ${costs:,.0f}"
            if costs_change is not None:
                change_indicator = (
                    "↑" if costs_change > 0 else "↓" if costs_change < 0 else "→"
                )
                data_summary += f" ({change_indicator} ${abs(costs_change):,.0f}, {costs_change_pct:+.1f}% from previous year)\n"
            else:
                data_summary += " (baseline year)\n"

            data_summary += (
                f"  Net Savings: ${net_savings:,.0f} ({savings_rate:.1f}% savings rate)"
            )
            if savings_change is not None:
                change_indicator = (
                    "↑" if savings_change > 0 else "↓" if savings_change < 0 else "→"
                )
                data_summary += f" ({change_indicator} ${abs(savings_change):,.0f}, {savings_change_pct:+.1f}% from previous year)\n"
            else:
                data_summary += " (baseline year)\n"

            if location and location != "N/A" and location != "Unknown":
                data_summary += f"  Location: {location}\n"

            previous_income = income
            previous_costs = costs
            previous_savings = net_savings

        mode_description = (
            "location-based with cost of living adjustments"
            if spending_mode == "location_based"
            else "percentage-based (fixed percentage of after-tax income)"
        )

        # Add user context if provided
        context_section = ""
        if income_context:
            context_section = f"""

CRITICAL: User-Provided Context About Their Income Situation:
"{income_context}"

YOU MUST USE THIS CONTEXT to explain why the income numbers are what they are. Reference specific dollar amounts and percentages from the data below, and connect them to the user's job, career stage, industry, or other factors mentioned in the context above. For example, if they mention expecting a promotion in year 3, look at the income jump in that year and explain it using their context."""

        prompt = f"""You are a financial analyst. Analyze the following financial projection data and provide a comprehensive, QUANTITATIVE year-by-year analysis. You MUST reference specific dollar amounts, percentages, and numbers from the data below.

**Projection Period**: {first_year.get("year", "N/A")} to {last_year.get("year", "N/A")} ({total_years} years)

**Calculation Method**: {mode_name} ({mode_description})

{context_section}

**Summary Statistics** (USE THESE NUMBERS IN YOUR ANALYSIS):
- Initial After-Tax Income: ${initial_income:,.0f}
- Final After-Tax Income: ${final_income:,.0f}
- Total Income Growth: {income_growth:.1f}% over {total_years} years
- Initial Costs: ${initial_costs:,.0f}
- Final Costs: ${final_costs:,.0f}
- Total Cost Growth: {cost_growth:.1f}% over {total_years} years
- Average Savings Rate: {avg_savings_rate:.1f}%

**Locations**: {", ".join(locations) if locations else "N/A (Percentage-based calculation)"}

{data_summary}

CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE:

1. ALWAYS cite specific numbers from the data below (e.g., "In Year 2025, income increased from $X to $Y, a Z% increase").
2. Reference dollar amounts explicitly - don't just say "income increased", say "income increased from $75,000 to $82,500".
3. Calculate and mention percentages - show the math (e.g., "This represents a 10% increase").
4. If context was provided above, you MUST reference it when explaining income patterns. For example: "The income jump from $X to $Y in Year 2026 aligns with your mention of expecting a promotion that year."
5. DO NOT use markdown formatting (no **, no ##, no bold). Write in plain text only.

Provide a detailed year-by-year analysis:

1. Annual Income Changes (CITE SPECIFIC DOLLAR AMOUNTS AND PERCENTAGES):
   - For EACH year, state the exact after-tax income amount and the dollar/percentage change from the previous year
   - Example format: "Year 2025: Income is $X, which is $Y higher/lower than Year 2024 (a Z% increase/decrease)"
   - Explain whether income growth is accelerating, decelerating, or stable using the numbers
   - Compare income changes to typical career progression or inflation (cite percentages)
   - If context was provided, explain how the user's job/career situation relates to these specific income numbers

2. Annual Cost Changes (CITE SPECIFIC DOLLAR AMOUNTS AND PERCENTAGES):
   - For EACH year, state the exact cost amount and the dollar/percentage change from the previous year
   - Example format: "Year 2025: Costs are $X, which is $Y higher/lower than Year 2024 (a Z% increase/decrease)"
   - Compare cost growth rate to income growth rate using percentages
   - Identify when costs are outpacing income growth and by how much (show the math)
   - Explain factors driving cost changes (location changes, inflation, lifestyle) using the numbers

3. Annual Savings Changes (CITE SPECIFIC DOLLAR AMOUNTS AND PERCENTAGES):
   - For EACH year, state the exact net savings amount and savings rate percentage
   - Show how the gap between income and costs is changing in dollar terms
   - Calculate and state the impact: "Savings increased by $X (Y%) this year because income grew Z% while costs only grew W%"

4. Trends and Patterns (USE NUMBERS TO SUPPORT YOUR ANALYSIS):
   - Identify periods of rapid income growth with specific examples: "Years 2025-2027 show income growth of X%, Y%, and Z% respectively"
   - Identify concerning periods with numbers: "In Year 2026, costs grew X% while income only grew Y%, reducing savings by $Z"
   - Quantify the overall trajectory: "Over the projection period, income grew X% while costs grew Y%, resulting in..."

5. Key Insights (CONNECT NUMBERS TO MEANING):
   - Identify the best and worst years with specific dollar amounts and percentages
   - Explain concerning trends with numbers: "In Year X, savings dropped to $Y (Z% of income) because..."
   - Assess whether income growth is keeping pace: "Income grew X% over the period while costs grew Y%, meaning..."
   - If context was provided, connect these insights to the user's career/job situation

6. Recommendations (BE SPECIFIC WITH NUMBERS):
   - Suggest specific dollar amounts to save in challenging years
   - Reference the numbers: "In Year 2025, if you could reduce costs by $X (Y%), you'd increase savings by $Z"
   - If context was provided, give career-specific recommendations: "Given your mention of [context], consider [action] which could increase income by approximately X% based on industry standards"

REMEMBER: Always cite specific numbers, dollar amounts, and percentages. Never make vague statements. If context was provided, you MUST reference it when explaining income patterns. Make the analysis quantitative and data-driven. DO NOT use markdown formatting - write in plain text only."""

        return prompt

    @staticmethod
    def strip_markdown(text: str) -> str:
        """Remove markdown formatting from text"""
        if not text:
            return text
        # Remove **bold** and *italic*
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"\*(.*?)\*", r"\1", text)
        # Remove # headers
        text = re.sub(r"#+\s*(.*?)(?:\n|$)", r"\1\n", text)
        # Remove `code`
        text = re.sub(r"`(.*?)`", r"\1", text)
        # Remove __bold__ and _italic_ (alternative markdown)
        text = re.sub(r"__(.*?)__", r"\1", text)
        text = re.sub(r"_(.*?)_", r"\1", text)
        return text
