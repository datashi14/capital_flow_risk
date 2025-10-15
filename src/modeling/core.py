"""
Core Credit Risk Modeling Module
Implements CAI (Credit Availability Index), PD/LGD/EAD models, and ECL calculations
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from scipy.stats import norm
import warnings
warnings.filterwarnings('ignore')


class CreditAvailabilityIndex:
    """
    Credit Availability Index (CAI)
    Measures ease of credit access based on macro factors
    
    CAI = weighted combination of:
    - Interest rate spread (negative weight)
    - Credit growth (positive weight)
    - Unemployment (negative weight)
    - GDP growth (positive weight)
    """
    
    def __init__(self, weights=None):
        if weights is None:
            self.weights = {
                'rate': -0.3,
                'credit_growth': 0.4,
                'unemployment': -0.2,
                'gdp_growth': 0.1
            }
        else:
            self.weights = weights
    
    def calculate(self, df, rate_col='cash_rate', credit_col='credit_growth_housing',
                  unemp_col='unemployment_rate', gdp_col='gdp_growth'):
        """
        Calculate CAI from macro dataframe
        Returns: Series with CAI values (0-100 scale)
        """
        # Normalize each component to z-scores
        rate_z = (df[rate_col] - df[rate_col].mean()) / df[rate_col].std()
        credit_z = (df[credit_col] - df[credit_col].mean()) / df[credit_col].std()
        unemp_z = (df[unemp_col] - df[unemp_col].mean()) / df[unemp_col].std()
        gdp_z = (df[gdp_col] - df[gdp_col].mean()) / df[gdp_col].std()
        
        # Weighted combination
        cai_raw = (
            self.weights['rate'] * rate_z +
            self.weights['credit_growth'] * credit_z +
            self.weights['unemployment'] * unemp_z +
            self.weights['gdp_growth'] * gdp_z
        )
        
        # Scale to 0-100 (50 = neutral)
        cai = 50 + 10 * cai_raw
        cai = cai.clip(0, 100)
        
        return cai


class PDModel:
    """
    Probability of Default (PD) Model
    
    Uses Merton-style approach with macro adjustments:
    PD = Φ(-DD) × macro_adjustment
    
    Where:
    - DD = Distance to Default = (Asset Value - Debt) / (Asset Volatility × sqrt(T))
    - macro_adjustment based on unemployment, rates, GDP
    """
    
    def __init__(self, base_pd=0.015):
        """
        base_pd: Through-the-cycle baseline default rate (e.g., 1.5%)
        """
        self.base_pd = base_pd
        self.coefficients = None
    
    def calculate_simple(self, df, unemp_col='unemployment_rate', 
                        rate_col='cash_rate', gdp_col='gdp_growth'):
        """
        Simple PD model: PD = f(unemployment, rates, GDP)
        
        PD = base_pd × exp(β1×unemployment + β2×rates + β3×GDP)
        """
        # Normalize features
        unemp_norm = (df[unemp_col] - 5.0) / 2.0  # Center at 5%, scale by 2pp
        rate_norm = (df[rate_col] - 2.5) / 2.0    # Center at 2.5%, scale by 2pp
        gdp_norm = (df[gdp_col] - 2.0) / 2.0      # Center at 2%, scale by 2pp
        
        # Coefficients (calibrated to typical credit cycles)
        beta_unemp = 0.4   # 1pp unemployment increase → 40% PD increase
        beta_rate = 0.2    # 1pp rate increase → 20% PD increase
        beta_gdp = -0.15   # 1pp GDP growth → 15% PD decrease
        
        # Log-linear model
        log_pd_adj = (
            beta_unemp * unemp_norm +
            beta_rate * rate_norm +
            beta_gdp * gdp_norm
        )
        
        pd = self.base_pd * np.exp(log_pd_adj)
        
        # Cap at reasonable bounds (0.1% to 15%)
        pd = pd.clip(0.001, 0.15)
        
        return pd
    
    def calculate_merton(self, asset_value, debt_value, volatility=0.3, time_horizon=1):
        """
        Merton model: structural default probability
        
        PD = Φ(-DD) where DD = (ln(V/D) + (μ - 0.5σ²)T) / (σ√T)
        
        Simplified: assume μ = 0 (risk-neutral)
        DD = (ln(V/D) - 0.5σ²T) / (σ√T)
        """
        leverage = asset_value / debt_value
        
        # Distance to default
        dd = (np.log(leverage) - 0.5 * volatility**2 * time_horizon) / \
             (volatility * np.sqrt(time_horizon))
        
        # PD = Φ(-DD)
        pd = norm.cdf(-dd)
        
        return pd
    
    def calibrate(self, X, y):
        """
        Calibrate PD model using logistic regression
        X: DataFrame with macro features
        y: Binary default indicator (1 = default, 0 = no default)
        """
        model = LogisticRegression()
        model.fit(X, y)
        self.coefficients = model.coef_
        return model


class LGDModel:
    """
    Loss Given Default (LGD) Model
    
    LGD depends on:
    - Collateral value (housing prices for mortgages)
    - Recovery costs
    - Seniority
    """
    
    def __init__(self, base_lgd=0.45):
        """
        base_lgd: Baseline LGD (e.g., 45% for unsecured)
        """
        self.base_lgd = base_lgd
    
    def calculate_secured(self, ltv_ratio, recovery_rate=0.8):
        """
        LGD for secured lending (e.g., mortgages)
        
        LGD = max(0, LTV / recovery_rate - 1)
        
        If LTV = 80%, recovery = 80%, then LGD = max(0, 0.8/0.8 - 1) = 0
        If LTV = 90%, recovery = 80%, then LGD = max(0, 0.9/0.8 - 1) = 12.5%
        """
        lgd = np.maximum(0, ltv_ratio / recovery_rate - 1)
        lgd = lgd.clip(0, 1)
        return lgd
    
    def calculate_downturn(self, base_lgd, housing_price_change):
        """
        Downturn LGD adjusts for falling collateral values
        
        LGD_downturn = base_LGD / (1 + housing_price_change)
        
        If housing falls 20%, LGD increases by 25%
        """
        adjustment = 1.0 / (1.0 + housing_price_change / 100)
        lgd_dt = base_lgd * adjustment
        lgd_dt = lgd_dt.clip(0, 1)
        return lgd_dt
    
    def calculate_simple(self, df, collateral_type='housing', 
                        price_col='housing_price_growth'):
        """
        Simple LGD model varying with collateral values
        """
        if collateral_type == 'housing':
            # Base LGD = 20% (well-secured mortgages)
            # Increases when housing prices fall
            lgd = 0.20 * (1.0 - df[price_col] / 100 * 0.5)
            lgd = lgd.clip(0.05, 0.60)
        else:
            # Unsecured lending: higher base LGD
            lgd = pd.Series(self.base_lgd, index=df.index)
        
        return lgd


class EADModel:
    """
    Exposure at Default (EAD) Model
    
    EAD = drawn_amount + CCF × undrawn_commitment
    
    Where CCF = Credit Conversion Factor (typically 50-75% for unfunded lines)
    """
    
    def __init__(self, ccf=0.75):
        """
        ccf: Credit Conversion Factor
        """
        self.ccf = ccf
    
    def calculate(self, drawn_amount, commitment, usage_rate=None):
        """
        Calculate EAD given drawn and committed amounts
        
        If usage_rate is provided, use it instead of assuming full drawdown
        """
        undrawn = commitment - drawn_amount
        
        if usage_rate is not None:
            # Stressed usage rate (how much of undrawn will be drawn at default)
            ead = drawn_amount + usage_rate * undrawn
        else:
            # Regulatory CCF
            ead = drawn_amount + self.ccf * undrawn
        
        return ead
    
    def calculate_stressed(self, drawn_amount, commitment, stress_factor=1.5):
        """
        Stressed EAD: assume higher utilization in stress
        """
        ccf_stressed = min(1.0, self.ccf * stress_factor)
        undrawn = commitment - drawn_amount
        ead_stressed = drawn_amount + ccf_stressed * undrawn
        
        return ead_stressed


class ECLCalculator:
    """
    Expected Credit Loss (ECL) Calculator
    
    ECL = PD × LGD × EAD
    
    12-month ECL vs. Lifetime ECL:
    - Stage 1: 12-month ECL
    - Stage 2/3: Lifetime ECL
    """
    
    def __init__(self):
        self.pd_model = PDModel()
        self.lgd_model = LGDModel()
        self.ead_model = EADModel()
    
    def calculate_12m_ecl(self, pd_12m, lgd, ead):
        """
        12-month ECL for Stage 1 assets
        """
        ecl = pd_12m * lgd * ead
        return ecl
    
    def calculate_lifetime_ecl(self, pd_lifetime, lgd, ead, maturity=5):
        """
        Lifetime ECL for Stage 2/3 assets
        
        Simple approach: sum discounted expected losses
        ECL = Σ PD_t × LGD_t × EAD_t × DF_t
        """
        discount_rate = 0.05  # 5% discount rate
        
        ecl = 0
        for t in range(1, maturity + 1):
            # Marginal PD in year t (simplified: uniform over life)
            pd_t = pd_lifetime / maturity
            
            # Discount factor
            df_t = 1 / (1 + discount_rate) ** t
            
            # Add to lifetime ECL
            ecl += pd_t * lgd * ead * df_t
        
        return ecl
    
    def calculate_portfolio_ecl(self, df, exposure, stage=1):
        """
        Calculate ECL for entire portfolio
        
        df: DataFrame with PD, LGD estimates
        exposure: Series or array with EAD for each loan
        stage: 1 (12-month) or 2/3 (lifetime)
        """
        if stage == 1:
            ecl = df['pd'] * df['lgd'] * exposure
        else:
            ecl = self.calculate_lifetime_ecl(df['pd'], df['lgd'], exposure)
        
        return ecl
    
    def stage_classification(self, current_pd, origination_pd, dpd=0):
        """
        Classify loans into IFRS 9 stages
        
        Stage 1: No significant increase in credit risk (SICR)
        Stage 2: SICR but not credit-impaired
        Stage 3: Credit-impaired (>90 DPD or other evidence)
        
        Simple rule:
        - Stage 3 if DPD > 90
        - Stage 2 if PD doubled since origination
        - Stage 1 otherwise
        """
        if dpd > 90:
            return 3
        elif current_pd > 2 * origination_pd:
            return 2
        else:
            return 1


def calculate_rwa_simple(ead, pd, lgd, correlation=0.15):
    """
    Simplified Risk-Weighted Assets (RWA) calculation
    Based on Basel IRB formula (simplified)
    
    RWA = EAD × RW × 12.5
    
    Where RW (risk weight) depends on PD, LGD, and asset correlation
    
    Correlation = 0.15 for retail, 0.12-0.24 for corporate
    """
    # Vasicek formula for capital requirement (K)
    # K = LGD × Φ(sqrt(1/(1-R)) × Φ⁻¹(PD) + sqrt(R/(1-R)) × Φ⁻¹(0.999)) - PD × LGD
    
    pd = np.clip(pd, 0.0001, 0.9999)  # Avoid numerical issues
    
    phi_inv_pd = norm.ppf(pd)
    phi_inv_999 = norm.ppf(0.999)
    
    sqrt_r = np.sqrt(correlation)
    sqrt_1_r = np.sqrt(1 - correlation)
    
    k = lgd * norm.cdf(
        sqrt_1_r * phi_inv_pd + sqrt_r * phi_inv_999
    ) - pd * lgd
    
    # Maturity adjustment (simplified: M = 2.5 years)
    # b = (0.11852 - 0.05478 × ln(PD))²
    b = (0.11852 - 0.05478 * np.log(pd)) ** 2
    maturity_adj = (1 + (2.5 - 2.5) * b) / (1 - 1.5 * b)
    
    k_adj = k * maturity_adj
    
    # RWA = EAD × K × 12.5
    rwa = ead * k_adj * 12.5
    
    return rwa


def calculate_capital_requirement(rwa, cet1_ratio=0.105):
    """
    Calculate minimum capital requirement
    
    Basel III minimum CET1 = 4.5%
    + Capital conservation buffer = 2.5%
    + Countercyclical buffer = 0-2.5%
    + D-SIB buffer = 0-3.5%
    
    Total = ~10.5% for typical large bank
    """
    capital_req = rwa * cet1_ratio
    return capital_req


if __name__ == "__main__":
    # Example usage
    print("=== Credit Risk Modeling Examples ===\n")
    
    # 1. CAI Calculation
    print("1. Credit Availability Index (CAI)")
    dates = pd.date_range('2020-01-01', '2024-12-31', freq='MS')
    df_test = pd.DataFrame({
        'cash_rate': np.random.uniform(1, 5, len(dates)),
        'credit_growth_housing': np.random.uniform(-5, 15, len(dates)),
        'unemployment_rate': np.random.uniform(4, 7, len(dates)),
        'gdp_growth': np.random.uniform(-1, 3, len(dates))
    }, index=dates)
    
    cai_model = CreditAvailabilityIndex()
    df_test['cai'] = cai_model.calculate(df_test)
    print(f"CAI range: {df_test['cai'].min():.1f} to {df_test['cai'].max():.1f}")
    print(f"Mean CAI: {df_test['cai'].mean():.1f}\n")
    
    # 2. PD Calculation
    print("2. Probability of Default (PD)")
    pd_model = PDModel(base_pd=0.02)
    df_test['pd'] = pd_model.calculate_simple(df_test)
    print(f"PD range: {df_test['pd'].min():.2%} to {df_test['pd'].max():.2%}")
    print(f"Mean PD: {df_test['pd'].mean():.2%}\n")
    
    # 3. LGD Calculation
    print("3. Loss Given Default (LGD)")
    lgd_model = LGDModel()
    df_test['housing_price_growth'] = np.random.uniform(-5, 10, len(dates))
    df_test['lgd'] = lgd_model.calculate_simple(df_test, collateral_type='housing')
    print(f"LGD range: {df_test['lgd'].min():.2%} to {df_test['lgd'].max():.2%}")
    print(f"Mean LGD: {df_test['lgd'].mean():.2%}\n")
    
    # 4. ECL Calculation
    print("4. Expected Credit Loss (ECL)")
    ecl_calc = ECLCalculator()
    ead = 100000  # $100k exposure
    ecl = ecl_calc.calculate_12m_ecl(df_test['pd'], df_test['lgd'], ead)
    print(f"12-month ECL range: ${ecl.min():.0f} to ${ecl.max():.0f}")
    print(f"Mean 12-month ECL: ${ecl.mean():.0f}\n")
    
    # 5. RWA Calculation
    print("5. Risk-Weighted Assets (RWA)")
    rwa = calculate_rwa_simple(ead, df_test['pd'].iloc[-1], df_test['lgd'].iloc[-1])
    capital_req = calculate_capital_requirement(rwa)
    print(f"EAD: ${ead:,.0f}")
    print(f"RWA: ${rwa:,.0f}")
    print(f"Capital Requirement (10.5%): ${capital_req:,.0f}")
