COLI_BY_STATE_2024 = {
    "West Virginia": 84.1,
    "Oklahoma": 85.7,
    "Kansas": 87.0,
    "Mississippi": 87.9,
    "Alabama": 88.0,
    "Arkansas": 88.7,
    "Missouri": 88.7,
    "Iowa": 89.7,
    "Michigan": 90.4,
    "Indiana": 90.5,
    "Tennessee": 90.5,
    "Georgia": 91.3,
    "North Dakota": 91.9,
    "Louisiana": 92.2,
    "South Dakota": 92.2,
    "Texas": 92.7,
    "Kentucky": 93.0,
    "Nebraska": 93.1,
    "New Mexico": 93.3,
    "Ohio": 94.2,
    "Illinois": 94.4,
    "Montana": 94.9,
    "Minnesota": 95.1,
    "Pennsylvania": 95.1,
    "Wyoming": 95.5,
    "South Carolina": 95.9,
    "Wisconsin": 97.0,
    "North Carolina": 97.8,
    "Virginia": 100.7,
    "Delaware": 100.8,
    "Nevada": 101.3,
    "Colorado": 102.0,
    "Idaho": 102.0,
    "Florida": 102.8,
    "Utah": 104.9,
    "Arizona": 111.5,
    "Oregon": 112.0,
    "Maine": 112.1,
    "Rhode Island": 112.2,
    "Connecticut": 112.3,
    "New Hampshire": 112.6,
    "Washington": 114.2,
    "Vermont": 114.4,
    "New Jersey": 114.6,
    "Maryland": 115.3,
    "New York": 123.3,
    "Alaska": 123.8,
    "District of Columbia": 141.9,
    "California": 144.8,
    "Massachusetts": 145.9,
    "Hawaii": 186.9,
    "United States": 103.59019607843136,
}

# Area-level multipliers within a state
# very_low = 0.5, less_than_average = 0.75, average = 1.0, above_average = 1.25, very_high = 2.0
AREA_LEVEL_MULTIPLIER = {
    "very_little": 0.5,  # aliasing to match spending choices wording if reused
    "very_low": 0.5,
    "less_than_average": 0.75,
    "average": 1.0,
    "above_average": 1.25,
    "very_high": 2.0,
}

# Spending category multipliers (used with weights):
# very_little 0.5, less_than_average 0.75, average 1.0, above_average 1.25, very_high 1.5
SPENDING_MULTIPLIER = {
    "very_little": 0.5,
    "less_than_average": 0.75,
    "average": 1.0,
    "above_average": 1.25,
    "very_high": 1.5,
}

# Weights for spending categories
SPENDING_WEIGHTS = {
    "housing": 0.4,
    "food": 0.3,
    "leisure": 0.2,
    "travel": 0.1,
}

BASE_US_AVG = 50000.0
