"""
Tax bracket data for federal and state income taxes (2024 rates)
Using current 2024 tax brackets
"""

# Federal Tax Brackets 2024 (Single filer)
FEDERAL_TAX_BRACKETS_2024 = [
    {"min": 0, "max": 11600, "rate": 0.10},  # 10%
    {"min": 11600, "max": 47150, "rate": 0.12},  # 12%
    {"min": 47150, "max": 100525, "rate": 0.22},  # 22%
    {"min": 100525, "max": 191950, "rate": 0.24},  # 24%
    {"min": 191950, "max": 243725, "rate": 0.32},  # 32%
    {"min": 243725, "max": 609350, "rate": 0.35},  # 35%
    {"min": 609350, "max": float("inf"), "rate": 0.37},  # 37%
]

# Standard Deduction 2024
FEDERAL_STANDARD_DEDUCTION_2024 = 14600  # Single filer


STATE_TAX_RATES_2024 = {
    "Alabama": [
        {"min": 0, "max": 500, "rate": 0.02},
        {"min": 500, "max": 3000, "rate": 0.04},
        {"min": 3000, "max": float("inf"), "rate": 0.05},
    ],
    "Alaska": [],  # No state income tax
    "Arizona": [
        {"min": 0, "max": float("inf"), "rate": 0.025},  # Flat 2.5%
    ],
    "Arkansas": [
        {"min": 0, "max": 4800, "rate": 0.02},
        {"min": 4800, "max": 9600, "rate": 0.04},
        {"min": 9600, "max": float("inf"), "rate": 0.055},
    ],
    "California": [
        {"min": 0, "max": 10099, "rate": 0.01},
        {"min": 10099, "max": 23942, "rate": 0.02},
        {"min": 23942, "max": 37788, "rate": 0.04},
        {"min": 37788, "max": 52455, "rate": 0.06},
        {"min": 52455, "max": 66295, "rate": 0.08},
        {"min": 66295, "max": 338639, "rate": 0.093},
        {"min": 338639, "max": 406364, "rate": 0.103},
        {"min": 406364, "max": 677275, "rate": 0.113},
        {"min": 677275, "max": float("inf"), "rate": 0.123},
    ],
    "Colorado": [
        {"min": 0, "max": float("inf"), "rate": 0.044},  # Flat 4.4%
    ],
    "Connecticut": [
        {"min": 0, "max": 10000, "rate": 0.03},
        {"min": 10000, "max": 50000, "rate": 0.05},
        {"min": 50000, "max": 100000, "rate": 0.055},
        {"min": 100000, "max": 200000, "rate": 0.06},
        {"min": 200000, "max": 250000, "rate": 0.065},
        {"min": 250000, "max": 500000, "rate": 0.069},
        {"min": 500000, "max": float("inf"), "rate": 0.0699},
    ],
    "Delaware": [
        {"min": 0, "max": 2000, "rate": 0.022},
        {"min": 2000, "max": 5000, "rate": 0.039},
        {"min": 5000, "max": 10000, "rate": 0.048},
        {"min": 10000, "max": 20000, "rate": 0.052},
        {"min": 20000, "max": 25000, "rate": 0.0555},
        {"min": 25000, "max": 60000, "rate": 0.066},
        {"min": 60000, "max": float("inf"), "rate": 0.066},
    ],
    "Florida": [],  # No state income tax
    "Georgia": [
        {"min": 0, "max": 750, "rate": 0.01},
        {"min": 750, "max": 2250, "rate": 0.02},
        {"min": 2250, "max": 3750, "rate": 0.03},
        {"min": 3750, "max": 5250, "rate": 0.04},
        {"min": 5250, "max": 7000, "rate": 0.05},
        {"min": 7000, "max": float("inf"), "rate": 0.0575},
    ],
    "Hawaii": [
        {"min": 0, "max": 2400, "rate": 0.014},
        {"min": 2400, "max": 4800, "rate": 0.032},
        {"min": 4800, "max": 9600, "rate": 0.055},
        {"min": 9600, "max": 14400, "rate": 0.064},
        {"min": 14400, "max": 19200, "rate": 0.068},
        {"min": 19200, "max": 24000, "rate": 0.072},
        {"min": 24000, "max": 36000, "rate": 0.076},
        {"min": 36000, "max": 48000, "rate": 0.079},
        {"min": 48000, "max": 150000, "rate": 0.0825},
        {"min": 150000, "max": 175000, "rate": 0.09},
        {"min": 175000, "max": 200000, "rate": 0.10},
        {"min": 200000, "max": float("inf"), "rate": 0.11},
    ],
    "Idaho": [
        {"min": 0, "max": float("inf"), "rate": 0.058},  # Flat 5.8%
    ],
    "Illinois": [
        {"min": 0, "max": float("inf"), "rate": 0.0495},  # Flat 4.95%
    ],
    "Indiana": [
        {"min": 0, "max": float("inf"), "rate": 0.0315},  # Flat 3.15%
    ],
    "Iowa": [
        {"min": 0, "max": float("inf"), "rate": 0.04},  # Flat 4% (2024)
    ],
    "Kansas": [
        {"min": 0, "max": 15000, "rate": 0.031},
        {"min": 15000, "max": 30000, "rate": 0.0525},
        {"min": 30000, "max": float("inf"), "rate": 0.057},
    ],
    "Kentucky": [
        {"min": 0, "max": float("inf"), "rate": 0.045},  # Flat 4.5%
    ],
    "Louisiana": [
        {"min": 0, "max": 12500, "rate": 0.0185},
        {"min": 12500, "max": 50000, "rate": 0.035},
        {"min": 50000, "max": float("inf"), "rate": 0.0425},
    ],
    "Maine": [
        {"min": 0, "max": 24500, "rate": 0.058},
        {"min": 24500, "max": 58550, "rate": 0.0675},
        {"min": 58550, "max": float("inf"), "rate": 0.0715},
    ],
    "Maryland": [
        {"min": 0, "max": 1000, "rate": 0.02},
        {"min": 1000, "max": 2000, "rate": 0.03},
        {"min": 2000, "max": 3000, "rate": 0.04},
        {"min": 3000, "max": 100000, "rate": 0.0475},
        {"min": 100000, "max": 125000, "rate": 0.05},
        {"min": 125000, "max": 150000, "rate": 0.0525},
        {"min": 150000, "max": 250000, "rate": 0.055},
        {"min": 250000, "max": float("inf"), "rate": 0.0575},
    ],
    "Massachusetts": [
        {"min": 0, "max": float("inf"), "rate": 0.05},  # Flat 5%
    ],
    "Michigan": [
        {"min": 0, "max": float("inf"), "rate": 0.0425},  # Flat 4.25%
    ],
    "Minnesota": [
        {"min": 0, "max": 30390, "rate": 0.0535},
        {"min": 30390, "max": 98360, "rate": 0.0678},
        {"min": 98360, "max": 183340, "rate": 0.0785},
        {"min": 183340, "max": float("inf"), "rate": 0.0985},
    ],
    "Mississippi": [
        {"min": 0, "max": 10000, "rate": 0.04},
        {"min": 10000, "max": float("inf"), "rate": 0.05},
    ],
    "Missouri": [
        {"min": 0, "max": 1200, "rate": 0.015},
        {"min": 1200, "max": 2400, "rate": 0.02},
        {"min": 2400, "max": 3600, "rate": 0.025},
        {"min": 3600, "max": 4800, "rate": 0.03},
        {"min": 4800, "max": 6000, "rate": 0.035},
        {"min": 6000, "max": 7000, "rate": 0.04},
        {"min": 7000, "max": 8000, "rate": 0.045},
        {"min": 8000, "max": 9000, "rate": 0.05},
        {"min": 9000, "max": float("inf"), "rate": 0.054},
    ],
    "Montana": [
        {"min": 0, "max": float("inf"), "rate": 0.0485},  # Flat 4.85%
    ],
    "Nebraska": [
        {"min": 0, "max": 3700, "rate": 0.0246},
        {"min": 3700, "max": 22170, "rate": 0.0351},
        {"min": 22170, "max": 35730, "rate": 0.0501},
        {"min": 35730, "max": float("inf"), "rate": 0.0651},
    ],
    "Nevada": [],  # No state income tax
    "New Hampshire": [],  # No income tax on wages (only on interest/dividends)
    "New Jersey": [
        {"min": 0, "max": 20000, "rate": 0.014},
        {"min": 20000, "max": 35000, "rate": 0.0175},
        {"min": 35000, "max": 40000, "rate": 0.035},
        {"min": 40000, "max": 75000, "rate": 0.05525},
        {"min": 75000, "max": 500000, "rate": 0.0637},
        {"min": 500000, "max": 1000000, "rate": 0.0897},
        {"min": 1000000, "max": float("inf"), "rate": 0.1075},
    ],
    "New Mexico": [
        {"min": 0, "max": 5500, "rate": 0.017},
        {"min": 5500, "max": 11000, "rate": 0.032},
        {"min": 11000, "max": 16000, "rate": 0.047},
        {"min": 16000, "max": 210000, "rate": 0.049},
        {"min": 210000, "max": 315000, "rate": 0.052},
        {"min": 315000, "max": float("inf"), "rate": 0.059},
    ],
    "New York": [
        {"min": 0, "max": 8500, "rate": 0.04},
        {"min": 8500, "max": 11700, "rate": 0.045},
        {"min": 11700, "max": 13900, "rate": 0.0525},
        {"min": 13900, "max": 80650, "rate": 0.059},
        {"min": 80650, "max": 215400, "rate": 0.0609},
        {"min": 215400, "max": 1077550, "rate": 0.0685},
        {"min": 1077550, "max": 5000000, "rate": 0.0968},
        {"min": 5000000, "max": 25000000, "rate": 0.103},
        {"min": 25000000, "max": float("inf"), "rate": 0.109},
    ],
    "North Carolina": [
        {"min": 0, "max": float("inf"), "rate": 0.0475},  # Flat 4.75%
    ],
    "North Dakota": [
        {"min": 0, "max": 44525, "rate": 0.011},
        {"min": 44525, "max": 225975, "rate": 0.0204},
        {"min": 225975, "max": float("inf"), "rate": 0.0275},
    ],
    "Ohio": [
        {"min": 0, "max": 26050, "rate": 0.0},  # First bracket is 0%
        {"min": 26050, "max": 46350, "rate": 0.025},
        {"min": 46350, "max": 92650, "rate": 0.035},
        {"min": 92650, "max": 115650, "rate": 0.0375},
        {"min": 115650, "max": float("inf"), "rate": 0.0399},
    ],
    "Oklahoma": [
        {"min": 0, "max": 1000, "rate": 0.0025},
        {"min": 1000, "max": 2500, "rate": 0.0075},
        {"min": 2500, "max": 3750, "rate": 0.0175},
        {"min": 3750, "max": 4900, "rate": 0.0275},
        {"min": 4900, "max": 7200, "rate": 0.0375},
        {"min": 7200, "max": 8700, "rate": 0.0475},
        {"min": 8700, "max": float("inf"), "rate": 0.05},
    ],
    "Oregon": [
        {"min": 0, "max": 3950, "rate": 0.0475},
        {"min": 3950, "max": 9900, "rate": 0.0675},
        {"min": 9900, "max": 125000, "rate": 0.0875},
        {"min": 125000, "max": float("inf"), "rate": 0.0999},
    ],
    "Pennsylvania": [
        {"min": 0, "max": float("inf"), "rate": 0.0307},  # Flat 3.07%
    ],
    "Rhode Island": [
        {"min": 0, "max": 68200, "rate": 0.0375},
        {"min": 68200, "max": 155050, "rate": 0.0475},
        {"min": 155050, "max": float("inf"), "rate": 0.0599},
    ],
    "South Carolina": [
        {"min": 0, "max": 3200, "rate": 0.0},
        {"min": 3200, "max": 16040, "rate": 0.03},
        {"min": 16040, "max": float("inf"), "rate": 0.06},
    ],
    "South Dakota": [],  # No state income tax
    "Tennessee": [],  # No state income tax (repealed in 2021)
    "Texas": [],  # No state income tax
    "Utah": [
        {"min": 0, "max": float("inf"), "rate": 0.0485},  # Flat 4.85%
    ],
    "Vermont": [
        {"min": 0, "max": 45200, "rate": 0.0335},
        {"min": 45200, "max": 109450, "rate": 0.066},
        {"min": 109450, "max": 229350, "rate": 0.076},
        {"min": 229350, "max": float("inf"), "rate": 0.0875},
    ],
    "Virginia": [
        {"min": 0, "max": 3000, "rate": 0.02},
        {"min": 3000, "max": 5000, "rate": 0.03},
        {"min": 5000, "max": 17000, "rate": 0.05},
        {"min": 17000, "max": float("inf"), "rate": 0.0575},
    ],
    "Washington": [],  # No state income tax
    "West Virginia": [
        {"min": 0, "max": 10000, "rate": 0.03},
        {"min": 10000, "max": 25000, "rate": 0.04},
        {"min": 25000, "max": 40000, "rate": 0.045},
        {"min": 40000, "max": 60000, "rate": 0.06},
        {"min": 60000, "max": float("inf"), "rate": 0.065},
    ],
    "Wisconsin": [
        {"min": 0, "max": 13810, "rate": 0.035},
        {"min": 13810, "max": 27630, "rate": 0.044},
        {"min": 27630, "max": 304170, "rate": 0.053},
        {"min": 304170, "max": 405550, "rate": 0.0725},
        {"min": 405550, "max": float("inf"), "rate": 0.0765},
    ],
    "Wyoming": [],  # No state income tax
    "District of Columbia": [
        {"min": 0, "max": 10000, "rate": 0.04},
        {"min": 10000, "max": 40000, "rate": 0.06},
        {"min": 40000, "max": 60000, "rate": 0.065},
        {"min": 60000, "max": 250000, "rate": 0.085},
        {"min": 250000, "max": 500000, "rate": 0.0925},
        {"min": 500000, "max": 1000000, "rate": 0.0975},
        {"min": 1000000, "max": float("inf"), "rate": 0.1075},
    ],
}


