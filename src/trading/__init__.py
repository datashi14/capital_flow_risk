"""
Trading & Hedging Strategies Package
Sophisticated hedging recommendations for credit portfolios
"""

from .hedging import (
    HedgingStrategy,
    generate_hedging_recommendations,
    CDSHedgeAnalyzer,
    CrossAssetHedger,
    calculate_hedge_ratio,
    estimate_basis_risk
)

__all__ = [
    'HedgingStrategy',
    'generate_hedging_recommendations',
    'CDSHedgeAnalyzer',
    'CrossAssetHedger',
    'calculate_hedge_ratio',
    'estimate_basis_risk'
]

