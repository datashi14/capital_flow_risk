"""
Credit Risk Modeling Package
Contains core PD/LGD/EAD models and portfolio aggregation
"""

from .core import (
    CreditAvailabilityIndex,
    PDModel,
    LGDModel,
    EADModel,
    ECLCalculator,
    calculate_rwa_simple,
    calculate_capital_requirement
)

from .portfolio import (
    Portfolio,
    create_example_au_portfolio,
    create_example_us_portfolio,
    compare_portfolios
)

__all__ = [
    'CreditAvailabilityIndex',
    'PDModel',
    'LGDModel',
    'EADModel',
    'ECLCalculator',
    'calculate_rwa_simple',
    'calculate_capital_requirement',
    'Portfolio',
    'create_example_au_portfolio',
    'create_example_us_portfolio',
    'compare_portfolios'
]

