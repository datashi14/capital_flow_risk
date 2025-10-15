"""
Stress Testing Scenarios
Implements various macro stress scenarios for capital and credit risk analysis
"""
import numpy as np
import pandas as pd


class StressScenario:
    """
    Base class for stress scenarios
    """
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.shocks = {}
    
    def apply(self, df_base):
        """
        Apply scenario shocks to baseline data
        Returns: DataFrame with stressed variables
        """
        df_stressed = df_base.copy()
        
        for var, shock in self.shocks.items():
            if var in df_stressed.columns:
                if isinstance(shock, dict):
                    # Time-varying shock
                    if 'instant' in shock:
                        df_stressed[var] = df_stressed[var] + shock['instant']
                    elif 'growth' in shock:
                        # Apply growth rate
                        df_stressed[var] = df_stressed[var] * (1 + shock['growth'])
                else:
                    # Simple additive shock
                    df_stressed[var] = df_stressed[var] + shock
        
        return df_stressed
    
    def __repr__(self):
        return f"StressScenario('{self.name}')"


class TighteningScenario(StressScenario):
    """
    Monetary Tightening Scenario
    - Interest rates surge +200 bps
    - Unemployment rises +2 pp
    - Housing prices fall -10%
    - Credit growth slows significantly
    """
    
    def __init__(self, rate_shock=2.0, unemployment_shock=2.0, housing_shock=-10.0):
        super().__init__(
            name="Monetary Tightening",
            description="Aggressive rate hikes to combat inflation"
        )
        
        self.rate_shock = rate_shock
        self.unemployment_shock = unemployment_shock
        self.housing_shock = housing_shock
    
    def apply(self, df_base):
        """
        Apply tightening scenario
        """
        df_stressed = df_base.copy()
        
        # Rate shock (instantaneous)
        if 'cash_rate' in df_stressed.columns:
            df_stressed['cash_rate'] = df_stressed['cash_rate'] + self.rate_shock
        if 'fed_funds_rate' in df_stressed.columns:
            df_stressed['fed_funds_rate'] = df_stressed['fed_funds_rate'] + self.rate_shock
        
        # Unemployment shock (gradual over 12 months)
        n = len(df_stressed)
        unemployment_path = np.linspace(0, self.unemployment_shock, min(12, n))
        unemployment_path = np.concatenate([unemployment_path, 
                                           np.full(n - len(unemployment_path), self.unemployment_shock)])
        
        if 'unemployment_rate' in df_stressed.columns:
            df_stressed['unemployment_rate'] = df_stressed['unemployment_rate'] + unemployment_path
        
        # Housing shock (gradual decline over 24 months)
        if 'housing_price_index' in df_stressed.columns or 'housing_price_growth' in df_stressed.columns:
            housing_path = np.linspace(0, self.housing_shock, min(24, n))
            housing_path = np.concatenate([housing_path,
                                          np.full(n - len(housing_path), self.housing_shock)])
            
            if 'housing_price_growth' in df_stressed.columns:
                df_stressed['housing_price_growth'] = df_stressed['housing_price_growth'] + housing_path
        
        # Credit growth slows (falls by 50%)
        if 'credit_growth_housing' in df_stressed.columns:
            df_stressed['credit_growth_housing'] = df_stressed['credit_growth_housing'] * 0.5
        if 'credit_growth' in df_stressed.columns:
            df_stressed['credit_growth'] = df_stressed['credit_growth'] * 0.5
        
        # Spread widens
        if 'bbsw_spread' in df_stressed.columns:
            df_stressed['bbsw_spread'] = df_stressed['bbsw_spread'] + 0.5
        if 'baa_spread' in df_stressed.columns:
            df_stressed['baa_spread'] = df_stressed['baa_spread'] + 0.5
        
        return df_stressed


