"""
Portfolio Aggregation & Risk-Weighted Assets (RWA)
Aggregates credit risk across portfolios and calculates capital requirements
"""
import numpy as np
import pandas as pd
from .core import PDModel, LGDModel, EADModel, ECLCalculator, calculate_rwa_simple, calculate_capital_requirement


class Portfolio:
    """
    Credit Portfolio with risk aggregation
    """
    
    def __init__(self, name="Portfolio"):
        self.name = name
        self.exposures = pd.DataFrame()
        self.pd_model = PDModel()
        self.lgd_model = LGDModel()
        self.ead_model = EADModel()
        self.ecl_calculator = ECLCalculator()
    
    def add_segment(self, segment_name, n_loans, avg_exposure, avg_pd, avg_lgd,
                   correlation=0.15, segment_type='retail'):
        """
        Add a portfolio segment
        
        segment_name: e.g., "Residential Mortgages", "SME Lending"
        n_loans: Number of loans in segment
        avg_exposure: Average exposure (EAD) per loan
        avg_pd: Average PD
        avg_lgd: Average LGD
        correlation: Asset correlation (0.15 for retail, 0.24 for corporate)
        """
        total_ead = n_loans * avg_exposure
        
        segment = pd.DataFrame({
            'segment': [segment_name],
            'type': [segment_type],
            'n_loans': [n_loans],
            'avg_exposure': [avg_exposure],
            'total_ead': [total_ead],
            'avg_pd': [avg_pd],
            'avg_lgd': [avg_lgd],
            'correlation': [correlation]
        })
        
        self.exposures = pd.concat([self.exposures, segment], ignore_index=True)
    
    def calculate_ecl(self):
        """
        Calculate ECL for entire portfolio
        """
        self.exposures['ecl_12m'] = (
            self.exposures['avg_pd'] * 
            self.exposures['avg_lgd'] * 
            self.exposures['total_ead']
        )
        
        # Lifetime ECL (simplified: 5x 12-month for stage 2/3)
        self.exposures['ecl_lifetime'] = self.exposures['ecl_12m'] * 5
        
        return self.exposures[['segment', 'ecl_12m', 'ecl_lifetime']]
    
    def calculate_rwa(self):
        """
        Calculate RWA for each segment using Basel IRB formula
        """
        rwa_list = []
        
        for idx, row in self.exposures.iterrows():
            rwa = calculate_rwa_simple(
                ead=row['total_ead'],
                pd=row['avg_pd'],
                lgd=row['avg_lgd'],
                correlation=row['correlation']
            )
            rwa_list.append(rwa)
        
        self.exposures['rwa'] = rwa_list
        
        return self.exposures[['segment', 'total_ead', 'rwa']]
    
    def calculate_capital(self, cet1_ratio=0.105, tier1_ratio=0.085):
        """
        Calculate capital requirements
        
        CET1 ratio: 10.5% (including buffers)
        Tier 1 ratio: 8.5%
        """
        if 'rwa' not in self.exposures.columns:
            self.calculate_rwa()
        
        total_rwa = self.exposures['rwa'].sum()
        
        capital = {
            'total_rwa': total_rwa,
            'cet1_required': total_rwa * cet1_ratio,
            'tier1_required': total_rwa * tier1_ratio,
            'total_capital_required': total_rwa * 0.125  # 12.5% total capital
        }
        
        return capital
    
    def stress_portfolio(self, pd_shock=1.5, lgd_shock=1.2, ead_shock=1.1):
        """
        Apply stress to portfolio
        
        pd_shock: Multiplier for PD (e.g., 1.5 = 50% increase)
        lgd_shock: Multiplier for LGD
        ead_shock: Multiplier for EAD
        """
        stressed = self.exposures.copy()
        
        stressed['avg_pd_stressed'] = stressed['avg_pd'] * pd_shock
        stressed['avg_lgd_stressed'] = np.minimum(stressed['avg_lgd'] * lgd_shock, 1.0)
        stressed['total_ead_stressed'] = stressed['total_ead'] * ead_shock
        
        # Recalculate ECL under stress
        stressed['ecl_stressed'] = (
            stressed['avg_pd_stressed'] * 
            stressed['avg_lgd_stressed'] * 
            stressed['total_ead_stressed']
        )
        
        # Recalculate RWA under stress
        rwa_stressed = []
        for idx, row in stressed.iterrows():
            rwa = calculate_rwa_simple(
                ead=row['total_ead_stressed'],
                pd=row['avg_pd_stressed'],
                lgd=row['avg_lgd_stressed'],
                correlation=row['correlation']
            )
            rwa_stressed.append(rwa)
        
        stressed['rwa_stressed'] = rwa_stressed
        
        return stressed
    
    def summary(self):
        """
        Print portfolio summary
        """
        print(f"\n{'='*60}")
        print(f"Portfolio: {self.name}")
        print(f"{'='*60}")
        
        if len(self.exposures) == 0:
            print("No exposures in portfolio")
            return
        
        # Calculate metrics if not already done
        if 'ecl_12m' not in self.exposures.columns:
            self.calculate_ecl()
        if 'rwa' not in self.exposures.columns:
            self.calculate_rwa()
        
        print(f"\nTotal Exposure (EAD): ${self.exposures['total_ead'].sum():,.0f}")
        print(f"Total ECL (12-month): ${self.exposures['ecl_12m'].sum():,.0f}")
        print(f"Total RWA: ${self.exposures['rwa'].sum():,.0f}")
        
        capital = self.calculate_capital()
        print(f"\nCapital Requirements:")
        print(f"  CET1 (10.5%): ${capital['cet1_required']:,.0f}")
        print(f"  Tier 1 (8.5%): ${capital['tier1_required']:,.0f}")
        print(f"  Total (12.5%): ${capital['total_capital_required']:,.0f}")
        
        print(f"\nSegment Breakdown:")
        print("-" * 60)
        for idx, row in self.exposures.iterrows():
            print(f"\n{row['segment']}:")
            print(f"  EAD: ${row['total_ead']:,.0f}")
            print(f"  Avg PD: {row['avg_pd']:.2%}")
            print(f"  Avg LGD: {row['avg_lgd']:.2%}")
            print(f"  ECL: ${row['ecl_12m']:,.0f}")
            print(f"  RWA: ${row['rwa']:,.0f}")


