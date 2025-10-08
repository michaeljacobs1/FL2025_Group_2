# Financial Projection System

## Overview

The Financial Projection System is a comprehensive Django application that provides advanced financial planning and projection capabilities. It allows users to create multiple investment scenarios, compare different strategies, and visualize their financial future.

## Features

### 1. Enhanced Models
- **ProjectionScenario**: Defines different investment scenarios (Conservative, Moderate, Aggressive, Custom)
- **ProjectionResult**: Stores detailed projection results with yearly breakdowns
- **ProjectionYearlyData**: Year-by-year projection data for detailed analysis
- **FinancialProfile**: User's financial information and goals
- **IncomeEntry**: Historical income data for trend analysis

### 2. Advanced Projection Service
- **ProjectionCalculator**: Core calculation engine with multiple scenarios
- **DataGenerator**: Utility for creating sample data for testing
- **Comprehensive calculations**: ROI, inflation adjustments, asset allocation

### 3. Multiple Scenarios
- **Conservative Growth**: 4% return, low risk
- **Moderate Growth**: 7% return, medium risk  
- **Aggressive Growth**: 10% return, high risk
- **Custom Scenarios**: User-defined parameters

### 4. Rich Visualizations
- Interactive charts using Chart.js
- Year-by-year breakdown tables
- Scenario comparison charts
- Net worth growth visualization

### 5. REST API
- Full CRUD operations for all models
- JSON serialization
- User-specific data filtering
- Authentication required

## Installation & Setup

### 1. Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Generate Sample Data
```bash
# Generate data for existing user
python manage.py generate_sample_data --username your_username

# Generate data for new demo user
python manage.py generate_sample_data
```

### 3. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

## Usage

### 1. Web Interface

#### Dashboard
- View financial profile status
- Access recent projections
- Quick actions for data entry

#### Financial Information
- Monthly income and expenses
- Current savings and goals
- Investment and retirement objectives

#### Income Timeline
- Historical income data
- Trend analysis
- Year-over-year comparisons

#### Projections & Results
- Run new projections with different scenarios
- View detailed results
- Compare multiple scenarios
- Generate sample data for testing

#### Scenario Comparison
- Side-by-side scenario analysis
- Visual comparisons
- Key insights and recommendations

### 2. API Endpoints

#### Financial Profiles
```
GET /api/financial-profiles/          # List user's financial profiles
POST /api/financial-profiles/        # Create new profile
GET /api/financial-profiles/{id}/    # Get specific profile
PUT /api/financial-profiles/{id}/    # Update profile
DELETE /api/financial-profiles/{id}/ # Delete profile
```

#### Projection Scenarios
```
GET /api/projection-scenarios/       # List scenarios
POST /api/projection-scenarios/     # Create scenario
GET /api/projection-scenarios/{id}/ # Get scenario
PUT /api/projection-scenarios/{id}/ # Update scenario
DELETE /api/projection-scenarios/{id}/ # Delete scenario
```

#### Projection Results
```
GET /api/projection-results/         # List projections
POST /api/projection-results/       # Create projection
GET /api/projection-results/{id}/   # Get projection details
PUT /api/projection-results/{id}/   # Update projection
DELETE /api/projection-results/{id}/ # Delete projection
```

#### Income Entries
```
GET /api/income-entries/            # List income entries
POST /api/income-entries/           # Create income entry
GET /api/income-entries/{id}/       # Get income entry
PUT /api/income-entries/{id}/      # Update income entry
DELETE /api/income-entries/{id}/   # Delete income entry
```

#### Personal Information
```
GET /api/personal-information/       # List personal info
POST /api/personal-information/     # Create personal info
GET /api/personal-information/{id}/ # Get personal info
PUT /api/personal-information/{id}/ # Update personal info
DELETE /api/personal-information/{id}/ # Delete personal info
```

### 3. Projection Calculations

#### Basic Projection
```python
from api.projection_service import ProjectionCalculator

calculator = ProjectionCalculator(user)
projection = calculator.calculate_projection(scenario_id, projected_years)
```

#### Scenario Comparison
```python
comparisons = calculator.compare_scenarios([scenario_id1, scenario_id2], projected_years)
```

#### Generate Sample Data
```python
from api.projection_service import DataGenerator

# Generate financial profile
profile = DataGenerator.generate_sample_financial_profile(user)

# Generate income timeline
DataGenerator.generate_sample_income_entries(user)

# Generate projections
projections = DataGenerator.generate_sample_projections(user)
```

## Data Models

### ProjectionScenario
- `name`: Scenario name
- `scenario_type`: conservative/moderate/aggressive/custom
- `annual_return_rate`: Expected annual return percentage
- `inflation_rate`: Expected inflation rate
- `risk_tolerance`: low/medium/high

### ProjectionResult
- `scenario`: Associated scenario
- `total_invested`: Total amount invested
- `projected_years`: Number of years projected
- `projected_valuation`: Final projected value
- `annual_return_rate`: Return rate used
- `inflation_rate`: Inflation rate used
- `monthly_contribution`: Monthly contribution amount
- `total_contributions`: Total contributions made
- `total_gains`: Total gains from investments
- `return_on_investment`: Calculated ROI percentage

### ProjectionYearlyData
- `projection`: Associated projection result
- `year`: Year number
- `beginning_balance`: Balance at start of year
- `contributions`: Contributions made during year
- `gains`: Gains earned during year
- `ending_balance`: Balance at end of year
- `inflation_adjusted_balance`: Balance adjusted for inflation

## Customization

### Adding New Scenarios
1. Create new ProjectionScenario instance
2. Set appropriate return and inflation rates
3. Define risk tolerance level

### Custom Calculations
1. Extend ProjectionCalculator class
2. Override calculation methods
3. Add new projection parameters

### Custom Visualizations
1. Modify Chart.js configurations
2. Add new chart types
3. Customize data formatting

## Security

- All API endpoints require authentication
- User-specific data filtering
- CSRF protection on forms
- Input validation and sanitization

## Performance

- Efficient database queries
- Cached calculations where appropriate
- Optimized chart rendering
- Responsive design for mobile devices

## Troubleshooting

### Common Issues

1. **Migration Errors**: Ensure all dependencies are installed
2. **Chart Not Displaying**: Check Chart.js CDN connection
3. **API Authentication**: Verify user is logged in
4. **Sample Data**: Run management command to generate data

### Debug Mode
```python
# In settings.py
DEBUG = True
```

### Logging
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Projection calculated successfully")
```

## Contributing

1. Follow Django best practices
2. Add tests for new features
3. Update documentation
4. Use proper error handling
5. Follow PEP 8 style guide

## License

This project is part of the Financial Planning application and follows the same license terms.