class SoftLandingScenario(StressScenario):
    """
    Soft Landing Scenario
    - Rates rise modestly +50 bps
    - Unemployment rises slightly +0.5 pp
    - Housing prices flat to slightly down
    - Credit growth moderates
    """
    
    def __init__(self, rate_shock=0.5, unemployment_shock=0.5, housing_shock=0.0):
        super().__init__(
            name="Soft Landing",
            description="Gradual slowdown, inflation controlled without recession"
        )
        
        self.rate_shock = rate_shock
        self.unemployment_shock = unemployment_shock
        self.housing_shock = housing_shock
    
    def apply(self, df_base):
        """
        Apply soft landing scenario
        """
        df_stressed = df_base.copy()
        
        # Modest rate increase
        if 'cash_rate' in df_stressed.columns:
            df_stressed['cash_rate'] = df_stressed['cash_rate'] + self.rate_shock
        if 'fed_funds_rate' in df_stressed.columns:
            df_stressed['fed_funds_rate'] = df_stressed['fed_funds_rate'] + self.rate_shock
        
        # Small unemployment increase
        if 'unemployment_rate' in df_stressed.columns:
            df_stressed['unemployment_rate'] = df_stressed['unemployment_rate'] + self.unemployment_shock
        
        # Housing flat
        if 'housing_price_growth' in df_stressed.columns:
            df_stressed['housing_price_growth'] = df_stressed['housing_price_growth'] + self.housing_shock
        
        # Credit growth moderates (85% of baseline)
        if 'credit_growth_housing' in df_stressed.columns:
            df_stressed['credit_growth_housing'] = df_stressed['credit_growth_housing'] * 0.85
        if 'credit_growth' in df_stressed.columns:
            df_stressed['credit_growth'] = df_stressed['credit_growth'] * 0.85
        
        return df_stressed


class FundingShockScenario(StressScenario):
    """
    Funding Shock Scenario
    - Bank funding spreads surge +75 bps
    - Liquidity stress
    - Credit availability tightens
    - SME lending falls sharply
    """
    
    def __init__(self, spread_shock=0.75, credit_shock=-15):
        super().__init__(
            name="Funding Shock",
            description="Sudden tightening in bank funding markets"
        )
        
        self.spread_shock = spread_shock
        self.credit_shock = credit_shock  # percentage points
    
    def apply(self, df_base):
        """
        Apply funding shock scenario
        """
        df_stressed = df_base.copy()
        
        # Spread shock
        if 'bbsw_spread' in df_stressed.columns:
            df_stressed['bbsw_spread'] = df_stressed['bbsw_spread'] + self.spread_shock
            df_stressed['bbsw_rate'] = df_stressed['cash_rate'] + df_stressed['bbsw_spread']
        
        if 'baa_spread' in df_stressed.columns:
            df_stressed['baa_spread'] = df_stressed['baa_spread'] + self.spread_shock
        
        if 'funding_cost' in df_stressed.columns:
            df_stressed['funding_cost'] = df_stressed['funding_cost'] + self.spread_shock
        
        # Credit growth collapses
        if 'credit_growth_housing' in df_stressed.columns:
            df_stressed['credit_growth_housing'] = df_stressed['credit_growth_housing'] + self.credit_shock
        if 'credit_growth_business' in df_stressed.columns:
            df_stressed['credit_growth_business'] = df_stressed['credit_growth_business'] + self.credit_shock * 1.5
        if 'credit_growth' in df_stressed.columns:
            df_stressed['credit_growth'] = df_stressed['credit_growth'] + self.credit_shock
        
        # Liquidity ratio falls
        if 'liquidity_ratio' in df_stressed.columns:
            df_stressed['liquidity_ratio'] = df_stressed['liquidity_ratio'] * 0.9
        
        return df_stressed