def create_example_au_portfolio():
    """
    Create example Australian bank portfolio
    """
    portfolio = Portfolio(name="Australian Bank Portfolio")
    
    # Residential mortgages: low PD, low LGD (well-secured)
    portfolio.add_segment(
        segment_name="Residential Mortgages",
        n_loans=50000,
        avg_exposure=500000,
        avg_pd=0.005,  # 0.5%
        avg_lgd=0.20,  # 20%
        correlation=0.15,
        segment_type='retail'
    )
    
    # Personal loans: higher PD, higher LGD (unsecured)
    portfolio.add_segment(
        segment_name="Personal Loans",
        n_loans=20000,
        avg_exposure=25000,
        avg_pd=0.03,  # 3%
        avg_lgd=0.45,  # 45%
        correlation=0.15,
        segment_type='retail'
    )
    
    # SME lending: moderate PD, moderate LGD
    portfolio.add_segment(
        segment_name="SME Lending",
        n_loans=5000,
        avg_exposure=200000,
        avg_pd=0.02,  # 2%
        avg_lgd=0.40,  # 40%
        correlation=0.20,
        segment_type='corporate'
    )
    
    # Commercial real estate: lower PD, lower LGD (secured by property)
    portfolio.add_segment(
        segment_name="Commercial Real Estate",
        n_loans=1000,
        avg_exposure=2000000,
        avg_pd=0.015,  # 1.5%
        avg_lgd=0.30,  # 30%
        correlation=0.18,
        segment_type='corporate'
    )
    
    return portfolio


def create_example_us_portfolio():
    """
    Create example US bank portfolio
    """
    portfolio = Portfolio(name="US Bank Portfolio")
    
    # Residential mortgages
    portfolio.add_segment(
        segment_name="Residential Mortgages",
        n_loans=80000,
        avg_exposure=350000,
        avg_pd=0.008,  # 0.8%
        avg_lgd=0.25,  # 25%
        correlation=0.15,
        segment_type='retail'
    )
    
    # Credit cards: high PD, high LGD (unsecured)
    portfolio.add_segment(
        segment_name="Credit Cards",
        n_loans=500000,
        avg_exposure=5000,
        avg_pd=0.05,  # 5%
        avg_lgd=0.70,  # 70%
        correlation=0.15,
        segment_type='retail'
    )
    
    # Auto loans
    portfolio.add_segment(
        segment_name="Auto Loans",
        n_loans=100000,
        avg_exposure=30000,
        avg_pd=0.02,  # 2%
        avg_lgd=0.35,  # 35%
        correlation=0.15,
        segment_type='retail'
    )
    
    # Commercial & Industrial loans
    portfolio.add_segment(
        segment_name="C&I Loans",
        n_loans=10000,
        avg_exposure=500000,
        avg_pd=0.025,  # 2.5%
        avg_lgd=0.45,  # 45%
        correlation=0.24,
        segment_type='corporate'
    )
    
    # Commercial real estate
    portfolio.add_segment(
        segment_name="Commercial Real Estate",
        n_loans=5000,
        avg_exposure=1500000,
        avg_pd=0.018,  # 1.8%
        avg_lgd=0.35,  # 35%
        correlation=0.18,
        segment_type='corporate'
    )
    
    return portfolio