def calculate_federal_tax(income: float) -> float:
    """
    Calculate federal income tax for a given income (2024 rates)
    Uses progressive marginal tax brackets with standard deduction
    Taxes are calculated only on income, using marginal rates
    """
    # Apply standard deduction
    taxable_income = max(0, income - FEDERAL_STANDARD_DEDUCTION_2024)

    if taxable_income <= 0:
        return 0.0

    total_tax = 0.0

    # Progressive tax calculation: calculate tax on each bracket
    for bracket in FEDERAL_TAX_BRACKETS_2024:
        bracket_min = bracket["min"]
        bracket_max = bracket["max"]
        rate = bracket["rate"]

        # Skip if taxable income is below this bracket
        if taxable_income <= bracket_min:
            break

        # Calculate amount of income in this bracket
        # Tax is calculated on the portion of income that falls in this bracket
        if taxable_income >= bracket_max:
            # All of this bracket applies
            taxable_in_bracket = bracket_max - bracket_min
        else:
            # Only part of this bracket applies
            taxable_in_bracket = taxable_income - bracket_min

        if taxable_in_bracket > 0:
            # Apply marginal rate to this bracket
            tax_in_bracket = taxable_in_bracket * rate
            total_tax += tax_in_bracket

    return total_tax


def calculate_state_tax(income: float, state: str) -> float:
    """
    Calculate state income tax for a given income and state (2024 rates)
    Uses progressive marginal tax brackets based on state location
    Taxes are calculated only on income, using marginal rates
    Returns 0 if state has no income tax
    """
    # Normalize state name (handle variations)
    state = state.strip()

    # Check if state has no income tax
    brackets = STATE_TAX_RATES_2024.get(state, [])
    if not brackets:
        return 0.0

    total_tax = 0.0

    # Progressive tax calculation: calculate tax on each bracket
    for bracket in brackets:
        bracket_min = bracket["min"]
        bracket_max = bracket["max"]
        rate = bracket["rate"]

        # Skip if income is below this bracket
        if income <= bracket_min:
            continue

        # Calculate amount of income in this bracket
        # Tax is calculated on the portion of income that falls in this bracket
        if income >= bracket_max:
            # All of this bracket applies
            taxable_in_bracket = bracket_max - bracket_min
        else:
            # Only part of this bracket applies
            taxable_in_bracket = income - bracket_min

        if taxable_in_bracket > 0:
            # Apply marginal rate to this bracket
            tax_in_bracket = taxable_in_bracket * rate
            total_tax += tax_in_bracket

        # If we've processed all brackets for this income, we're done
        if income <= bracket_max:
            break

    return total_tax


def calculate_total_tax(income: float, state: str) -> dict:
    """
    Calculate both federal and state taxes
    Returns a dictionary with federal_tax, state_tax, and total_tax
    """
    federal_tax = calculate_federal_tax(income)
    state_tax = calculate_state_tax(income, state)
    total_tax = federal_tax + state_tax

    return {
        "federal_tax": federal_tax,
        "state_tax": state_tax,
        "total_tax": total_tax,
        "after_tax_income": income - total_tax,
    }