class SevereRecessionScenario(StressScenario):
    """
    Severe Recession Scenario (like 2008-09)
    - Unemployment spikes to 10%+
    - Housing crashes -25%
    - Rates cut to near zero
    - Credit markets freeze
    """
    
    def __init__(self):
        super().__init__(
            name="Severe Recession",
            description="2008-style financial crisis"
        )
    
    def apply(self, df_base):
        """
        Apply severe recession scenario
        """
        df_stressed = df_base.copy()
        n = len(df_stressed)
        
        # Unemployment spikes to 10%
        unemployment_path = np.linspace(0, 5, min(12, n))
        unemployment_path = np.concatenate([unemployment_path,
                                           np.full(n - len(unemployment_path), 5)])
        
        if 'unemployment_rate' in df_stressed.columns:
            df_stressed['unemployment_rate'] = df_stressed['unemployment_rate'] + unemployment_path
            df_stressed['unemployment_rate'] = np.minimum(df_stressed['unemployment_rate'], 12)
        
        # Housing crash -25%
        housing_path = np.linspace(0, -25, min(18, n))
        housing_path = np.concatenate([housing_path,
                                      np.full(n - len(housing_path), -25)])
        
        if 'housing_price_growth' in df_stressed.columns:
            df_stressed['housing_price_growth'] = housing_path
        
        # Rates cut aggressively
        if 'cash_rate' in df_stressed.columns:
            df_stressed['cash_rate'] = np.maximum(df_stressed['cash_rate'] - 3.0, 0.1)
        if 'fed_funds_rate' in df_stressed.columns:
            df_stressed['fed_funds_rate'] = np.maximum(df_stressed['fed_funds_rate'] - 4.0, 0.1)
        
        # Credit growth collapses
        if 'credit_growth_housing' in df_stressed.columns:
            df_stressed['credit_growth_housing'] = df_stressed['credit_growth_housing'] - 20
        if 'credit_growth' in df_stressed.columns:
            df_stressed['credit_growth'] = df_stressed['credit_growth'] - 20
        
        # Spreads explode
        if 'bbsw_spread' in df_stressed.columns:
            df_stressed['bbsw_spread'] = df_stressed['bbsw_spread'] + 2.0
        if 'baa_spread' in df_stressed.columns:
            df_stressed['baa_spread'] = df_stressed['baa_spread'] + 3.0
        
        return df_stressed


class CustomScenario(StressScenario):
    """
    Custom scenario with user-defined shocks
    """
    
    def __init__(self, name, shocks):
        """
        shocks: dict of {variable: shock_value}
        Example: {'cash_rate': 1.5, 'unemployment_rate': 1.0}
        """
        super().__init__(name, "Custom user-defined scenario")
        self.custom_shocks = shocks
    
    def apply(self, df_base):
        """
        Apply custom shocks
        """
        df_stressed = df_base.copy()
        
        for var, shock in self.custom_shocks.items():
            if var in df_stressed.columns:
                df_stressed[var] = df_stressed[var] + shock
        
        return df_stressed


def apply_scenario_to_portfolio(portfolio, scenario, df_macro):
    """
    Apply macro scenario to portfolio and recalculate risk metrics
    
    portfolio: Portfolio object from modeling.portfolio
    scenario: StressScenario object
    df_macro: DataFrame with macro variables
    
    Returns: Stressed portfolio metrics
    """
    from ..modeling.core import PDModel, LGDModel
    
    # Apply scenario to macro data
    df_stressed = scenario.apply(df_macro)
    
    # Get latest stressed values
    latest = df_stressed.iloc[-1]
    
    # Calculate stressed PD based on macro variables
    pd_model = PDModel()
    
    # For each segment, apply stressed PD/LGD
    stressed_portfolio = portfolio.exposures.copy()
    
    # Estimate PD impact
    if 'unemployment_rate' in latest:
        unemployment_impact = (latest['unemployment_rate'] - df_macro.iloc[-1]['unemployment_rate']) / 2.0
        pd_multiplier = 1 + unemployment_impact * 0.3  # 30% PD increase per 2pp unemployment
    else:
        pd_multiplier = 1.0
    
    # Estimate LGD impact (from housing price changes)
    if 'housing_price_growth' in latest:
        housing_impact = (latest['housing_price_growth'] - df_macro.iloc[-1].get('housing_price_growth', 0)) / 10
        lgd_multiplier = 1 - housing_impact * 0.1  # 10% LGD increase per 10% house price fall
        lgd_multiplier = np.clip(lgd_multiplier, 0.8, 1.5)
    else:
        lgd_multiplier = 1.0
    
    # EAD impact (credit growth slowdown)
    ead_multiplier = 1.05  # Assume 5% increase in utilization under stress
    
    # Apply to portfolio
    stressed_results = portfolio.stress_portfolio(
        pd_shock=pd_multiplier,
        lgd_shock=lgd_multiplier,
        ead_shock=ead_multiplier
    )
    
    return stressed_results, df_stressed


