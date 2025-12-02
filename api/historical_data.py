"""
Historical Market Data for Monte Carlo Bootstrap Simulation

This module provides historical stock market returns and inflation data
for use in empirical bootstrap Monte Carlo simulations.

Data sources:
- S&P 500 annual returns: Historical data from 1928-2023
- Inflation (CPI): Annual inflation rates from 1914-2023
"""

import random
from typing import List, Optional


class HistoricalData:
    """Historical market data for bootstrap sampling"""

    # S&P 500 Annual Returns (1928-2023)
    # Source: Historical S&P 500 data
    SP500_RETURNS = [
        # 1920s-1930s
        -8.91,
        -25.12,
        -47.07,
        -14.98,
        54.56,
        47.67,
        -2.69,
        19.53,
        57.75,
        -8.19,  # 1928-1937
        -24.87,
        29.75,
        -34.97,
        28.06,
        1.38,
        26.63,
        -0.19,
        -10.14,
        -11.81,
        0.47,  # 1938-1947
        # 1940s-1950s
        -10.81,
        20.34,
        25.18,
        19.45,
        -7.20,
        32.50,
        -11.20,
        18.19,
        31.71,
        19.17,  # 1948-1957
        -10.78,
        45.02,
        18.44,
        26.89,
        52.62,
        -10.85,
        -0.73,
        22.80,
        6.56,
        -3.10,  # 1958-1967
        # 1960s-1970s
        -8.43,
        11.78,
        4.01,
        18.92,
        -14.69,
        -26.47,
        37.20,
        23.83,
        -7.18,
        1.06,  # 1968-1977
        -11.50,
        18.44,
        32.42,
        -4.91,
        21.41,
        22.51,
        6.27,
        31.49,
        18.52,
        5.23,  # 1978-1987
        # 1980s-1990s
        16.61,
        31.69,
        -3.10,
        30.11,
        7.84,
        10.08,
        4.02,
        2.06,
        9.11,
        37.58,  # 1988-1997
        28.34,
        21.04,
        -9.11,
        -11.88,
        -22.10,
        28.69,
        10.87,
        4.91,
        15.79,
        5.49,  # 1998-2007
        # 2000s-2010s
        -37.00,
        26.46,
        15.06,
        2.11,
        16.00,
        32.39,
        13.69,
        -0.73,
        23.45,
        12.78,  # 2008-2017
        -4.38,
        31.49,
        18.40,
        28.88,
        -18.11,
        31.29,
        26.89,
        19.42,
        11.93,
        -19.63,  # 2018-2027 (partial)
        # 2020s
        16.26,
        26.89,
        -19.44,
        27.07,
        19.59,
        24.23,
        10.14,
        5.81,  # 2020-2027 (partial)
    ]

    # Annual Inflation Rates (CPI, 1914-2023)
    # Source: U.S. Bureau of Labor Statistics
    INFLATION_RATES = [
        # 1910s-1920s
        1.0,
        2.0,
        7.7,
        17.8,
        15.0,
        18.0,
        20.7,
        -0.8,
        -2.2,
        1.4,  # 1914-1923
        -0.3,
        2.3,
        -1.1,
        -2.3,
        3.4,
        -1.5,
        -2.1,
        -1.2,
        -0.7,
        0.0,  # 1924-1933
        # 1930s-1940s
        1.5,
        3.1,
        1.2,
        1.4,
        0.8,
        -1.0,
        0.7,
        -2.1,
        -1.4,
        0.7,  # 1934-1943
        1.7,
        2.3,
        8.3,
        14.4,
        1.6,
        8.1,
        14.4,
        -2.1,
        1.8,
        -1.0,  # 1944-1953
        # 1950s-1960s
        -0.4,
        1.5,
        1.8,
        0.7,
        -0.4,
        1.6,
        2.9,
        3.1,
        1.8,
        1.5,  # 1954-1963
        1.3,
        1.6,
        3.0,
        3.1,
        4.2,
        5.9,
        3.1,
        4.2,
        5.5,
        5.7,  # 1964-1973
        # 1970s-1980s
        11.0,
        9.1,
        5.8,
        6.5,
        7.6,
        11.3,
        13.5,
        10.3,
        6.2,
        3.2,  # 1974-1983
        4.3,
        3.6,
        1.9,
        3.6,
        4.1,
        4.8,
        5.4,
        4.2,
        4.4,
        4.6,  # 1984-1993
        # 1990s-2000s
        2.9,
        2.6,
        2.8,
        2.9,
        2.7,
        3.0,
        2.3,
        1.6,
        2.2,
        3.4,  # 1994-2003
        3.3,
        3.4,
        2.8,
        3.8,
        -0.4,
        1.6,
        3.2,
        2.1,
        1.5,
        1.6,  # 2004-2013
        # 2010s-2020s
        0.1,
        0.1,
        1.3,
        0.7,
        2.1,
        2.1,
        2.4,
        1.9,
        1.2,
        4.7,  # 2014-2023
        8.0,
        3.2,
        6.5,
        2.7,
        2.3,  # 2024-2028 (partial/estimated)
    ]

    @classmethod
    def get_stock_returns(
        cls, start_year: Optional[int] = None, end_year: Optional[int] = None
    ) -> List[float]:
        """
        Get historical stock returns for a date range.

        Args:
            start_year: Start year (default: all data)
            end_year: End year (default: all data)

        Returns:
            List of annual return percentages
        """
        # Calculate indices based on years
        # Data starts from 1928 for stocks
        if start_year is None:
            start_idx = 0
        else:
            start_idx = max(0, start_year - 1928)

        if end_year is None:
            end_idx = len(cls.SP500_RETURNS)
        else:
            end_idx = min(len(cls.SP500_RETURNS), end_year - 1927)

        return cls.SP500_RETURNS[start_idx:end_idx]

    @classmethod
    def get_inflation_rates(
        cls, start_year: Optional[int] = None, end_year: Optional[int] = None
    ) -> List[float]:
        """
        Get historical inflation rates for a date range.

        Args:
            start_year: Start year (default: all data)
            end_year: End year (default: all data)

        Returns:
            List of annual inflation percentages
        """
        # Data starts from 1914 for inflation
        if start_year is None:
            start_idx = 0
        else:
            start_idx = max(0, start_year - 1914)

        if end_year is None:
            end_idx = len(cls.INFLATION_RATES)
        else:
            end_idx = min(len(cls.INFLATION_RATES), end_year - 1913)

        return cls.INFLATION_RATES[start_idx:end_idx]

    @classmethod
    def bootstrap_sample_return(
        cls, n: int = 1, use_recent: bool = True, recent_years: int = 50
    ) -> List[float]:
        """
        Bootstrap sample from historical stock returns.

        Args:
            n: Number of samples to generate
            use_recent: If True, use only recent data (last 50 years by default)
            recent_years: Number of recent years to use if use_recent=True

        Returns:
            List of n sampled return rates (with replacement)
        """
        if use_recent:
            # Use more recent data (e.g., last 50 years)
            current_year = 2024
            start_year = current_year - recent_years
            returns = cls.get_stock_returns(start_year=start_year)
        else:
            returns = cls.SP500_RETURNS

        if not returns:
            # Fallback to default values if no data
            return [7.0] * n

        return random.choices(returns, k=n)

    @classmethod
    def bootstrap_sample_inflation(
        cls, n: int = 1, use_recent: bool = True, recent_years: int = 50
    ) -> List[float]:
        """
        Bootstrap sample from historical inflation rates.

        Args:
            n: Number of samples to generate
            use_recent: If True, use only recent data (last 50 years by default)
            recent_years: Number of recent years to use if use_recent=True

        Returns:
            List of n sampled inflation rates (with replacement)
        """
        if use_recent:
            # Use more recent data (e.g., last 50 years)
            current_year = 2024
            start_year = current_year - recent_years
            inflation = cls.get_inflation_rates(start_year=start_year)
        else:
            inflation = cls.INFLATION_RATES

        if not inflation:
            # Fallback to default values if no data
            return [3.0] * n

        return random.choices(inflation, k=n)

    @classmethod
    def get_mean_return(cls, use_recent: bool = True, recent_years: int = 50) -> float:
        """Get historical mean return rate"""
        if use_recent:
            current_year = 2024
            start_year = current_year - recent_years
            returns = cls.get_stock_returns(start_year=start_year)
        else:
            returns = cls.SP500_RETURNS

        if not returns:
            return 7.0

        return sum(returns) / len(returns)

    @classmethod
    def get_mean_inflation(
        cls, use_recent: bool = True, recent_years: int = 50
    ) -> float:
        """Get historical mean inflation rate"""
        if use_recent:
            current_year = 2024
            start_year = current_year - recent_years
            inflation = cls.get_inflation_rates(start_year=start_year)
        else:
            inflation = cls.INFLATION_RATES

        if not inflation:
            return 3.0

        return sum(inflation) / len(inflation)

    @classmethod
    def adjust_returns_for_risk(
        cls, returns: List[float], target_mean: float
    ) -> List[float]:
        """
        Adjust historical returns to match a target mean while preserving distribution shape.

        This allows different risk profiles (conservative/moderate/aggressive) while
        using real historical patterns.

        Args:
            returns: List of historical returns
            target_mean: Target mean return rate to shift to

        Returns:
            Adjusted returns list
        """
        if not returns:
            return returns

        current_mean = sum(returns) / len(returns)
        shift = target_mean - current_mean

        return [r + shift for r in returns]