def compare_portfolios(portfolio_au, portfolio_us):
    """
    Compare two portfolios side by side
    """
    # Calculate metrics for both
    portfolio_au.calculate_ecl()
    portfolio_au.calculate_rwa()
    portfolio_us.calculate_ecl()
    portfolio_us.calculate_rwa()
    
    capital_au = portfolio_au.calculate_capital()
    capital_us = portfolio_us.calculate_capital()
    
    comparison = pd.DataFrame({
        'Metric': [
            'Total EAD',
            'Total ECL (12m)',
            'Total RWA',
            'CET1 Required',
            'ECL / EAD (%)',
            'RWA / EAD (%)'
        ],
        'Australia': [
            f"${portfolio_au.exposures['total_ead'].sum():,.0f}",
            f"${portfolio_au.exposures['ecl_12m'].sum():,.0f}",
            f"${portfolio_au.exposures['rwa'].sum():,.0f}",
            f"${capital_au['cet1_required']:,.0f}",
            f"{portfolio_au.exposures['ecl_12m'].sum() / portfolio_au.exposures['total_ead'].sum() * 100:.3f}%",
            f"{portfolio_au.exposures['rwa'].sum() / portfolio_au.exposures['total_ead'].sum() * 100:.1f}%"
        ],
        'United States': [
            f"${portfolio_us.exposures['total_ead'].sum():,.0f}",
            f"${portfolio_us.exposures['ecl_12m'].sum():,.0f}",
            f"${portfolio_us.exposures['rwa'].sum():,.0f}",
            f"${capital_us['cet1_required']:,.0f}",
            f"{portfolio_us.exposures['ecl_12m'].sum() / portfolio_us.exposures['total_ead'].sum() * 100:.3f}%",
            f"{portfolio_us.exposures['rwa'].sum() / portfolio_us.exposures['total_ead'].sum() * 100:.1f}%"
        ]
    })
    
    return comparison


if __name__ == "__main__":
    print("\n" + "="*70)
    print("CREDIT PORTFOLIO ANALYSIS - AUSTRALIA vs UNITED STATES")
    print("="*70)
    
    # Create example portfolios
    au_portfolio = create_example_au_portfolio()
    us_portfolio = create_example_us_portfolio()
    
    # Show summaries
    au_portfolio.summary()
    us_portfolio.summary()
    
    # Compare portfolios
    print("\n" + "="*70)
    print("PORTFOLIO COMPARISON")
    print("="*70)
    comparison = compare_portfolios(au_portfolio, us_portfolio)
    print("\n" + comparison.to_string(index=False))
    
    # Stress test
    print("\n" + "="*70)
    print("STRESS TEST: SEVERE RECESSION")
    print("="*70)
    print("Assumptions: PD +50%, LGD +20%, EAD +10%")
    
    au_stressed = au_portfolio.stress_portfolio(pd_shock=1.5, lgd_shock=1.2, ead_shock=1.1)
    us_stressed = us_portfolio.stress_portfolio(pd_shock=1.5, lgd_shock=1.2, ead_shock=1.1)
    
    print(f"\nAustralia - Stressed ECL: ${au_stressed['ecl_stressed'].sum():,.0f}")
    print(f"  vs. Base ECL: ${au_portfolio.exposures['ecl_12m'].sum():,.0f}")
    print(f"  Increase: ${(au_stressed['ecl_stressed'].sum() - au_portfolio.exposures['ecl_12m'].sum()):,.0f}")
    
    print(f"\nUnited States - Stressed ECL: ${us_stressed['ecl_stressed'].sum():,.0f}")
    print(f"  vs. Base ECL: ${us_portfolio.exposures['ecl_12m'].sum():,.0f}")
    print(f"  Increase: ${(us_stressed['ecl_stressed'].sum() - us_portfolio.exposures['ecl_12m'].sum()):,.0f}")