def compare_scenarios(portfolio, scenarios, df_macro):
    """
    Compare multiple scenarios side by side
    
    Returns: DataFrame with comparison metrics
    """
    results = []
    
    # Baseline
    portfolio.calculate_ecl()
    portfolio.calculate_rwa()
    capital_base = portfolio.calculate_capital()
    
    results.append({
        'Scenario': 'Baseline',
        'Total ECL': portfolio.exposures['ecl_12m'].sum(),
        'Total RWA': portfolio.exposures['rwa'].sum(),
        'CET1 Required': capital_base['cet1_required'],
        'ECL Change (%)': 0,
        'RWA Change (%)': 0
    })
    
    # Stressed scenarios
    for scenario in scenarios:
        stressed, _ = apply_scenario_to_portfolio(portfolio, scenario, df_macro)
        
        ecl_stressed = stressed['ecl_stressed'].sum()
        rwa_stressed = stressed['rwa_stressed'].sum()
        capital_stressed = rwa_stressed * 0.105
        
        results.append({
            'Scenario': scenario.name,
            'Total ECL': ecl_stressed,
            'Total RWA': rwa_stressed,
            'CET1 Required': capital_stressed,
            'ECL Change (%)': (ecl_stressed / portfolio.exposures['ecl_12m'].sum() - 1) * 100,
            'RWA Change (%)': (rwa_stressed / portfolio.exposures['rwa'].sum() - 1) * 100
        })
    
    return pd.DataFrame(results)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("STRESS TESTING SCENARIOS")
    print("="*70)
    
    # Create sample macro data
    dates = pd.date_range('2024-01-01', '2026-12-31', freq='MS')
    df_macro = pd.DataFrame({
        'cash_rate': 4.5,
        'unemployment_rate': 4.0,
        'housing_price_growth': 5.0,
        'credit_growth_housing': 8.0,
        'bbsw_spread': 0.5
    }, index=dates)
    
    # Define scenarios
    tightening = TighteningScenario()
    soft_landing = SoftLandingScenario()
    funding_shock = FundingShockScenario()
    severe = SevereRecessionScenario()
    
    scenarios = [tightening, soft_landing, funding_shock, severe]
    
    print("\n" + "-"*70)
    print("SCENARIO DEFINITIONS")
    print("-"*70)
    
    for scenario in scenarios:
        print(f"\n{scenario.name}:")
        print(f"  {scenario.description}")
        df_stressed = scenario.apply(df_macro)
        print(f"  Unemployment: {df_macro.iloc[-1]['unemployment_rate']:.1f}% → {df_stressed.iloc[-1]['unemployment_rate']:.1f}%")
        print(f"  Cash Rate: {df_macro.iloc[-1]['cash_rate']:.2f}% → {df_stressed.iloc[-1]['cash_rate']:.2f}%")
        if 'housing_price_growth' in df_stressed.columns:
            print(f"  Housing Growth: {df_macro.iloc[-1]['housing_price_growth']:.1f}% → {df_stressed.iloc[-1]['housing_price_growth']:.1f}%")
    
    print("\n" + "="*70)
    print("Run with portfolio data to see full stress impact on ECL and RWA")
    print("="*70)
